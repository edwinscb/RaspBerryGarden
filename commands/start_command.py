from telegram import Update
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO
from utils import logger

COMMAND_NAME = "start"

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    if str(update.effective_chat.id) == CHAT_ID_AUTORIZADO:
        user = update.effective_user
        await update.message.reply_html(
            f"Hola {user.mention_html()}! Estoy escuchando tus comandos. Usa /help para ver los comandos disponibles."
        )
    else:
        logger.warning(f"Usuario no autorizado: {update.effective_chat.id}")
        await update.message.reply_text("Lo siento, no estás autorizado para usar este bot.")
