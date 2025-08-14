import subprocess
import psutil
import shutil
import traceback
import time
import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO, SERVICIOS
from utils import logger, escape_markdown

COMMAND_NAME = "status"

def nivel_icono(p):
    """Devuelve ícono según porcentaje"""
    return "🟢" if p < 70 else "🟡" if p < 90 else "🔴"

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /status mejorado"""
    logger.info(f"Comando /status recibido de chat_id={update.effective_chat.id}")

    if str(update.effective_chat.id) != CHAT_ID_AUTORIZADO:
        logger.warning("Usuario no autorizado intentando usar /status")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    try:
        # Uptime del sistema
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))

        # Recursos principales
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        total_disk, used_disk, _ = shutil.disk_usage("/")
        disk_percent = used_disk / total_disk * 100

        ram_icon = nivel_icono(ram.percent)
        disk_icon = nivel_icono(disk_percent)
        cpu_icon = nivel_icono(cpu_percent)

        # Estado de servicios
        estado_servicios = []
        for servicio in SERVICIOS:
            activo = subprocess.run(
                ["systemctl", "is-active", servicio],
                capture_output=True, text=True
            ).stdout.strip()

            cpu_nanos = subprocess.run(
                ["systemctl", "show", servicio, "--property=CPUUsageNSec"],
                capture_output=True, text=True
            ).stdout.strip()

            try:
                nanos = int(cpu_nanos.split("=")[1])
                cpu_seg = nanos / 1_000_000_000
            except (IndexError, ValueError):
                cpu_seg = 0.0

            icono = "✅" if activo == "active" else "⚠️"
            estado_servicios.append(f"{icono} {servicio:<15} {cpu_seg:>6.1f}s CPU")

        # Ordenar: activos primero
        estado_servicios.sort(key=lambda x: "⚠️" in x)

        # Construir mensaje
        raw_message = (
            f"📊 *Estado de la Raspberry Pi*\n"
            f"⏱ Uptime: `{uptime_str}`\n"
            f"{cpu_icon} CPU: `{cpu_percent}%`\n"
            f"{ram_icon} RAM: `{ram.percent}%` ({ram.used / (1024**2):.2f} MB de {ram.total / (1024**2):.2f} MB)\n"
            f"{disk_icon} Almacenamiento: `{disk_percent:.1f}%` ({used_disk / (1024**3):.2f} GB de {total_disk / (1024**3):.2f} GB)\n\n"
            f"🛠 *Servicios:*\n" +
            "\n".join(estado_servicios)
        )

        # Alerta si algo está caído
        if any("⚠️" in s for s in estado_servicios):
            raw_message += "\n\n⚠️ *Atención:* Uno o más servicios no están activos"

        safe_message = escape_markdown(raw_message)
        await update.message.reply_text(safe_message, parse_mode='MarkdownV2')

    except Exception as e:
        logger.error("Error en /status:\n" + traceback.format_exc())
        error_text = escape_markdown(str(e))
        await update.message.reply_text(f"Ocurrió un error inesperado: {error_text}", parse_mode='MarkdownV2')
