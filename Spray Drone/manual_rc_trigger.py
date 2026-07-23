from pymavlink import mavutil
from sprayingmaster import *
from time import sleep, time

PORT = "/dev/ttyAMA0"  
BAUD = 115200

PUMP_PIN = 17
SMALL_PIN = 27
LARGE_PIN = 22

PWM_LOW = 1200
PWM_HIGH = 1800

RC_TIMEOUT = 2

print("Initializing Spray System...")
Spray_Init(PUMP_PIN, SMALL_PIN, LARGE_PIN)
Pump_Off()

print("Connecting to Cube...")
master = mavutil.mavlink_connection(PORT, baud=BAUD)
master.wait_heartbeat()
print("Connected to vehicle")

master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
    0,
    mavutil.mavlink.MAVLINK_MSG_ID_RC_CHANNELS,
    100000,
    0, 0, 0, 0, 0
)

current_nozzle = "SMALL"
last_rc_time = time()

print("Listening for RC input...")

try:
    while True:
        msg = master.recv_match(
            type=['RC_CHANNELS', 'RC_CHANNELS_RAW'],
            blocking=True,
            timeout=1
        )

        # RC timeout failsafe
        if msg is None:
            if time() - last_rc_time > RC_TIMEOUT:
                Pump_Off()
            continue

        last_rc_time = time()

        ch5 = None
        ch7 = None

        if msg.get_type() == "RC_CHANNELS_RAW":
            ch5 = msg.chan5_raw
            ch7 = msg.chan7_raw
        elif msg.get_type() == "RC_CHANNELS":
            ch5 = msg.chan5
            ch7 = msg.chan7

        # Disarm safety
        if not master.motors_armed():
            Pump_Off()
            continue

        if ch7 is not None:
            if ch7 < PWM_LOW and current_nozzle != "SMALL":
                Select_Nozzle("SMALL")
                current_nozzle = "SMALL"

            elif ch7 > PWM_HIGH and current_nozzle != "LARGE":
                Select_Nozzle("LARGE")
                current_nozzle = "LARGE"

        if ch5 is not None:
            if ch5 > PWM_HIGH:
                Pump_On()
            elif ch5 < PWM_LOW:
                Pump_Off()

        print(f"CH5={ch5}  CH7={ch7}  Nozzle={current_nozzle}")
        sleep(0.05)

except KeyboardInterrupt:
    print("User exit")

except Exception as e:
    print(f"ERROR: {e}")

finally:
    print("Shutting down safely")
    Pump_Off()
    Clear_Spray()
    master.close()
