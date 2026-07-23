import cv2
import numpy as np
from pixel2gps import *
import threading
import dronekit
import time
from pyproj import Geod
from datetime import datetime
from filelock import FileLock
ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

_geod = Geod(ellps="WGS84")

def gps_distance(lat1, lon1, lat2, lon2):
    _, _, dist = _geod.inv(lon1, lat1, lon2, lat2)
    return dist  # meters

min_area = 200
margin = 0   # 15% border

latest_frame = None
last_frame_time = 0.0
grabber_running = True
frame_lock = threading.Lock()

lower_yellow1 = (18, 10, 225)
upper_yellow1 = (40, 60, 255)

lower_yellow2 = (18, 50,  200)
upper_yellow2 = (35, 150, 255)

min_area = 10

VIDEO_PATH = f"/home/jetsonboii/nidar/yellowframes/{ts}.mp4"
VIDEO_FPS = 10
VIDEO_CODEC = "mp4v"
THRESH_M = 1
GIMBAL_OFFSET_X  = 0.16
GIMBAL_OFFSET_Y  = 0.035
GIMBAL_OFFSET_Z  = 0.225
GIMBAL_PITCH     = -90
GIMBAL_YAW       = 0
#DRONE_CONNECTION = "/dev/ttyACM0"
DRONE_CONNECTION = "udp:127.0.0.1:14551"
BAUDRATE = 115200
SAVE_LOCATION = "/home/jetsonboii/nidar/yellowframes"
GPS_LOG_PATH = f"{SAVE_LOCATION}/{ts}_detections.txt"

lock = FileLock("Dropping.txt.lock")

rtsp_url = "rtsp://192.168.144.25:8554/main.264"

def is_new(lat, lon, saved, thresh_m):
    for slat, slon in saved:
        if gps_distance(lat, lon, slat, slon) < thresh_m:
            return False
    return True

def frame_grabber_thread(url):
    global latest_frame, last_frame_time, grabber_running
    cap = connect_to_camera(url)
    while grabber_running:
        ret, frame = cap.read()
        if not ret:
            print("RTSP read failed, reconnecting...")
            time.sleep(1)
            cap.release()
            cap = connect_to_camera(url)
            continue
        with frame_lock:
            latest_frame = frame
            last_frame_time = time.time()
    cap.release()

def detect_yellow_in_image(img,
                           min_area = min_area):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, lower_yellow1, upper_yellow1)
    mask2 = cv2.inRange(hsv, lower_yellow2, upper_yellow2)

    mask = cv2.bitwise_or(mask1, mask2)

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
        cv2.drawMarker(annotated, (cx, cy), (0,255,0),
                       markerType=cv2.MARKER_CROSS, markerSize=12, thickness=2)
        # print(area)
    return annotated, centers

def connect_to_camera(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cv2.CAP_PROP_FPS
    if not cap.isOpened():
        print("Error: Cannot connect to the camera.")
        exit()
    print("Connected to the camera. Press 'q' to quit.")
    return cap

def record(master, rtsp_url=rtsp_url):
    global grabber_running
    video_writer = None
    saved = []
    threading.Thread(target=frame_grabber_thread, args=(rtsp_url,), daemon=True).start()
    while True:
        with frame_lock:
            frame = None if latest_frame is None else latest_frame.copy()
        if frame is not None:
            att = master.attitude
            pos = master.location.global_relative_frame
            # print(att, pos)
            H, W = frame.shape[:2]
            xmin = int(W * margin)
            xmax = int(W * (1 - margin))
            ymin = int(H * margin)
            ymax = int(H * (1 - margin))
            annotated, centers = detect_yellow_in_image(frame)
            if video_writer is None:
                h, w = frame.shape[:2]
                video_writer = cv2.VideoWriter(VIDEO_PATH, cv2.VideoWriter_fourcc(*VIDEO_CODEC), VIDEO_FPS, (w, h))

            if centers:
                for center in centers[:1]:
                    cx, cy = center
                    if not (xmin <= cx <= xmax and ymin <= cy <= ymax):
                        continue
                    drone_H = pos.alt
                    drone_roll = att.roll; drone_pitch = att.pitch; drone_yaw = att.yaw
                    x, y = pixel2meter(center[0], center[1], drone_H, drone_roll, drone_pitch, drone_yaw, K, dist, GIMBAL_OFFSET_Z, GIMBAL_PITCH, GIMBAL_YAW)
                    gps_det = offset_to_gps(pos.lat, pos.lon, x, y, GIMBAL_OFFSET_X, GIMBAL_OFFSET_Y)
                    if is_new(gps_det[0], gps_det[1], saved, THRESH_M):
                        print("Detected, Saved :", gps_det)
                        saved.append(gps_det)
                    gps_str = f"{gps_det[0]}_{gps_det[1]}.png"
                    cv2.putText(annotated, gps_str, (center[0], center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    cv2.imshow("YellowImage", annotated)
                    video_writer.write(annotated)
                    with lock:
                        with open("Dropping.txt", "a") as f:
                            f.write(str(gps_det[0]) + ","+ str(gps_det[1]) + ","+str(drone_H) + "\n")

            else:
                cv2.imshow("YellowImage", frame)
                video_writer.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    grabber_running = False
    cv2.destroyAllWindows()
    print(saved)

if __name__ == "__main__":
    master = dronekit.connect(DRONE_CONNECTION, wait_ready=True, baud=BAUDRATE)
    record(master)
