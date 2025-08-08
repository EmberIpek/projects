from machine import Pin, time_pulse_us
import time

TRIGGER = Pin(2, Pin.OUT)
ECHO = Pin(3, Pin.IN)

def checkDist():
    # send pulse
    TRIGGER.value(0)
    time.sleep_us(2)
    TRIGGER.value(1)
    time.sleep_us(10)
    TRIGGER.value(0)
    
    # calculate distance in cm, speed of sound in air = 343m/s
    duration = time_pulse_us(ECHO, 1, 30000)
    if duration < 0:
        return None
    return duration * (343 / 2) * (0.0001)
    
#     while ECHO.value == 0:
#         pass
#     t1 = time.ticks_us()
#     while ECHO.value == 1:
#         pass
#     t2 = time.ticks_us()
#     # print("t1: ", t1, "t2: ", t2)
#     # calculate distance in cm, speed of sound in air = 343m/s
#     return (t2 - t1) * (343 / 2) * (0.01)

while True:
    dist = checkDist()
    print("Distance:", dist)
    time.sleep(0.1)