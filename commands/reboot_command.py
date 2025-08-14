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

    logger.debug("📥 Comando /reboot recibido.")
    logger.debug(f"Usuario: {update.effective_user.id}")

    user_id = str(update.effective_user.id)
    if user_id != CHAT_ID_AUTORIZADO:
        logger.warning(f"❌ Usuario NO autorizado intentando usar /reboot: {user_id}")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    if esperando_confirmacion:
        logger.debug("⚠️ Ya hay una confirmación pendiente.")
        await update.message.reply_text("Ya hay una confirmación pendiente. Usa los botones del mensaje anterior.")
        return

    esperando_confirmacion = True

    keyboard = [[
        InlineKeyboardButton("✅ Sí", callback_data="reboot_yes"),
        InlineKeyboardButton("❌ No", callback_data="reboot_no"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = "⚠️ ¿Seguro que quieres reiniciar la Raspberry Pi?\n⏳ Este diálogo expira en 30 segundos."
    logger.debug("📤 Enviando mensaje de confirmación con botones...")
    sent = await update.message.reply_text(
        escape_markdown(msg), parse_mode="MarkdownV2", reply_markup=reply_markup
    )

    pending_msg_chat_id = sent.chat.id
    pending_msg_message_id = sent.message_id
    logger.debug(f"💾 Mensaje guardado para expiración: chat_id={pending_msg_chat_id}, msg_id={pending_msg_message_id}")

    task_expiracion = asyncio.create_task(expirar_confirmacion(context))
    logger.debug("⏳ Temporizador de expiración iniciado.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Maneja los clicks de los botones ✅/❌ """
    global esperando_confirmacion, task_expiracion

    logger.debug("📥 CallbackQuery recibido (botón presionado).")

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    logger.debug(f"👤 Usuario que presionó botón: {user_id}")
    logger.debug(f"Callback data: {query.data}")

    if user_id != CHAT_ID_AUTORIZADO:
        logger.warning("❌ Usuario no autorizado intentó usar los botones.")
        return

    if not esperando_confirmacion:
        logger.warning("⚠️ Botón presionado pero ya no se estaba esperando confirmación.")
        return

    if task_expiracion:
        logger.debug("🛑 Cancelando temporizador de expiración...")
        task_expiracion.cancel()
        task_expiracion = None

    esperando_confirmacion = False

    try:
        logger.debug("🗑 Quitando botones del mensaje...")
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning(f"⚠️ No se pudo quitar el reply_markup: {e}")

    if query.data == "reboot_yes":
        logger.info("✅ Confirmado reinicio.")
        await query.edit_message_text("♻️ Reiniciando la Raspberry Pi...")
        logger.debug("🔄 Ejecutando comando: sudo reboot")
        subprocess.run(["sudo", "reboot"], check=False)
    elif query.data == "reboot_no":
        logger.info("❌ Reinicio cancelado por el usuario.")
        await query.edit_message_text("❌ Reinicio cancelado.")

async def expirar_confirmacion(context: ContextTypes.DEFAULT_TYPE):
    """ Expira la confirmación a los 30s, desactivando los botones. """
    global esperando_confirmacion, pending_msg_chat_id, pending_msg_message_id
    logger.debug("⏳ Esperando 30 segundos para expiración...")
    try:
        await asyncio.sleep(30)
        if esperando_confirmacion and pending_msg_chat_id and pending_msg_message_id:
            esperando_confirmacion = False
            logger.debug("⌛ Tiempo agotado. Cancelando reinicio.")
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=pending_msg_chat_id, message_id=pending_msg_message_id, reply_markup=None
                )
            except Exception as e:
                logger.warning(f"⚠️ No se pudo quitar reply_markup en expiración: {e}")

            try:
                await context.bot.edit_message_text(
                    chat_id=pending_msg_chat_id,
                    message_id=pending_msg_message_id,
                    text="⌛ Tiempo de confirmación agotado. Reinicio cancelado."
                )
            except Exception as e:
                logger.warning(f"⚠️ No se pudo editar mensaje en expiración: {e}")
            logger.info("ℹ️ Reinicio cancelado por inactividad.")
    except asyncio.CancelledError:
        logger.debug("🛑 Temporizador de expiración cancelado por acción del usuario.")
