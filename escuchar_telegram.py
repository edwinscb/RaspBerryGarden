import os
import sys
import importlib
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TOKEN

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR) 
COMMANDS_DIR = os.path.join(BASE_DIR, "commands")

def load_commands(application):
    for file in os.listdir(COMMANDS_DIR):
        if file.endswith("_command.py"):
            module_name = f"commands.{file[:-3]}"
            module = importlib.import_module(module_name)

            if hasattr(module, "COMMAND_NAME") and hasattr(module, "command"):
                application.add_handler(CommandHandler(module.COMMAND_NAME, module.command))
                print(f"✅ Comando /{module.COMMAND_NAME} cargado")

                if hasattr(module, "button_handler"):
                    application.add_handler(CallbackQueryHandler(module.button_handler))
                    print(f"🔘 Botones para /{module.COMMAND_NAME} registrados")
            else:
                print(f"⚠️ {file} no tiene COMMAND_NAME o command()")

def main():
    application = Application.builder().token(TOKEN).build()
    load_commands(application)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
