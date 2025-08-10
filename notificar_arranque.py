import subprocess
import datetime
import shutil

# Importa la función del otro script
from notificar_telegram import enviar_mensaje_telegram

# Obtener información del sistema
# ----------------------------------------
# Hora actual
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Nombre del host
hostname = subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()

# Dirección IP
ip_address = subprocess.run(['hostname', '-I'], capture_output=True, text=True).stdout.strip()

# Temperatura de la CPU
try:
    cpu_temp = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True).stdout.strip().split('=')[1]
except (FileNotFoundError, IndexError):
    cpu_temp = "N/A"

# Uso del disco
total, used, free = shutil.disk_usage("/")
disk_usage = f"Usado: {used // (2**30)}GB / {total // (2**30)}GB"
# ----------------------------------------

# Construir el mensaje
message = f"""
✅ *Raspberry Pi encendida y lista.*
-----------------------------------
📅 **Fecha y hora:** {timestamp}
💻 **Host:** {hostname}
🌐 **IP Local:** {ip_address}
🌡️ **Temp. CPU:** {cpu_temp}
💾 **Disco:** {disk_usage}
"""

# Enviar el mensaje usando la función importada
enviar_mensaje_telegram(message)
