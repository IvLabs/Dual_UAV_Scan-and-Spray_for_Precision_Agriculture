# main.py
import time
import subprocess
from LawnMower import LawnmowerMission
from GimbalController import set_gimbal

def start_yellow_detection():
    """
    Starts yellow detection as a separate process.
    It writes GPS points to Dropping.txt
    """
    subprocess.Popen(["python3", "-m", "Yellow_detection"],cwd=".")

def main():
    print("===== NIDAR AUTONOMOUS SYSTEM START =====")
    
    # 1. Set the gimbal
    try:
        
        Yaw   = (0*10).to_bytes(2, byteorder='little', signed=True)
        Pit   = (-90*10).to_bytes(2, byteorder='little', signed=True)
        set_gimbal(Yaw, Pit)
        print("[MAIN] Gimbal set to nadir")
    except Exception as e:
        print("[WARN] Gimbal command failed:", e)
    
    
    # 2. Start yellow detection (NON-BLOCKING)
    start_yellow_detection()
    time.sleep(5)  # allow camera pipeline to stabilize

    # 3. Start lawnmower mission (BLOCKING)
    print("[MAIN] Starting lawnmower mission")
    mission = LawnmowerMission()
    mission.run()

if __name__ == "__main__":
    main()

