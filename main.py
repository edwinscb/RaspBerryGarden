import smbus2
import time

# Dirección I2C del sensor BH1750 (GY-30)
DEVICE = 0x23 

# Modo de medición de alta resolución (High Resolution Mode)
POWER_ON = 0x01  # Enciende el sensor
ONE_TIME_HIGH_RES_MODE = 0x20

bus = smbus2.SMBus(1)

def read_light():
    # Escribe un comando para iniciar la medición
    bus.write_byte(DEVICE, ONE_TIME_HIGH_RES_MODE)
    time.sleep(0.5)

    # Lee 2 bytes de datos
    data = bus.read_i2c_block_data(DEVICE, 0, 2)

    # Convierte los datos a lux
    lux = (data[1] + (256 * data[0])) / 1.2
    return lux

try:
    while True:
        light_level = read_light()
        print(f"Nivel de luz: {light_level:.2f} lux")
        time.sleep(1)
except KeyboardInterrupt:
    print("Programa terminado por el usuario")
