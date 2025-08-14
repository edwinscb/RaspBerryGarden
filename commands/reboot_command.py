import subprocess
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

COMMAND_NAME = "reboot"

async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reboot que muestra botones de confirmación."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sí", callback_data="reboot_yes"),
            InlineKeyboardButton("❌ No", callback_data="reboot_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "¿Seguro que quieres reiniciar la Raspberry Pi?",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la respuesta de los botones."""
    query = update.callback_query
    await query.answer()

    if query.data == "reboot_yes":
        await query.edit_message_text("♻ Reiniciando Raspberry Pi...")
        subprocess.run(["sudo", "reboot"])
    elif query.data == "reboot_no":
        await query.edit_message_text("❌ Cancelado el reinicio")
