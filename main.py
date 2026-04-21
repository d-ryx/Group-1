
from machine import Pin, ADC, time_pulse_us, SoftI2C
import onewire, ds18x20
import time
from  i2c_lcd import I2cLcd

#Setting up the LCD
I2C_ADDR = 0x27
i2c = SoftI2C(sda=Pin(16), scl=Pin(17), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, 4, 20) 
lcd.clear()
lcd.move_to(2,1)
lcd.putstr("SWIMS IRRIGATION")
time.sleep(2)

class Sensor:
    def __init__(self, pin_number, name):
        self.pin_number = pin_number
        self.name = name

    def read(self):
        raise NotImplementedError("Subclass must implement read()")

    def report(self):
        return f"{self.name}: {self.read()}"

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
        self.tank_height = 300
        self.water_level = 0

    def read(self):
        self.trig.off()
        time.sleep_us(2)
        self.trig.on()
        time.sleep_us(10)
        self.trig.off()
        duration = time_pulse_us(self.echo, 1, 30000)
        if duration < 0:
            self.water_level = -1 
            return -1
        distance = duration * 0.017 # (0.034/2) where  0.034cm/microsecond is speed of sound in air
        percent = ((self.tank_height - distance) / self.tank_height) * 100
        self.water_level = max(0, min(100, percent))
        return self.water_level
        
    def report(self):
        if self.water_level < 0:
            return f"{self.name}: Error"
        return f"{self.name}: {self.water_level:.1f}%"
       
class MoistureSensor(Sensor):
    def __init__(self, pin_number, name):
        super().__init__(pin_number, name)
        self.adc = ADC(Pin(pin_number))
        self.adc.atten(ADC.ATTN_11DB)

    def read(self):
        raw = self.adc.read()
        percentage = (raw / 4095) * 100
        return round(percentage, 1)

    def report(self):
        percentage = self.read()
        return (f"{self.name}: {percentage:.1f}%")

class RainSensor(Sensor):
    def __init__(self, pin_number, name):
        super().__init__(pin_number, name)
        self.adc = ADC(Pin(pin_number))
        self.adc.atten(ADC.ATTN_11DB)

    def read(self):
        raw = self.adc.read()
        percentage = (raw / 4095) * 100
        return percentage

    def status(self):
        """Shows the weather status"""
        rain_pct = self.read()
        if rain_pct >= 60:
            status = "RAINING"
        elif rain_pct >= 2:
            status = "LIGHT RAIN"
        else:
            status = "NO RAIN"
        return f"{status}"

    def report(self):
        """Returns name and rain percentage"""
        rain_pct = self.read()   
        return f"{self.name}: {rain_pct:.1f}%"

class IrrigationPump:
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

class RefillPump:
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
        return "REFILL PUMP ON" if self.is_on else "REFILL PUMP OFF"

# Thresholds
REFILL_ON_THRESHOLD = 25   # Tank low → start filling
REFILL_OFF_THRESHOLD = 90  # Tank sufficiently full → stop filling

PUMP_ON_THRESHOLD = 2
PUMP_OFF_THRESHOLD = 60

soil_dry = 30
soil_wet = 60

temp = TemperatureSensor(4, "Temperature")
tank_status = UltraSonicSensor(18, 19, "Tank Status")
moisture = MoistureSensor(32, "Moisture")
rain_sensor = RainSensor(33,"Rain")
pump_empty = IrrigationPump(25)
pump_refill = RefillPump(21)
sensors = [temp, tank_status, moisture, rain_sensor]

while True:
    lcd.clear()
    cursor_y = 0
    print("=" * 45)
    print("Smart Irrigation".center(45))
    print("=" * 45)

    rain_value = rain_sensor.read()
    rain_status = rain_sensor.status()
    tank = tank_status.read()
    soil_value = moisture.read()

    if rain_value <= PUMP_ON_THRESHOLD and soil_value <= soil_dry:
        pump_empty.turn_on()
    else:
        pump_empty.turn_off()

    if tank < REFILL_ON_THRESHOLD:
        pump_refill.turn_on()
    else:
        pump_refill.turn_off()

    print(f"  {rain_status}  |  {pump_empty.status()}  |  {pump_refill.status()}")
    for sensor in sensors:
        print(sensor.report())
        lcd.move_to(0, cursor_y)
        lcd.putstr(str(sensor.report()))
        cursor_y += 1
        time.sleep(1)
    time.sleep(1)
    

    
