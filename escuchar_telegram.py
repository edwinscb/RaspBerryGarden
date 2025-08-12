import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import psutil

# Habilita el registro para ver lo que hace tu bot.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TOKEN = "8117967778:AAERGuCoPy95XeMviSnZ1Jd_rSmW_j5wk5Q"
# Define el CHAT_ID del usuario autorizado
CHAT_ID_AUTORIZADO = "6119961807"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /start solo si el usuario está autorizado."""
    # Verificamos si el CHAT_ID del mensaje es el autorizado
    if str(update.effective_chat.id) == CHAT_ID_AUTORIZADO:
        user = update.effective_user
        await update.message.reply_html(
            f"Hola {user.mention_html()}! Estoy escuchando tus comandos."
        )
    else:
        # Opcional: Ignoramos o enviamos un mensaje de no autorización
        logger.info(f"Comando /start ignorado de un usuario no autorizado: {update.effective_chat.id}")
        await update.message.reply_text("Lo siento, no estás autorizado para usar este bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /help y lista los comandos disponibles."""
    if str(update.effective_chat.id) == CHAT_ID_AUTORIZADO:
        comandos_disponibles = [
            "/start - Inicia una conversación con el bot.",
            "/help - Muestra los comandos disponibles.",
            "/status - Muestra el estado de la Raspberry Pi y sus servicios."
        ]
        
        mensaje = "Comandos disponibles:\n" + "\n".join(comandos_disponibles)
        await update.message.reply_text(mensaje)
    else:
        await update.message.reply_text("Lo siento, no estás autorizado para usar este bot.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /status y muestra el estado del sistema."""
    if str(update.effective_chat.id) == CHAT_ID_AUTORIZADO:
        # Obtener información del sistema
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        
        # Obtener el estado de los servicios que has creado
        services_status_command = "systemctl status telegram-notification.service telegram-bot-listener.service guardar_datos.service raspberry-monitor.service --no-pager"
        services_status = os.popen(services_status_command).read()
        
        # Formatear el mensaje
        message = f"**Estado de la Raspberry Pi**\n\n"
        message += f"CPU: {cpu_percent}%\n"
        message += f"RAM: {ram.percent}% ({ram.used / (1024**2):.2f} MB de {ram.total / (1024**2):.2f} MB)\n\n"
        message += f"**Estado de los Servicios**\n"
        message += f"```\n{services_status}```"

        await update.message.reply_text(message, parse_mode='MarkdownV2')
    else:
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")

def main() -> None:
    """Inicia el bot."""
    # Crea la aplicación y pásale el token de tu bot.
    application = Application.builder().token(TOKEN).build()

    # Enlaza el manejador para el comando 'start'.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))

    # Inicia el bot para escuchar mensajes.
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()