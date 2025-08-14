import os
import importlib
from telegram import Update
from telegram.ext import Application, CommandHandler
from config import TOKEN

def load_commands(application):
    commands_dir = "commands"
    for file in os.listdir(commands_dir):
        if file.endswith("_command.py"):
            module_name = f"{commands_dir}.{file[:-3]}"
            module = importlib.import_module(module_name)

            # Aseguramos que tenga las variables esperadas
            if hasattr(module, "COMMAND_NAME") and hasattr(module, "command"):
                application.add_handler(CommandHandler(module.COMMAND_NAME, module.command))
                print(f"✅ Comando /{module.COMMAND_NAME} cargado")
            else:
                print(f"⚠️ {file} no tiene COMMAND_NAME o command()")

def main():
    application = Application.builder().token(TOKEN).build()
    load_commands(application)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
