import re
from telegram import Update
from telegram.ext import ContextTypes
from database.queries import save_results, get_ranking
from utils import validate_name


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"¡Hola {user_name}! Soy el bot que registra y muestra los resultados de los juegos.\n"
        "Para registrar tus tiempos, usa el comando /record, seguido de los tiempos de los dos juegos.\n"
        "Por ejemplo: /record 1:30 85 (primer tiempo para Queens y segundo para Tango).\n"
        "Si quieres ver el ranking de resultados, usa /results."
    )


async def record_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name

    # Verificar si el usuario está autorizado
    if validate_name(user_name):
        # Explicar cómo enviar los tiempos para los dos juegos
        await update.message.reply_text(
            "Para registrar los resultados, por favor, envía los tiempos de los dos juegos en el siguiente formato:\n"
            "Juego Queens: [Tiempo en formato MM:SS o SS]\n"
            "Juego Tango: [Tiempo en formato MM:SS o SS]\n"
            "Ejemplo: '1:25 85' o '85 1:25' (primer tiempo para Queens y segundo para Tango)"
        )
    else:
        await update.message.reply_text(
            "No estás autorizado para registrar resultados. Solo los amigos pueden hacerlo."
        )


# Función para manejar la respuesta del usuario con los tiempos de los juegos
async def handle_tiempos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    message_text = update.message.text

    # Usamos una expresión regular para capturar los tiempos
    match = re.match(r"(\d+[:]\d+|\d+)\s+(\d+[:]\d+|\d+)", message_text)

    if match:
        # Extraemos los dos tiempos, uno para cada juego
        queens_time = match.group(1)
        tango_time = match.group(2)

        # Convertimos los tiempos de MM:SS o SS a solo segundos
        queens_seconds = convert_to_seconds(queens_time)
        tango_seconds = convert_to_seconds(tango_time)

        # Guardar los resultados en la base de datos, reemplazando el registro si ya existe
        save_results(user_name, queens_seconds, tango_seconds)

        await update.message.reply_text(
            f"¡Resultados de {user_name} guardados correctamente!\n"
            f"Juego Queens: {queens_seconds} segundos\n"
            f"Juego Tango: {tango_seconds} segundos"
        )
    else:
        await update.message.reply_text(
            "Por favor, envía los tiempos en el formato correcto: 'Tiempo Queens' 'Tiempo Tango'.\n"
            "Ejemplo: '1:25 85' o '85 1:25'."
        )


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name  # Obtener el nombre del usuario desde Telegram
    
    # Obtener el ranking desde la base de datos, pasando el nombre de usuario
    ranking = get_ranking(user_name)  # Pasar el nombre del usuario a la función
    
    # Formatear el ranking en un mensaje
    if ranking:
        ranking_message = "Ranking de Resultados:\n"
        for idx, (nombre, juego_queens, juego_tango) in enumerate(ranking, start=1):
            ranking_message += f"{idx}. {nombre} - Queens: {juego_queens}s | Tango: {juego_tango}s\n"
    else:
        ranking_message = "No hay resultados registrados aún."

    await update.message.reply_text(ranking_message)



# Función para convertir MM:SS o SS a segundos
def convert_to_seconds(time_str):
    # Si el tiempo está en formato MM:SS, lo convertimos a segundos
    if ':' in time_str:
        minutes, seconds = time_str.split(':')
        return int(minutes) * 60 + int(seconds)
    # Si el tiempo está solo en segundos
    return int(time_str)
