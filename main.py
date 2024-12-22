from telegram.ext import Application, CommandHandler
from db import init_db  # Asegúrate de que la base de datos se inicialice antes de usarla
from commands import start, record_results, show_results  # Importar las funciones de comandos
from config import TOKEN  # Token de la configuración

# Inicializar la base de datos
init_db()

# Crear la aplicación del bot
application = Application.builder().token(TOKEN).build()

# Agregar los handlers de comandos
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("record", record_results))
application.add_handler(CommandHandler("results", show_results))  # Registrar el comando /results

# Ejecutar el bot
if __name__ == "__main__":
    application.run_polling()
