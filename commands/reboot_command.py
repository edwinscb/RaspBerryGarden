import subprocess
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import CHAT_ID_AUTORIZADO
from utils import logger, escape_markdown

COMMAND_NAME = "reboot"

# Estado de confirmación
esperando_confirmacion = False
task_expiracion = None  # Para guardar el temporizador

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /reboot: pide confirmación con botones."""
    global esperando_confirmacion, task_expiracion

    chat_id = str(update.effective_chat.id)

    if chat_id != CHAT_ID_AUTORIZADO:
        logger.warning(f"Usuario no autorizado intentando usar /reboot: {chat_id}")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    if not esperando_confirmacion:
        esperando_confirmacion = True

        keyboard = [
            [
                InlineKeyboardButton("✅ Sí", callback_data="reboot_yes"),
                InlineKeyboardButton("❌ No", callback_data="reboot_no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = "⚠️ ¿Seguro que quieres reiniciar la Raspberry Pi?\n⏳ Este diálogo expirará en 30 segundos."
        await update.message.reply_text(escape_markdown(msg), parse_mode="MarkdownV2", reply_markup=reply_markup)

        # Iniciar temporizador de 30 segundos
        task_expiracion = asyncio.create_task(expirar_confirmacion(context, update.effective_chat.id))
    else:
        await update.message.reply_text("Ya estás en proceso de confirmación. Usa los botones para responder.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja las respuestas de los botones."""
    global esperando_confirmacion, task_expiracion

    query = update.callback_query
    chat_id = str(query.message.chat_id)

    if chat_id != CHAT_ID_AUTORIZADO or not esperando_confirmacion:
        await query.answer()  # Responde al botón sin acción
        return

    await query.answer()  # Evita el "loading..."

    if query.data == "reboot_yes":
        esperando_confirmacion = False
        if task_expiracion:
            task_expiracion.cancel()
        await query.edit_message_text("♻️ Reiniciando la Raspberry Pi...")
        logger.info("Reiniciando Raspberry Pi por comando de Telegram.")
        subprocess.run(["sudo", "reboot"], check=False)

    elif query.data == "reboot_no":
        esperando_confirmacion = False
        if task_expiracion:
            task_expiracion.cancel()
        await query.edit_message_text("❌ Reinicio cancelado.")
        logger.info("Reinicio cancelado por el usuario.")

async def expirar_confirmacion(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Cancela la confirmación después de 30 segundos si no hay respuesta."""
    global esperando_confirmacion
    try:
        await asyncio.sleep(30)
        if esperando_confirmacion:
            esperando_confirmacion = False
            await context.bot.send_message(chat_id, "⌛ Tiempo de confirmación agotado. Reinicio cancelado.")
            logger.info("Reinicio cancelado por inactividad.")
    except asyncio.CancelledError:
        pass
