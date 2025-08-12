import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import subprocess
import psutil

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
    """Muestra el estado de la Raspberry Pi y servicios."""
    if str(update.effective_chat.id) != CHAT_ID_AUTORIZADO:
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    try:
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()

        # Comando para servicios
        cmd = [
            "/usr/bin/systemctl", "status",
            "telegram-notification.service",
            "telegram-bot-listener.service",
            "guardar_datos.service",
            "raspberry-monitor.service",
            "--no-pager"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5  # máximo 5 segundos
            )
            services_status = escape_markdown(result.stdout)
        except subprocess.TimeoutExpired:
            services_status = escape_markdown("⚠️ Tiempo de espera excedido al consultar los servicios.")

        # Escapar valores de CPU y RAM
        cpu_str = escape_markdown(f"{cpu_percent}%")
        ram_percent_str = escape_markdown(f"{ram.percent}%")
        ram_used_str = escape_markdown(f"{ram.used / (1024**2):.2f} MB")
        ram_total_str = escape_markdown(f"{ram.total / (1024**2):.2f} MB")

        message = (
            "*Estado de la Raspberry Pi*\n\n"
            f"CPU: `{cpu_str}`\n"
            f"RAM: `{ram_percent_str}` (`{ram_used_str}` de `{ram_total_str}`)\n\n"
            "*Estado de los Servicios*\n"
            f"```\n{services_status}```"
        )

        await update.message.reply_text(message, parse_mode='MarkdownV2')

    except Exception as e:
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
