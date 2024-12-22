import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from commands import record_results, handle_tiempos, start, results
from database.queries import init_db
from config import BOT_TOKEN

# Configurar el logging para tener visibilidad de los errores
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

# Inicializar la base de datos
init_db()

# Crear la aplicación del bot
application = Application.builder().token(BOT_TOKEN).build()

# Comando /start
application.add_handler(CommandHandler("start", start))

# Comando /results
application.add_handler(CommandHandler("results", results))

# Comando /record y el manejo de los resultados
application.add_handler(CommandHandler("record", record_results))


# Agregar el handler para manejar los tiempos enviados
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiempos))

# Ejecutar el bot
if __name__ == "__main__":
    application.run_polling()
