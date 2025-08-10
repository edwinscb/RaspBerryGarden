import subprocess
import shutil

def check_for_alerts():
    """
    Verifica las condiciones de alerta (temperatura, voltaje, disco).
    Retorna un mensaje de alerta si alguna se cumple, o None si todo está bien.
    """
    alerta_mensaje = "🚨 *¡Alerta de Raspberry Pi!* 🚨\n\n"
    hay_alerta = False

    # 1. Verificar la temperatura de la CPU
    try:
        temp_raw = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True).stdout.strip()
        cpu_temp = float(temp_raw.split('=')[1].replace("'", " ").replace("C", ""))
        if cpu_temp > 60:
            alerta_mensaje += f"🔥 *Temperatura alta:* {cpu_temp}°C (Límite: >70°C)\n"
            hay_alerta = True
    except (FileNotFoundError, IndexError, ValueError):
        pass

    # 2. Verificar el bajo voltaje
    try:
        throttled_raw = subprocess.run(['vcgencmd', 'get_throttled'], capture_output=True, text=True).stdout.strip()
        if 'throttled=0x50000' in throttled_raw:
            alerta_mensaje += "⚡️ *Bajo voltaje detectado.* (El rendimiento está afectado)\n"
            hay_alerta = True
    except (FileNotFoundError, IndexError):
        pass

    # 3. Verificar el espacio en disco
    try:
        total, used, free = shutil.disk_usage("/")
        uso_porcentaje = (used / total) * 100
        if uso_porcentaje > 80:
            alerta_mensaje += f"⚠️ *Espacio en disco lleno:* {uso_porcentaje:.2f}% ({used // (2**30)}GB / {total // (2**30)}GB)\n"
            hay_alerta = True
    except Exception:
        pass
    
    return alerta_mensaje if hay_alerta else None

if __name__ == "__main__":
    check_for_alerts()
