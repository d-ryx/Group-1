# code for temp
import machine
import onewire, ds18x20
import time

t_pin = machine.Pin(4)
t_sensor = ds18x20.DS18X20(onewire.OneWire(t_pin))
scans = t_sensor.scan()

while True:
    t_sensor.convert_temp()
    time.sleep_ms(750)
    
    for scan in scans:
        # Read the result from the sensor memory
        temp = t_sensor.read_temp(scan)
        print(f"Temperature: {temp:.1f} °C")
    time.sleep(2)


# code for distance
import network
import socket
import time
from machine import Pin, time_pulse_us

# Ultrasonic pins
trigger = Pin(5, Pin.OUT)
echo = Pin(18, Pin.IN)

# Tank height (cm)
TANK_HEIGHT = 100  

def get_distance():
    trigger.off()
    time.sleep_ms(2)
    trigger.on()
    time.sleep_ms(10)
    trigger.off()
    duration = time_pulse_us(echo, 1, 30000)
    distance = (duration / 2) / 29.1
    print (f"Distance: {distance:.1f}cm")
    

while True:
    dist = get_distance()
    time.sleep(2)
    
