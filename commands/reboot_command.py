import subprocess
import asyncio
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import CHAT_ID_AUTORIZADO
from utils import escape_markdown

# Configurar logger para consola
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

COMMAND_NAME = "reboot"

# Estado global
esperando_confirmacion = False
task_expiracion = None
pending_msg_chat_id = None
pending_msg_message_id = None

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /reboot con confirmación y depurado paso a paso """
    global esperando_confirmacion, task_expiracion, pending_msg_chat_id, pending_msg_message_id

    logger.debug("=== [INICIO] Usuario ejecutó /reboot ===")
    logger.debug(f"Usuario ID: {update.effective_user.id}")
    logger.debug(f"Mensaje recibido: {update.message.text if update.message else 'Sin texto'}")

    if str(update.effective_user.id) != CHAT_ID_AUTORIZADO:
        logger.debug("Usuario NO autorizado, enviando respuesta.")
        await update.message.reply_text("Lo siento, no estás autorizado para ejecutar este comando.")
        logger.debug("=== [FIN] Comando rechazado por usuario no autorizado ===")
        return

    if esperando_confirmacion:
        logger.debug("Ya hay confirmación pendiente, notificando al usuario.")
        await update.message.reply_text("Ya hay una confirmación pendiente. Usa los botones del mensaje anterior.")
        logger.debug("=== [FIN] Comando detenido por confirmación previa ===")
        return

    logger.debug("Preparando mensaje de confirmación con botones.")
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

    pending_msg_chat_id = sent.chat.id
    pending_msg_message_id = sent.message_id
    logger.debug(f"Mensaje enviado con ID: {pending_msg_message_id}")

    logger.debug("Creando tarea de expiración de confirmación (30s).")
    task_expiracion = asyncio.create_task(expirar_confirmacion(context))

    logger.debug("=== [FIN] /reboot esperando confirmación ===")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Maneja los botones de confirmación """
    global esperando_confirmacion, task_expiracion

    logger.debug("=== [INICIO] Botón presionado ===")
    query = update.callback_query
    await query.answer()

    logger.debug(f"Usuario que presionó botón: {query.from_user.id}")
    logger.debug(f"Callback data recibida: {query.data}")

    if str(query.from_user.id) != CHAT_ID_AUTORIZADO or not esperando_confirmacion:
        logger.debug("Botón ignorado: usuario no autorizado o confirmación expirada.")
        logger.debug("=== [FIN] Botón ignorado ===")
        return

    if task_expiracion:
        logger.debug("Cancelando tarea de expiración.")
        task_expiracion.cancel()
        task_expiracion = None

    esperando_confirmacion = False

    logger.debug("Eliminando botones del mensaje.")
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning(f"No se pudo eliminar reply_markup: {e}")

    if query.data == "reboot_yes":
        logger.debug("Usuario confirmó reinicio. Ejecutando 'sudo reboot'.")
        await query.edit_message_text("♻️ Reiniciando la Raspberry Pi...")
        subprocess.run(["sudo", "reboot"], check=False)
    elif query.data == "reboot_no":
        logger.debug("Usuario canceló reinicio.")
        await query.edit_message_text("❌ Reinicio cancelado.")

    logger.debug("=== [FIN] Botón procesado ===")

async def expirar_confirmacion(context: ContextTypes.DEFAULT_TYPE):
    """ Expira la confirmación después de 30s """
    global esperando_confirmacion, pending_msg_chat_id, pending_msg_message_id
    logger.debug("Iniciando cuenta regresiva de 30s para expiración.")
    try:
        await asyncio.sleep(30)
        if esperando_confirmacion:
            logger.debug("Tiempo agotado, cancelando reinicio.")
            esperando_confirmacion = False
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=pending_msg_chat_id, message_id=pending_msg_message_id, reply_markup=None
                )
            except Exception as e:
                logger.warning(f"No se pudo quitar botones al expirar: {e}")

            try:
                await context.bot.edit_message_text(
                    chat_id=pending_msg_chat_id,
                    message_id=pending_msg_message_id,
                    text="⌛ Tiempo de confirmación agotado. Reinicio cancelado."
                )
            except Exception as e:
                logger.warning(f"No se pudo editar mensaje al expirar: {e}")
    except asyncio.CancelledError:
        logger.debug("Expiración cancelada porque el usuario tomó una decisión.")
