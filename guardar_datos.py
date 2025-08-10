import csv
from datetime import datetime
import time
from leer_sensores import iniciar_sensores, leer_todos_sensores
from notificar_telegram import enviar_mensaje_telegram
import traceback

ARCHIVO_CSV = "datos_sensores.csv"

def guardar_csv(fecha, humedad, raw, voltaje, luz):
    header = ["timestamp", "humedad_suelo_%", "valor_crudo_ADC", "voltaje_V", "luz_lux"]
    fila = [fecha, humedad, raw, voltaje, luz]
    try:
        with open(ARCHIVO_CSV, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
    except FileExistsError:
        pass

    with open(ARCHIVO_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fila)

def main():
    try:
        sensor_humedad, sensor_luz = iniciar_sensores()
        enviar_mensaje_telegram("✅ Servicio de guardado de datos iniciado correctamente.")
        print("Guardando datos cada 10 minutos (Ctrl+C para detener)...")

        while True:
            humedad, raw, voltaje, luz = leer_todos_sensores(sensor_humedad, sensor_luz)
            ahora = datetime.now().isoformat(sep=" ", timespec="seconds")
            guardar_csv(ahora, humedad, raw, voltaje, luz)
            print(f"{ahora} | Humedad: {humedad:.1f}% | Luz: {luz:.1f} lux guardados.")
            time.sleep(600)  # 10 minutos

    except KeyboardInterrupt:
        print("Guardado detenido por usuario.")
    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error detectado:", e)
        enviar_mensaje_telegram(f"❌ Error en guardar_datos.py:\n{e}\n\nTraceback:\n{error_trace}")

if __name__ == "__main__":
    main()
