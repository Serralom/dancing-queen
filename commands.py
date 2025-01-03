import re
from telegram import Update
from telegram.ext import ContextTypes
from queries import save_results, get_ranking, get_historical_ranking, get_top_precoces, get_average_times
from utils import validate_name


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"¡Hola {user_name}!\n"
        "Para ver el ranking de resultados, usa el comando /results.\n"
        "Para registrar tus tiempos, usa el comando /record."
    )


async def record_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name

    if validate_name(user_name):
        await update.message.reply_text(
            "Envía tus tiempos de hoy en Queens y en Tango\n"
            "Primero el tiempo del Queens, después el tiempo del Tango\n"
            "El tiempo ha de estar en formato MM:SS o SS, separados entre sí por un espacio (no usar , o .)\n"
            "Ejemplo: '1:25 40' o '85 243' (primer tiempo para Queens y segundo para Tango)"
        )
    else:
        # await update.message.reply_text(
        #     "No estás autorizado para registrar resultados. Espabila chaval."
        # )
        await update.message.reply_text(
            "Envía tus tiempos de hoy en Queens y en Tango\n"
            "Primero el tiempo del Queens, después el tiempo del Tango\n"
            "El tiempo ha de estar en formato MM:SS o SS, separados entre sí por un espacio (no usar , o .)\n"
            "Ejemplo: '1:25 40' o '85 243' (primer tiempo para Queens y segundo para Tango)"
        )


# Función para manejar los tiempos de los juegos en distintos formatos
async def handle_tiempos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    message_text = update.message.text

    # Expresión regular para capturar los tiempos
    match = re.match(r"(\d+[:]\d+|\d+)\s+(\d+[:]\d+|\d+)", message_text)

    if match:
        queens_time = match.group(1)
        tango_time = match.group(2)

        queens_seconds = convert_to_seconds(queens_time)
        tango_seconds = convert_to_seconds(tango_time)

        save_results(user_name, "tango", tango_seconds)
        save_results(user_name, "queens", queens_seconds)

        await update.message.reply_text(
            f"¡Resultados de {user_name} guardados correctamente!\n"
            f"Queens: {queens_seconds} segundos\n"
            f"Tango: {tango_seconds} segundos"
        )
    else:
        await update.message.reply_text(
            "Por favor, envía los tiempos en el formato correcto: 'Tiempo Queens' 'Tiempo Tango'.\n"
            "Ejemplo: '1:25 40' o '85 243' (primer tiempo para Queens y segundo para Tango)"
        )


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🔎 Resultados disponibles:\n\n"
        "Ranking de hoy: /ranking_hoy\n"
        "Ranking anual de victorias: /ranking_anual\n"
        "Ranking histórico de victorias: /ranking_historico\n"
        "Mejores tiempos y promedios: /mejores_tiempos\n"
        "Todo lo anterior: /todo"
    )
    await update.message.reply_text(message)

    

async def ranking_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ranking_queens = get_ranking("queens")
    ranking_tango = get_ranking("tango")
    ranking_hoy_message = "Ranking de hoy:\n"
    if ranking_queens or ranking_tango:
        ranking_message_queens = "\nRanking Queens:\n"
        for idx, (nombre, tiempo) in enumerate(ranking_queens, start=1):
            ranking_message_queens += f"{idx}. {tiempo}s {nombre}\n"

        ranking_message_tango = "\nRanking Tango:\n"
        for idx, (nombre, tiempo) in enumerate(ranking_tango, start=1):
            ranking_message_tango += f"{idx}. {tiempo}s {nombre}\n"

        ranking_hoy_message += f"{ranking_message_queens}\n{ranking_message_tango}"
    else:
        ranking_hoy_message += "No hay resultados registrados hoy.\n"
    await update.message.reply_text(ranking_hoy_message)

async def ranking_anual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ranking_historico, tango_victories, queens_victories = get_historical_ranking()

    historic_message = "\nRanking Anual: 📅\n"
    historic_message += "\nTango Dancers: 🕺\n"
    for idx, (nombre, victorias) in enumerate(tango_victories, start=1):
        historic_message += f"{idx}. {nombre}: {victorias}\n"

    historic_message += "\nKings of Queens: 👑\n"
    for idx, (nombre, victorias) in enumerate(queens_victories, start=1):
        historic_message += f"{idx}. {nombre}: {victorias}\n"

    historic_message += "\nDancing Queens: 🏆\n"
    for idx, (nombre, victorias) in enumerate(ranking_historico, start=1):
        historic_message += f"{idx}. {nombre}: {victorias}\n"
    await update.message.reply_text(historic_message)

victorias_previas_queens = {
    "Miguel": 1,
    "Carlos": 22,
    "Miguel Serrano": 16,
    "Pachu MS": 3,
    "G.": 30,
    "David": 21,
    "Alejandro": 0,
}

victorias_previas_tango = {
    "Miguel": 2,
    "Carlos": 16,
    "Miguel Serrano": 34,
    "Pachu MS": 11,
    "G.": 10,
    "David": 12,
    "Alejandro": 1,
}

async def ranking_historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ranking_historico, tango_victories, queens_victories = get_historical_ranking()

    tango_victorias_totales = [(nombre, victorias + victorias_previas_tango.get(nombre, 0)) for nombre, victorias in tango_victories]
    tango_victorias_totales_ordenadas = sorted(tango_victorias_totales, key=lambda x: x[1], reverse=True)

    historic_message = "\nRanking Histórico: 📜\n"
    historic_message += "\nTango Dancers: 🕺\n"
    for idx, (nombre, victorias_totales) in enumerate(tango_victorias_totales_ordenadas, start=1):
        historic_message += f"{idx}. {nombre}: {victorias_totales}\n"

    queens_victorias_totales = [(nombre, victorias + victorias_previas_queens.get(nombre, 0)) for nombre, victorias in queens_victories]
    queens_victorias_totales_ordenadas = sorted(queens_victorias_totales, key=lambda x: x[1], reverse=True)

    historic_message += "\nKings of Queens: 👑\n"
    for idx, (nombre, victorias_totales) in enumerate(queens_victorias_totales_ordenadas, start=1):
        historic_message += f"{idx}. {nombre}: {victorias_totales}\n"

    ranking_historico_totales = [(nombre, victorias + victorias_previas_tango.get(nombre, 0) + victorias_previas_queens.get(nombre, 0)) for nombre, victorias in ranking_historico]
    ranking_historico_totales_ordenado = sorted(ranking_historico_totales, key=lambda x: x[1], reverse=True)

    historic_message += "\nDancing Queens: 🏆\n"
    for idx, (nombre, victorias_totales) in enumerate(ranking_historico_totales_ordenado, start=1):
        historic_message += f"{idx}. {nombre}: {victorias_totales}\n"

    await update.message.reply_text(historic_message)



async def mejores_tiempos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    best_queens_time, best_queens_players, best_tango_time, best_tango_players = get_top_precoces()
    avg_times_dict = get_average_times()
    precoces_message = "\nTop Precoces: ⚡️🥵⌛️\n"
    precoces_message += f"Queens: {best_queens_time}s ({', '.join(best_queens_players)})\n"
    precoces_message += f"Tango: {best_tango_time}s ({', '.join(best_tango_players)})\n"
    await update.message.reply_text(precoces_message)

    avg_queens_message = "\nPromedio Queens:\n"
    sorted_queens = sorted(avg_times_dict.items(), key=lambda x: x[1]["avg_queens"] if x[1]["avg_queens"] != "N/A" else float('inf'))
    for nombre, tiempos in sorted_queens:
        avg_queens_time = tiempos["avg_queens"]
        if avg_queens_time is not None:
            avg_queens_message += f"{avg_queens_time:.2f}s - {nombre}\n" if avg_queens_time != "N/A" else ""
    await update.message.reply_text(avg_queens_message)

    avg_tango_message = "\nPromedio Tango:\n"
    sorted_tango = sorted(avg_times_dict.items(), key=lambda x: x[1]["avg_tango"] if x[1]["avg_tango"] != "N/A" else float('inf'))
    for nombre, tiempos in sorted_tango:
        avg_tango_time = tiempos["avg_tango"]
        if avg_tango_time is not None:
            avg_tango_message += f"{avg_tango_time:.2f}s - {nombre}\n" if avg_tango_time != "N/A" else ""
    await update.message.reply_text(avg_tango_message)

async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ranking_hoy(update, context)
    await ranking_anual(update, context)
    await ranking_historico(update, context)
    await mejores_tiempos(update, context)
    

def convert_to_seconds(time_str):
    if ':' in time_str:
        minutes, seconds = time_str.split(':')
        return int(minutes) * 60 + int(seconds)
    return int(time_str)
