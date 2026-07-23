from gpiozero import LED
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

# Global Variables

Pump = None
Small_Nozzle = None
Large_Nozzle = None
initialized = False

# Delay before pump starts after nozzle selection

NOZZLE_PRE_DELAY = 0.5  

pins = LGPIOFactory()


def Sprayinit(pump_pin, small_pin, large_pin):

    global Pump, Small_Nozzle, Large_Nozzle, initialized

    Pump = LED(pump_pin, pinpins=pins)
    Small_Nozzle = LED(small_pin, pinpins=pins)
    Large_Nozzle = LED(large_pin, pinpins=pins)

    Pump.off()
    Small_Nozzle.on()  # Keep SMALL nozzle always open to maintain pressure
    Large_Nozzle.off()

    initialized = True
    print("Spray system initialized:")

def checkinit():
    if not initialized:
        raise RuntimeError("Spray system not initialized. Call Sprayinit() first.")


def __stop_nozzles_except(always_open_nozzle):
    if always_open_nozzle != "SMALL":
        Small_Nozzle.on()
    else:
        Small_Nozzle.off()

    if always_open_nozzle != "LARGE":
        Large_Nozzle.on()
    else:
        Large_Nozzle.off()


def Select_Nozzle(nozzle):
    checkinit()
    print(f"Selecting nozzle: {nozzle}")
    if nozzle == "SMALL":
        Small_Nozzle.on()
        sleep(NOZZLE_PRE_DELAY)
        Large_Nozzle.off()
    elif nozzle == "LARGE":
        Large_Nozzle.on()
        sleep(NOZZLE_PRE_DELAY)
        Small_Nozzle.off()
    else:
        print("Unknown nozzle type")


def Pump_On():
    checkinit()
    Pump.on()
    print("Pump ON")


def Pump_Off():
    checkinit()
    Pump.off()
    print("Pump OFF")
    
    


def Stop_Spray():
    checkinit()
    Pump.off()
    Large_Nozzle.off()
    Small_Nozzle.on()  # always open to maintain pressure
    print("Spray stopped, SMALL nozzle still open")


def Clear_Spray():
    if initialized:
        Pump.off()
        Small_Nozzle.off()
        Large_Nozzle.off()
        print("Spray system cleared")
