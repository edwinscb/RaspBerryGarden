import time
import json
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Importa la función de notificación desde tu archivo
from notificar_telegram import enviar_mensaje_telegram

ARCHIVO_CALIBRACION = "calibracion.json"

class CapacitiveMoistureSensorCalibrado:
    def __init__(self, canal):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)
        self.chan = AnalogIn(self.ads, canal)

    def calibrar_punto(self, mensaje_telegram):
        enviar_mensaje_telegram(mensaje_telegram)
        enviar_mensaje_telegram("🤖 Espera 30 segundos mientras tomo 10 lecturas.")
        
        # Simulamos una pausa en la espera de una acción del usuario
        time.sleep(30)
        
        lecturas = []
        for i in range(10):
            valor = self.chan.value
            lecturas.append(valor)
            enviar_mensaje_telegram(f"Lectura {i+1}/10: {valor}")
            time.sleep(3)
            
        promedio = sum(lecturas) / len(lecturas)
        enviar_mensaje_telegram(f"✅ Promedio de lecturas: *{promedio:.2f}*")
        return promedio

def guardar_calibracion(seco, mojado):
    datos = {"valor_seco": seco, "valor_mojado": mojado}
    with open(ARCHIVO_CALIBRACION, "w") as f:
        json.dump(datos, f)
    
    mensaje_guardado = (
        f"💾 *Calibración guardada*:\n"
        f"💧 Valor Seco: *{seco:.2f}*\n"
        f"💦 Valor Mojado: *{mojado:.2f}*"
    )
    enviar_mensaje_telegram(mensaje_guardado)

def main():
    enviar_mensaje_telegram("🚀 *Iniciando calibración del sensor...*")
    
    # Mensajes de preparación y precaución
    enviar_mensaje_telegram(
        "⚠️ *Preparación para la calibración* ⚠️\n\n"
        "1. Ten listo el sensor y un recipiente con agua o tierra húmeda.\n"
        "2. El proceso durará unos 2 minutos en total.\n"
        "3. No toques ni muevas el sensor durante las tomas de lectura."
    )
    time.sleep(10) # Espera 10 segundos para que el usuario lea

    try:
        sensor = CapacitiveMoistureSensorCalibrado(ADS.P0)
        
        # Calibración del punto seco
        enviar_mensaje_telegram("🌬️ *Paso 1: Calibración en aire seco*.\n\n"
                                "Coloca el sensor en el aire (sin tocar nada) para la primera lectura. Te avisaré cuando termine.")
        valor_seco = sensor.calibrar_punto("") # El mensaje específico se puso antes
        
        # Calibración del punto mojado
        enviar_mensaje_telegram("💧 *Paso 2: Calibración en agua o suelo húmedo*.\n\n"
                                "Ahora, sumerge el sensor en agua o en tierra húmeda para la segunda lectura. Te avisaré cuando esté listo.")
        valor_mojado = sensor.calibrar_punto("") # El mensaje específico se puso antes
        
        guardar_calibracion(valor_seco, valor_mojado)
        enviar_mensaje_telegram("🎉 *¡Calibración finalizada!*")
        
    except Exception as e:
        enviar_mensaje_telegram(f"❌ *Ha ocurrido un error*: {e}")
        
if __name__ == "__main__":
    main()
