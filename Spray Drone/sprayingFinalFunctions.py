
import time
import cv2
import numpy as np
from multiprocessing.shared_memory import SharedMemory
import time
from pymavlink import mavutil
from pyproj import Geod

_geod = Geod(ellps="WGS84")
TOL_PX = 50
K_P = 0.0005
K_ALT = 0.1
SPRAY_ALT = 3
#lower_yellow=(20, 90,  120)
#upper_yellow=(35, 160, 250)
#lower_yellow=(20, 100,  120)
#upper_yellow=(35, 250, 250)
#lower_yellow = (0, 0, 0)
#upper_yellow = (180, 255, 50)

lower_yellow=(20, 30,  225)
upper_yellow=(30, 150, 255)
min_area = 100

def clamp(x, m):
    return max(-m, min(m, x))

def send_body_velocity(vehicle, vx, vy, vz):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_BODY_NED,
        0b010111000111,
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, 0)
    vehicle.send_mavlink(msg)

def gps_distance(lat1, lon1, lat2, lon2):
    _, _, dist = _geod.inv(lon1, lat1, lon2, lat2)
    return dist

def read_points(fname):
    pts = []
    with open(fname) as f:
        for l in f:
            if l.strip():
                lat, lon = map(float, l.split(",")[:2])
                pts.append((lat, lon))
    return pts

def detect_yellow_in_image(img, lower_yellow, upper_yellow, min_area):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    annotated = img.copy()
    centers = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        cx = x + w // 2
        cy = y + h // 2
        centers.append((cx, cy))
        cv2.rectangle(annotated, (x, y), (x+w, y+h), (0,0,255), 2)
        cv2.drawMarker(annotated, (cx, cy), (0,255,0), markerType=cv2.MARKER_CROSS, markerSize=12, thickness=2)
    return annotated, centers

def reach_center(vehicle, latest_frame):
    h, w = latest_frame.shape[:2]
    ann, centers = detect_yellow_in_image(latest_frame, lower_yellow, upper_yellow, min_area)
    if centers:
        for cx, cy in centers[:1]:
            ex, ey = cx - w // 2, h // 2 - cy
            ez = vehicle.location.global_relative_frame.alt - SPRAY_ALT
            if abs(ex) < TOL_PX and abs(ey) < TOL_PX:
                send_body_velocity(vehicle, 0, 0, 0)
                return True, ann
            vx, vy, vz = -K_P * ey, -K_P * ex, K_ALT * ez
            vx = clamp(vx, 0.5)
            vy = clamp(vy, 0.5)
            vz = clamp(vz, 0.5)
            send_body_velocity(vehicle, vx, vy, vz)
            return False, ann
    else:
        send_body_velocity(vehicle, 0, 0, 0)
        return False, ann

def connect_to_camera(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        print("Error: Cannot connect to the camera.")
        exit()
    print("Connected to the camera. Press 'q' to quit.")
    return cap

def frame_grabber_process(url, shm_name, shape, dtype, stop_event, lock):
    cap = connect_to_camera(url)
    shm = SharedMemory(name=shm_name)
    frame_buf = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            cap.release()
            cap = connect_to_camera(url)
            continue
        with lock:
            np.copyto(frame_buf, frame)
    cap.release()
    shm.close()

def live_viewer_thread(shared_frame, lock, stop_event):
    while not stop_event.is_set():
        with lock:
            frame = shared_frame.copy()
        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break
    cv2.destroyAllWindows()
