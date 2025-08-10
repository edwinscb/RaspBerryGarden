# leer_sensores.py
import time
import json
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import smbus2

ARCHIVO_CALIBRACION = "calibracion.json"

class CapacitiveMoistureSensorCalibrado:
    def __init__(self, canal, valor_seco, valor_mojado):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)
        self.chan = AnalogIn(self.ads, canal)
        self.valor_seco = valor_seco
        self.valor_mojado = valor_mojado

    def leer_humedad(self):
        raw = self.chan.value
        humedad = (self.valor_seco - raw) * 100 / (self.valor_seco - self.valor_mojado)
        humedad = max(0, min(100, humedad))
        return humedad, raw, self.chan.voltage

class GY30:
    def __init__(self, bus_num=1, addr=0x23):
        self.bus = smbus2.SMBus(bus_num)
        self.addr = addr

    def leer_luz(self):
        self.bus.write_byte(self.addr, 0x10)
        time.sleep(0.2)
        data = self.bus.read_i2c_block_data(self.addr, 0x00, 2)
        lux = (data[0] << 8) + data[1]
        lux = lux / 1.2
        return lux

def cargar_calibracion():
    with open(ARCHIVO_CALIBRACION, "r") as f:
        datos = json.load(f)
    return datos["valor_seco"], datos["valor_mojado"]

def iniciar_sensores():
    valor_seco, valor_mojado = cargar_calibracion()
    sensor_humedad = CapacitiveMoistureSensorCalibrado(ADS.P0, valor_seco, valor_mojado)
    sensor_luz = GY30()
    return sensor_humedad, sensor_luz

def leer_todos_sensores(sensor_humedad, sensor_luz):
    humedad, raw, voltaje = sensor_humedad.leer_humedad()
    luz = sensor_luz.leer_luz()
    return humedad, raw, voltaje, luz

if __name__ == "__main__":
    sensor_humedad, sensor_luz = iniciar_sensores()
    print("Leyendo sensores (Ctrl+C para salir)...")
    try:
        while True:
            humedad, raw, voltaje, luz = leer_todos_sensores(sensor_humedad, sensor_luz)
            print(f"Humedad: {humedad:.1f}% | Luz: {luz:.1f} lux")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Fin de lectura")
