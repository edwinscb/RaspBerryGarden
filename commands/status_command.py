import subprocess
import psutil
import shutil
import traceback
from telegram import Update
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO, SERVICIOS
from utils import logger, escape_markdown

COMMAND_NAME = "status"

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /status"""
    logger.info(f"Comando /status recibido de chat_id={update.effective_chat.id}")

    if str(update.effective_chat.id) != CHAT_ID_AUTORIZADO:
        logger.warning("Usuario no autorizado intentando usar /status")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    try:
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        total_disk, used_disk, _ = shutil.disk_usage("/")
        disk_percent = used_disk / total_disk * 100

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
            estado_servicios.append(f"{icono} {servicio} — {cpu_seg:.1f}s CPU")

        raw_message = (
            f"📊 Estado de la Raspberry Pi\n"
            f"• CPU: {cpu_percent}%\n"
            f"• RAM: {ram.percent}% ({ram.used / (1024**2):.2f} MB de {ram.total / (1024**2):.2f} MB)\n"
            f"💾 Almacenamiento: {disk_percent:.1f}% ({used_disk / (1024**3):.2f} GB de {total_disk / (1024**3):.2f} GB)\n\n"
            f"🛠 Servicios:\n" +
            "\n".join(estado_servicios)
        )

        safe_message = escape_markdown(raw_message)
        await update.message.reply_text(safe_message, parse_mode='MarkdownV2')

    except Exception as e:
        logger.error("Error en /status:\n" + traceback.format_exc())
        error_text = escape_markdown(str(e))
        await update.message.reply_text(f"Ocurrió un error inesperado: {error_text}", parse_mode='MarkdownV2')
