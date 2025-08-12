import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Habilita el registro para ver lo que hace tu bot.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Reemplaza 'TU_TOKEN_DE_BOT' con el token que te dio BotFather
TOKEN = "8117967778:AAERGuCoPy95XeMviSnZ1Jd_rSmW_j5wk5Q"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje cuando se emite el comando /start."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hola {user.mention_html()}! Estoy escuchando.",
        # El comando 'start' es para empezar una conversación con el bot.
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envía un mensaje cuando se emite el comando /help."""
    await update.message.reply_text("Usa /start para iniciar el bot.")

def main() -> None:
    """Inicia el bot."""
    # Crea la aplicación y pásale el token de tu bot.
    application = Application.builder().token(TOKEN).build()

    # Enlaza los manejadores para los comandos 'start' y 'help'.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Inicia el bot para escuchar mensajes.
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()