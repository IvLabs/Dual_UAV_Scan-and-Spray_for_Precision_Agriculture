import time
import cv2
import numpy as np
import threading
from multiprocessing import Process, Event, Lock
from multiprocessing.shared_memory import SharedMemory
import Telemetry_communication_agri as comm
from typing import List
from typing import List, Dict
from pyproj import Geod
from dronekit import connect, VehicleMode, LocationGlobalRelative
from sprayingFinalFunctions import *
_Geod = Geod(ellps="WGS84")

class SPRAYMISSION:
    def __init__(self, **cfg):
        DEFAULTS = {
            "CONNECTION_STRING"  : "10.87.53.100:14550",
            "WPNAV_SPEED"        : 1500,        # in cm/s
            "ALTITUDE"           : 4,
            "COUNT_SPRAY_POINT"  : 3,
            "THRESHOLD_METERS"   : 1.0,
            "REACH_BREAK"        : 1,           # in m
            "HOVER_SECONDS"      : 15,
            "THREAD_SLEEP"       : 10,
            "TELEMETRY_PORT"     : "/dev/ttyUSB0",
            "TELEMETRY_BAUD"     : 57600,
            "RTSP_URL"           : "rtsp://192.168.144.25:8554/main.264",
            "TOL_PX"             : 50,      # pixels
            "K_P"                : 0.0005       # velocity gain
        }
        self.cfg = DEFAULTS.copy()
        self.cfg.update(cfg)
        self.rc_rtl_triggered = False
        self.SHOW_LIVE = False
        self.abort_reason = None
        self.m_state = {"drop_location": [], "scan_finished": False}
        self.finished_check = False
        self.telemetry_stop_event = threading.Event()
        self.telemetry_thread = None
        self.dropped: List[Dict] = []
        self.vehicle= None

    def haversine_m(self, lat1, lon1, lat2, lon2):
        """Calculate the great-circle distance between two points on the Earth surface."""
        az12, az21, dist = _Geod.inv(lon1, lat1, lon2, lat2)
        return dist

    def mode_callback(self, vehicle, attr_name, value):
        if value.name == "RTL":
            print("[INFO] RTL detected via RC")
            self.rc_rtl_triggered = True
            self.abort_reason = "RTL triggered by RC"
        print(f"[DEBUG] Mode changed to {value.name}")

    def centering(self):
        frame = None
        while frame is None:
            print("[Centring] Grabbing frame")
            with self.lock:
                frame = self.shared_frame.copy()
            reached, ann = reach_center(self.vehicle, frame)
        while not reached:
            print("[Centring] Frame grabbed, centering...")
            with self.lock:
                frame = self.shared_frame.copy()
            cv2.imshow("Hmm", ann)
            cv2.waitKey(1)
            print(frame.shape)
            time.sleep(0.1)
            reached, ann = reach_center(self.vehicle, frame)
        print("Reached center")
        time.sleep(10)

        pos = self.vehicle.location.global_relative_frame
        self.vehicle.simple_goto(LocationGlobalRelative(pos.lat, pos.lon, self.cfg["ALTITUDE"]))
        while abs(self.vehicle.location.global_relative_frame.alt - self.cfg["ALTITUDE"]) > 0.2:
        time.sleep(0.2)

        # Hover for drop
        print(f"[INFO] Hovering for {self.cfg['HOVER_SECONDS']} seconds for SPRAYING")
        waiting_time = time.time()
        while(time.time() - waiting_time < self.cfg['HOVER_SECONDS']):
            if self.rc_rtl_triggered:
                time.sleep(0.2)
                print("[ABORT] RC RTL detected → shutting down")
                return

    def deviate_to_spray(self, drop_point):
        if self.rc_rtl_triggered:
            print("[ABORT] RC RTL detected → shutting down")
            return
        # Switch to GUIDED mode for deviation
        print("[INFO] Switching to GUIDED mode for deviation")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.parameters['WPNAV_SPEED'] = self.cfg["WPNAV_SPEED"]
        print("[INFO] WPNAV_SPEED now =", self.vehicle.parameters['WPNAV_SPEED'],"cm/s")
        time.sleep(1)
        
        drop_location = LocationGlobalRelative(
            drop_point["lat"], 
            drop_point["lon"], 
            self.cfg["ALTITUDE"]
        )
        self.vehicle.simple_goto(drop_location, groundspeed = self.cfg["WPNAV_SPEED"])
        
        # Wait until at drop location
        print("[INFO] Flying to SPRAY location...")
        while True:
            pos = self.vehicle.location.global_frame
            if pos and pos.lat is not None:
                dist = self.haversine_m(pos.lat, pos.lon, drop_point["lat"], drop_point["lon"])
                if dist <= self.cfg["REACH_BREAK"]:  # Within 1 meter
                    print("[INFO] Arrived at 1m away from SPRAY location")
                    time.sleep(2) # Stabilize before drop
                    break
            time.sleep(0.5)
        
        self.centering()
        
        
        print("[INFO] SPRAYING Completed")
        time.sleep(2)

    def check_for_new_spray_point(self):
        """Check for new point in the receiver"""
        if self.m_state["scan_finished"] and len(self.m_state["drop_location"]) == 0:
            self.finished_check = True
            print("[DEBUG] Finished check is now TRUE")
        if not self.m_state["drop_location"]:
            return
        drop_point = self.m_state["drop_location"].pop(0)
        print()
        print(f"[INFO] SPRAY point detected at {drop_point['lat']},{drop_point['lon']}")
        # Record drop
        self.dropped.append({
            "lat": drop_point["lat"], 
            "lon": drop_point["lon"],
            "alt": drop_point.get("alt"), 
            "time": time.time()
        })
        self.deviate_to_spray(drop_point)
        print(f"[INFO] Location of SPRAYED point is recorded")
        print()
    
    def telemetry_worker(self, radio_link):
        """
        Runs continuously in background to listen telemetry data
        """
        print("[THREAD] Telemetry listen started")
        while not self.telemetry_stop_event.is_set():
            try:
                comm.listen_telemetry(radio_link, self.m_state)
                print("[THREAD] Number of incoming SPRAY points found:", len(self.m_state["drop_location"]))
                time.sleep(self.cfg["THREAD_SLEEP"])
                if self.rc_rtl_triggered:
                    time.sleep(0.2)
                    print("[ABORT] RC RTL detected → shutting down")
                    return
            except Exception as e:
                print("[WARN][Telemetry Thread]", e)
            time.sleep(0.05)  #small sleep to avoid CPU hog
        print("[THREAD] Telemetry listener stopped")

    def connect_vehicle(self):
        print("[INFO] Connecting to vehicle...")
        try:
            self.vehicle = connect(
                self.cfg["CONNECTION_STRING"],
                wait_ready=True,
                heartbeat_timeout=120
            )
            print("[DEBUG] Connect() returned vehicle object")
        except Exception as e:
            print("[ERROR] Connect() failed:", e)
            raise
        print("[DEBUG] Waiting for heartbeat...")
        try:
            self.vehicle.wait_ready(timeout=60)
            print("[DEBUG] Vehicle ready, heartbeat OK")
        except Exception as e:
            print("[ERROR] Wait_ready() failed:", e)
            raise
        return self.vehicle

    def arm_and_takeoff(self, target_alt: float):
        if self.vehicle is None:
            raise RuntimeError("Vehicle not connected")
        print("[INFO] Arming and taking off...")
        while not self.vehicle.is_armable:
            time.sleep(0.5)
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        while not self.vehicle.armed:
            time.sleep(0.5)
        self.vehicle.simple_takeoff(target_alt)
        while True:
            if self.vehicle.location.global_relative_frame.alt >= target_alt * 0.9:
                break
            time.sleep(0.5)
        print("[INFO] Takeoff complete")

    def finalize_mission(self) -> None:
        try:
            if self.vehicle:
                self.vehicle.parameters['RTL_ALT'] = self.cfg["ALTITUDE"]
                self.vehicle.mode = VehicleMode("RTL")
        except Exception:
            pass
        time.sleep(2)
        if self.vehicle:
            try:
                self.vehicle.close()
            except Exception:
                pass
        print("[INFO] Mission finished and vehicle closed.")
        import sys
        sys.exit(0)

    def run(self):
        try:
            viewer_stop = Event()
            shape = (720, 1280,3)
            dtype = np.uint8
            shm = SharedMemory(create=True, size=np.prod(shape) * np.dtype(dtype).itemsize)
            self.shared_frame = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
            stop_event = Event()

            self.lock = Lock()
            p = Process(target=frame_grabber_process, args=(self.cfg["RTSP_URL"], shm.name, shape, dtype, stop_event, self.lock), daemon=True)
            p.start()

            if self.SHOW_LIVE:
                viewer = threading.Thread(target=live_viewer_thread, args=(self.shared_frame, self.lock, viewer_stop), daemon=True)
                viewer.start()
            radio_link = comm.start_radio(self.cfg["TELEMETRY_PORT"], self.cfg["TELEMETRY_BAUD"])
            self.telemetry_thread = threading.Thread(
                target=self.telemetry_worker,
                args=(radio_link,),
                daemon=True
            )
            self.telemetry_thread.start()
            self.connect_vehicle()
            self.vehicle.add_attribute_listener('mode', self.mode_callback)
            print("Current Mode",self.vehicle.mode.name)

            print("[INFO] Waiting for pilot to ARM the vehicle...")
            while not self.vehicle.armed:
                print("  - Vehicle not armed. Awaiting RC switch...")
                time.sleep(1)
            print("[INFO] Vehicle armed by pilot!")

            while True:
                if len(self.m_state["drop_location"]) >= self.cfg["COUNT_SPRAY_POINT"]:
                    self.arm_and_takeoff(self.cfg["ALTITUDE"])
                    break
            
            while not self.finished_check:
                try:
                    self.check_for_new_spray_point()
                    print("[INFO] WAITING for more SPRAY point to come")
                    if self.rc_rtl_triggered:
                        time.sleep(0.2)
                        print("[ABORT] RC RTL detected → shutting down")
                        return
                    time.sleep(1.0)
                except Exception as e:
                    print(f"[WARN] Error in mission loop: {e}")
                    import traceback
                    traceback.print_exc()
                    self.vehicle.mode = VehicleMode("RTL")
                    time.sleep(1.0)

        except KeyboardInterrupt:
            print("\nMission interrupted by user")
            self.vehicle.parameters['RTL_ALT'] = self.cfg["ALTITUDE"]
            self.vehicle.mode = VehicleMode("RTL")
        except Exception as e:
            print(f"Mission error: {e}")
            import traceback
            traceback.print_exc()
            self.vehicle.mode = VehicleMode("RTL")
        finally:
            try:
                print("[INFO] Finalizing mission data...")
                self.finalize_mission()
            except Exception as e:
                print("[WARN] Finalize_mission raised:", e)

if __name__ == "__main__":
    print("="*60)
    print("SPRAY MISSION FOR ARAVAT DRONE")
    print("="*60)
    mission = SPRAYMISSION()
    mission.run()
