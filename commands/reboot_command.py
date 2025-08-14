import subprocess
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO
from utils import logger, escape_markdown

COMMAND_NAME = "reboot"

# Estado
esperando_confirmacion = False
task_expiracion = None
pending_msg_chat_id = None
pending_msg_message_id = None

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /reboot: pide confirmación con botones y expira en 30s. """
    global esperando_confirmacion, task_expiracion, pending_msg_chat_id, pending_msg_message_id

    # Valida usuario (más seguro que validar chat en grupos)
    user_id = str(update.effective_user.id)
    if user_id != CHAT_ID_AUTORIZADO:
        logger.warning(f"Usuario no autorizado intentando usar /reboot: {user_id}")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    if esperando_confirmacion:
        await update.message.reply_text("Ya hay una confirmación pendiente. Usa los botones del mensaje anterior.")
        return

    esperando_confirmacion = True

    keyboard = [[
        InlineKeyboardButton("✅ Sí", callback_data="reboot_yes"),
        InlineKeyboardButton("❌ No", callback_data="reboot_no"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = "⚠️ ¿Seguro que quieres reiniciar la Raspberry Pi?\n⏳ Este diálogo expira en 30 segundos."
    sent = await update.message.reply_text(
        escape_markdown(msg), parse_mode="MarkdownV2", reply_markup=reply_markup
    )

    # Guarda referencia para poder editar/invalidar luego
    pending_msg_chat_id = sent.chat.id
    pending_msg_message_id = sent.message_id

    # Temporizador de expiración
    task_expiracion = asyncio.create_task(expirar_confirmacion(context))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Maneja los clicks de los botones ✅/❌ """
    global esperando_confirmacion, task_expiracion

    query = update.callback_query
    await query.answer()  # quita el spinner

    user_id = str(query.from_user.id)
    if user_id != CHAT_ID_AUTORIZADO or not esperando_confirmacion:
        # Ignora si no es el usuario autorizado o ya no estamos esperando
        return

    data = query.data
    logger.info(f"Callback recibido: {data} por user_id={user_id}")

    # Desactiva expiración
    if task_expiracion:
        task_expiracion.cancel()
        task_expiracion = None

    esperando_confirmacion = False

    # Deshabilita botones antes de editar el texto
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning(f"No se pudo quitar el reply_markup: {e}")

    if data == "reboot_yes":
        await query.edit_message_text("♻️ Reiniciando la Raspberry Pi...")
        logger.info("Reiniciando Raspberry Pi por comando de Telegram.")
        subprocess.run(["sudo", "reboot"], check=False)
    elif data == "reboot_no":
        await query.edit_message_text("❌ Reinicio cancelado.")
        logger.info("Reinicio cancelado por el usuario.")

async def expirar_confirmacion(context: ContextTypes.DEFAULT_TYPE):
    """ Expira la confirmación a los 30s, desactivando los botones. """
    global esperando_confirmacion, pending_msg_chat_id, pending_msg_message_id
    try:
        await asyncio.sleep(30)
        if esperando_confirmacion and pending_msg_chat_id and pending_msg_message_id:
            esperando_confirmacion = False
            try:
                # Quita botones y edita el texto
                await context.bot.edit_message_reply_markup(
                    chat_id=pending_msg_chat_id, message_id=pending_msg_message_id, reply_markup=None
                )
            except Exception as e:
                logger.warning(f"No se pudo quitar reply_markup en expiración: {e}")

            try:
                await context.bot.edit_message_text(
                    chat_id=pending_msg_chat_id,
                    message_id=pending_msg_message_id,
                    text="⌛ Tiempo de confirmación agotado. Reinicio cancelado."
                )
            except Exception as e:
                logger.warning(f"No se pudo editar mensaje en expiración: {e}")
            logger.info("Reinicio cancelado por inactividad.")
    except asyncio.CancelledError:
        # Cancelado porque el usuario pulsó un botón
        pass
