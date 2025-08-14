import subprocess
from telegram import Update
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO
from utils import logger

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
        await update.message.reply_text(
            "⚠️ ¿Seguro que quieres reiniciar la Raspberry Pi?\n"
            "Usa `/reboot confirmar` para continuar.",
            parse_mode="MarkdownV2"
        )
        return

    # Confirmación explícita
    if context.args[0].lower() == "confirmar":
        await update.message.reply_text("♻️ Reiniciando la Raspberry Pi...")
        logger.info("Reiniciando Raspberry Pi por comando de Telegram.")
        subprocess.run(["sudo", "reboot"], check=False)
    else:
        await update.message.reply_text(
            "Comando no reconocido. Si quieres reiniciar, usa:\n"
            "`/reboot confirmar`",
            parse_mode="MarkdownV2"
        )
