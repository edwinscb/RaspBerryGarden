import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess
import psutil
import shutil

# Configuración de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Credenciales
TOKEN = "8117967778:AAERGuCoPy95XeMviSnZ1Jd_rSmW_j5wk5Q"
CHAT_ID_AUTORIZADO = "6119961807"

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiales para MarkdownV2."""
    special_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in special_chars else c for c in text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start: inicia la conversación si el usuario está autorizado."""
    if str(update.effective_chat.id) == CHAT_ID_AUTORIZADO:
        user = update.effective_user
        await update.message.reply_html(
            f"Hola {user.mention_html()}! Estoy escuchando tus comandos. Usa /help para ver los comandos disponibles."
        )
    else:
        logger.warning(f"Usuario no autorizado: {update.effective_chat.id}")
        await update.message.reply_text("Lo siento, no estás autorizado para usar este bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help: muestra la lista de comandos."""
    if str(update.effective_chat.id) == CHAT_ID_AUTORIZADO:
        comandos_disponibles = [
            "/start - Inicia una conversación con el bot.",
            "/help - Muestra los comandos disponibles.",
            "/status - Muestra el estado de la Raspberry Pi y sus servicios."
        ]
        await update.message.reply_text("Comandos disponibles:\n" + "\n".join(comandos_disponibles))
    else:
        await update.message.reply_text("Lo siento, no estás autorizado para usar este bot.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra estado de CPU, RAM, almacenamiento y servicios resumido."""
    logger.info(f"Comando /status recibido de chat_id={update.effective_chat.id}")

    if str(update.effective_chat.id) != CHAT_ID_AUTORIZADO:
        logger.warning("Usuario no autorizado intentando usar /status")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    try:
        # Estado general CPU y RAM
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()

        # Estado de almacenamiento
        total_disk, used_disk, free_disk = shutil.disk_usage("/")
        disk_percent = used_disk / total_disk * 100

        # Lista de servicios
        servicios = [
            "telegram-notification.service",
            "telegram-bot-listener.service",
            "guardar_datos.service",
            "raspberry-monitor.service"
        ]
        estado_servicios = []
        for servicio in servicios:
            # Estado activo/inactivo
            activo = subprocess.run(
                ["systemctl", "is-active", servicio],
                capture_output=True, text=True
            ).stdout.strip()

            # CPU consumida
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

        # Construcción del mensaje
        raw_message = (
            f"📊 Estado de la Raspberry Pi\n"
            f"• CPU: {cpu_percent}%\n"
            f"• RAM: {ram.percent}% ({ram.used / (1024**2):.2f} MB de {ram.total / (1024**2):.2f} MB)\n"
            f"💾 Almacenamiento: {disk_percent:.1f}% ({used_disk / (1024**3):.2f} GB de {total_disk / (1024**3):.2f} GB)\n\n"
            f"🛠 Servicios:\n" +
            "\n".join(estado_servicios)
        )

        # Escapar todo
        safe_message = escape_markdown(raw_message)

        await update.message.reply_text(safe_message, parse_mode='MarkdownV2')

    except Exception as e:
        logger.error("Error en /status:\n" + traceback.format_exc())
        error_text = escape_markdown(str(e))
        await update.message.reply_text(f"Ocurrió un error inesperado: {error_text}", parse_mode='MarkdownV2')

def main() -> None:
    """Inicia el bot de Telegram."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
