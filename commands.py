import re
from telegram import Update
from telegram.ext import ContextTypes
from database.queries import save_results, get_ranking, get_historical_ranking, get_top_precoces, get_average_times
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

    # Obtener el ranking de hoy
    ranking_hoy = get_ranking()

    # Obtener el ranking histórico de victorias y los mejores tiempos
    ranking_historico, tango_victories, queens_victories = get_historical_ranking()

    # Obtener los "Top Precoces"
    best_queens_time, best_queens_players, best_tango_time, best_tango_players = get_top_precoces()

    # Obtener los tiempos promedio por jugador
    avg_times_dict = get_average_times()

    # Procesar los resultados de hoy
    ranking_message = f"Ranking de hoy (para {user_name}):\n"
    if ranking_hoy:
        for idx, (nombre, juego_queens, juego_tango) in enumerate(ranking_hoy, start=1):
            ranking_message += f"{idx}. {nombre} - Queens: {juego_queens}s, Tango: {juego_tango}s\n"
    else:
        ranking_message += "No hay resultados registrados hoy.\n"

    # Procesar el ranking histórico de victorias
    ranking_message += "\nDancind Queens:\n"
    for idx, (nombre, victorias) in enumerate(ranking_historico, start=1):
        ranking_message += f"{idx}. {nombre} - Total victorias: {victorias}\n"

    # Mostrar el ganador de cada edición de Tango
    tango_message = "\nTango Dancers:\n"
    for winner in tango_victories:
        nombre, numero_juego, mejor_tiempo = winner
        tango_message += f"Juego {numero_juego}: {nombre} - Tiempo: {mejor_tiempo}s\n"

    # Mostrar el ganador de cada edición de Queens
    queens_message = "\nKings of Queens:\n"
    for winner in queens_victories:
        nombre, numero_juego, mejor_tiempo = winner
        queens_message += f"Juego {numero_juego}: {nombre} - Tiempo: {mejor_tiempo}s\n"

    # Añadir los "Top Precoces" al mensaje
    precoces_message = "\nTop Precoces:\n"
    precoces_message += f"Queens: {best_queens_time}s ({', '.join(best_queens_players)})\n"
    precoces_message += f"Tango: {best_tango_time}s ({', '.join(best_tango_players)})\n"

    # Mostrar los tiempos promedio de cada jugador
    avg_times_message = "\nTiempos promedio por jugador:\n"
    for nombre, times in avg_times_dict.items():
        avg_queens_time = times["avg_queens"]
        avg_tango_time = times["avg_tango"]
        avg_times_message += f"{nombre} - Promedio Queens: {avg_queens_time:.2f}s | Promedio Tango: {avg_tango_time:.2f}s\n"

    # Mostrar los tiempos promedio de Queens ordenados de menor a mayor
    avg_queens_message = "\nPromedio de Tiempos en Queens (de menor a mayor):\n"
    sorted_queens = sorted(avg_times_dict.items(), key=lambda x: x[1]["avg_queens"] if x[1]["avg_queens"] != "N/A" else float('inf'))
    for nombre, tiempos in sorted_queens:
        avg_queens_time = tiempos["avg_queens"]
        avg_queens_message += f"{nombre} - Promedio Queens: {avg_queens_time:.2f}s\n" if avg_queens_time != "N/A" else ""

    # Mostrar los tiempos promedio de Tango ordenados de menor a mayor
    avg_tango_message = "\nPromedio de Tiempos en Tango (de menor a mayor):\n"
    sorted_tango = sorted(avg_times_dict.items(), key=lambda x: x[1]["avg_tango"] if x[1]["avg_tango"] != "N/A" else float('inf'))
    for nombre, tiempos in sorted_tango:
        avg_tango_time = tiempos["avg_tango"]
        avg_tango_message += f"{nombre} - Promedio Tango: {avg_tango_time:.2f}s\n" if avg_tango_time != "N/A" else ""

    # Enviar los mensajes
    await update.message.reply_text(queens_message)
    await update.message.reply_text(tango_message)
    await update.message.reply_text(precoces_message)
    await update.message.reply_text(ranking_message)
    await update.message.reply_text(avg_times_message)
    await update.message.reply_text(avg_queens_message)
    await update.message.reply_text(avg_tango_message)


# Función para convertir MM:SS o SS a segundos
def convert_to_seconds(time_str):
    # Si el tiempo está en formato MM:SS, lo convertimos a segundos
    if ':' in time_str:
        minutes, seconds = time_str.split(':')
        return int(minutes) * 60 + int(seconds)
    # Si el tiempo está solo en segundos
    return int(time_str)
