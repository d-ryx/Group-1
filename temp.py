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

