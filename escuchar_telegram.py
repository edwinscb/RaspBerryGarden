import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

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

def main() -> None:
    """Inicia el bot."""
    # Crea la aplicación y pásale el token de tu bot.
    application = Application.builder().token(TOKEN).build()

    # Enlaza el manejador para el comando 'start'.
    application.add_handler(CommandHandler("start", start))

    # Inicia el bot para escuchar mensajes.
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()