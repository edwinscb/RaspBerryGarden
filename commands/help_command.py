import subprocess
from telegram import Update
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO
from utils import logger, escape_markdown

COMMAND_NAME = "reboot"

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /reboot: reinicia la Raspberry Pi con confirmación."""
    chat_id = str(update.effective_chat.id)

    if chat_id != CHAT_ID_AUTORIZADO:
        logger.warning(f"Usuario no autorizado intentando usar /reboot: {chat_id}")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    # Si no hay argumento, pedimos confirmación
    if not context.args:
        msg = "⚠️ ¿Seguro que quieres reiniciar la Raspberry Pi?\nUsa /reboot confirmar para continuar."
        await update.message.reply_text(escape_markdown(msg), parse_mode="MarkdownV2")
        return

    # Confirmación explícita
    if context.args[0].lower() == "confirmar":
        await update.message.reply_text(escape_markdown("♻️ Reiniciando la Raspberry Pi..."), parse_mode="MarkdownV2")
        logger.info("Reiniciando Raspberry Pi por comando de Telegram.")
        subprocess.run(["sudo", "reboot"], check=False)
    else:
        msg = "Comando no reconocido. Si quieres reiniciar, usa:\n/reboot confirmar"
        await update.message.reply_text(escape_markdown(msg), parse_mode="MarkdownV2")
