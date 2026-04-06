from machine import Pin, ADC, time_pulse_us
import onewire, ds18x20
import time

class Sensor:
    def __init__(self, pin_number, name):
        self.pin_number = pin_number
        self.name = name

    def read(self):
        raise NotImplementedError("Subclass must implement read()")

    def report(self):
        print(f"{self.name}: {self.read()}")

class TemperatureSensor(Sensor):
    def __init__(self, pin_number, name):
        super().__init__(pin_number, name)
        self.dat = Pin(pin_number)
        self.ds = ds18x20.DS18X20(onewire.OneWire(self.dat))
        self.roms = self.ds.scan()

    def read(self):
        self.ds.convert_temp()
        time.sleep_ms(750)
        temp_value = self.ds.read_temp(self.roms[0])
        return f"{temp_value:.1f} °C"

class UltraSonicSensor(Sensor):
    def __init__(self, trig_pin, echo_pin, name):
        super().__init__(trig_pin, name)
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

    def read(self):
        self.trig.off()
        time.sleep_us(2)
        self.trig.on()
        time.sleep_us(10)
        self.trig.off()
        duration = time_pulse_us(self.echo, 1, 30000)
        if duration < 0:
            return "Out of Range"
        distance = duration * (0.0340/2)
        return (f"{distance:.1f}cm")

class MoistureSensor(Sensor):
    def __init__(self, pin_number, name):
        super().__init__(pin_number, name)
        self.adc = ADC(Pin(pin_number))
        self.adc.atten(ADC.ATTN_11DB)

    def read(self):
        raw = self.adc.read()
        percentage = ((raw / 4095) * 100)
        return (f"{percentage:.1f} %")

class RainSensor(Sensor):
    def __init__(self, pin_number, name):
        super().__init__(pin_number, name)
        self.adc = ADC(Pin(pin_number))
        self.adc.atten(ADC.ATTN_11DB)

    def read(self):
        raw = self.adc.read()
        percentage = int((raw / 4095) * 100)
        return percentage,(f"{percentage:.1f} %")

    def status(self):
        rain_pct = self.read()
        if rain_pct >= 60:
            return "RAINING"
        elif rain_pct >= 2:
            return "LIGHT RAIN"
        else:
            return "NO RAIN"

class Pump:
    def __init__(self, pin_number):
        self.pin = Pin(pin_number, Pin.OUT)
        self.pin.value(0)
        self.is_on = False

    def turn_on(self):
        self.pin.value(1)
        self.is_on = True

    def turn_off(self):
        self.pin.value(0)
        self.is_on = False

    def status(self):
        return "PUMP ON" if self.is_on else "PUMP OFF"

PUMP_ON_THRESHOLD = 2
PUMP_OFF_THRESHOLD = 60

print("=" * 45)
print("   Smart Irrigation - Rain Sensor Module")
print("=" * 45)

temp = TemperatureSensor(4, "Temperature")
distance = UltraSonicSensor(18, 19, "Distance")
moisture = MoistureSensor(32, "Moisture")
rain_sensor = RainSensor(33,"Rain")
pump = Pump(pin_number=25)



while True:
    rain_percentage, rain_pct_formatted = rain_sensor.read()
    rain_status = rain_sensor.read()

    if rain_percentage < PUMP_ON_THRESHOLD:
        pump.turn_on()
    elif rain_percentage >= PUMP_OFF_THRESHOLD:
        pump.turn_off()

    print("Rain: {}  |  {}".format(rain_pct_formatted,  pump.status()))
    temp.report()
    distance.report()
    moisture.report()
    rain_sensor.report()
    time.sleep(2)
