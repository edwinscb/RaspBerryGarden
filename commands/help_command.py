from telegram import Update
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO

COMMAND_NAME = "help"

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help"""
    if str(update.effective_chat.id) == CHAT_ID_AUTORIZADO:
        comandos_disponibles = [
            "/start - Inicia una conversación con el bot.",
            "/help - Muestra los comandos disponibles.",
            "/status - Muestra el estado de la Raspberry Pi y sus servicios.",
            "/reboot - Reinicia la Raspberry Pi (requiere confirmación).",
        ]
        await update.message.reply_text("Comandos disponibles:\n" + "\n".join(comandos_disponibles))
    else:
        await update.message.reply_text("Lo siento, no estás autorizado para usar este bot.")
