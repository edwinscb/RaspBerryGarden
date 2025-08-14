import subprocess
import asyncio
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO
from utils import escape_markdown

# Configurar logger para que imprima en consola
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

COMMAND_NAME = "reboot"

# Estado
esperando_confirmacion = False
task_expiracion = None
pending_msg_chat_id = None
pending_msg_message_id = None

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /reboot: pide confirmación con botones y expira en 30s. """
    global esperando_confirmacion, task_expiracion, pending_msg_chat_id, pending_msg_message_id

    logger.debug("Comando /reboot recibido.")
    user_id = str(update.effective_user.id)
    logger.debug(f"Usuario que ejecuta: {user_id}")

    if user_id != CHAT_ID_AUTORIZADO:
        logger.warning(f"Usuario NO autorizado: {user_id}")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        return

    if esperando_confirmacion:
        logger.debug("Ya hay una confirmación pendiente.")
        await update.message.reply_text("Ya hay una confirmación pendiente. Usa los botones del mensaje anterior.")
        return

    esperando_confirmacion = True

    keyboard = [[
        InlineKeyboardButton("✅ Sí", callback_data="reboot_yes"),
        InlineKeyboardButton("❌ No", callback_data="reboot_no"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = "⚠️ ¿Seguro que quieres reiniciar la Raspberry Pi?\n⏳ Este diálogo expira en 30 segundos."
    logger.debug("Enviando mensaje de confirmación con botones.")
    sent = await update.message.reply_text(
        escape_markdown(msg), parse_mode="MarkdownV2", reply_markup=reply_markup
    )

    pending_msg_chat_id = sent.chat.id
    pending_msg_message_id = sent.message_id
    logger.debug(f"Mensaje enviado con ID: {pending_msg_message_id}")

    task_expiracion = asyncio.create_task(expirar_confirmacion(context))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Maneja los clicks de los botones ✅/❌ """
    global esperando_confirmacion, task_expiracion

    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    logger.debug(f"Botón pulsado por usuario {user_id}, data={query.data}")

    if user_id != CHAT_ID_AUTORIZADO or not esperando_confirmacion:
        logger.debug("Botón ignorado (usuario no autorizado o confirmación expirada).")
        return

    if task_expiracion:
        logger.debug("Cancelando temporizador de expiración.")
        task_expiracion.cancel()
        task_expiracion = None

    esperando_confirmacion = False

    try:
        logger.debug("Quitando botones del mensaje.")
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning(f"No se pudo quitar el reply_markup: {e}")

    if query.data == "reboot_yes":
        logger.info("Usuario confirmó reinicio.")
        await query.edit_message_text("♻️ Reiniciando la Raspberry Pi...")
        subprocess.run(["sudo", "reboot"], check=False)
    elif query.data == "reboot_no":
        logger.info("Usuario canceló reinicio.")
        await query.edit_message_text("❌ Reinicio cancelado.")

async def expirar_confirmacion(context: ContextTypes.DEFAULT_TYPE):
    """ Expira la confirmación a los 30s, desactivando los botones. """
    global esperando_confirmacion, pending_msg_chat_id, pending_msg_message_id
    try:
        logger.debug("Esperando 30s para expiración de confirmación.")
        await asyncio.sleep(30)
        if esperando_confirmacion and pending_msg_chat_id and pending_msg_message_id:
            logger.info("Tiempo de confirmación agotado.")
            esperando_confirmacion = False
            try:
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
    except asyncio.CancelledError:
        logger.debug("Expiración cancelada porque el usuario pulsó un botón.")
