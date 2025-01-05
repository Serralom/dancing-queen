import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from commands import *
from queries import init_db

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Configurar el logging para tener visibilidad de los errores
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

init_db()

application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("results", results))
application.add_handler(CommandHandler("record", record_results))
application.add_handler(CommandHandler("hoy", ranking_hoy))
application.add_handler(CommandHandler("anual", ranking_anual))
application.add_handler(CommandHandler("historico", ranking_historico))
application.add_handler(CommandHandler("mejores_tiempos", mejores_tiempos))
application.add_handler(CommandHandler("todo", todo))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiempos))

if __name__ == "__main__":
    application.run_polling()
