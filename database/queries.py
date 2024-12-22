import sqlite3
import pendulum

DB_NAME = "results.db"


def get_start_of_day():
    # Obtener la fecha actual en la zona horaria de España
    spain_tz = pendulum.timezone('Europe/Madrid')
    now = pendulum.now(spain_tz)

    # Si la hora actual es antes de las 9 AM, obtenemos el inicio del día como 9 AM de ayer
    if now.hour < 9:
        start_of_day = now.subtract(days=1).set(hour=9, minute=0, second=0)
    else:
        start_of_day = now.set(hour=9, minute=0, second=0)

    return start_of_day


def init_db():
    # Inicializar la base de datos si no existe
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    juego_queens INTEGER,
                    juego_tango INTEGER,
                    fecha_hora TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS victorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    juego TEXT,
                    numero_juego INTEGER,
                    tiempo INTEGER)''')  # Añadimos el número de juego y el tiempo
    
    conn.commit()
    conn.close()


# Definir la función para guardar los resultados
def save_results(nombre, juego_queens, juego_tango):
    # Obtener la fecha y hora actual en formato adecuado
    fecha_hora = pendulum.now().to_datetime_string()

    # Usar las fechas fijas de referencia para cada juego
    tango_base_date = pendulum.parse('2024-10-08')  # Fecha de referencia de Tango
    queens_base_date = pendulum.parse('2024-04-30')  # Fecha de referencia de Queens

    # Calcular el número de días transcurridos desde la fecha base de cada juego
    now = pendulum.now()
    tango_game_number = now.diff(tango_base_date).in_days()
    queens_game_number = now.diff(queens_base_date).in_days()

    # Guardar los resultados en la base de datos
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Insertar los resultados en la tabla 'resultados'
    c.execute('''INSERT INTO resultados (nombre, juego_queens, juego_tango, fecha_hora)
                 VALUES (?, ?, ?, ?)''', (nombre, queens_game_number, tango_game_number, fecha_hora))
    conn.commit()

    # Guardar el número de juego correspondiente en la tabla de victorias
    # Guardamos los datos de victorias con el número de juego calculado
    c.execute('''INSERT INTO victorias (nombre, juego, numero_juego, tiempo)
                 VALUES (?, ?, ?, ?)''', (nombre, 'tango', tango_game_number, juego_tango))
    c.execute('''INSERT INTO victorias (nombre, juego, numero_juego, tiempo)
                 VALUES (?, ?, ?, ?)''', (nombre, 'queens', queens_game_number, juego_queens))

    conn.commit()
    conn.close()

    print(f"Datos guardados para {nombre}: Juego Queens #{queens_game_number}, Juego Tango #{tango_game_number}")


def get_ranking():
    # Obtener el inicio del día (9 AM del día actual o de ayer si es antes de las 9 AM)
    start_of_day = get_start_of_day().to_datetime_string()

    # Conectar a la base de datos y obtener el ranking desde el inicio del día hasta ahora
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Ejecutar la consulta SQL para obtener los resultados del día
    c.execute("SELECT nombre, juego_queens, juego_tango FROM resultados WHERE fecha_hora >= ? ORDER BY fecha_hora ASC", (start_of_day,))
    ranking_hoy = c.fetchall()
    conn.close()

    # Procesar los resultados para mostrar el ranking
    if ranking_hoy:
        print(ranking_hoy)
        ranking_message = "Ranking de Resultados (Hoy):\n"
        print(ranking_hoy)  # Esto se usa para depurar los resultados
        for idx, (nombre, juego_queens, juego_tango) in enumerate(ranking_hoy, start=1):
            ranking_message += f"{idx}. {nombre} - Queens: {juego_queens}s | Tango: {juego_tango}s\n"
    else:
        ranking_message = "No hay resultados registrados hoy."

    return ranking_message




def get_historical_ranking():
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Obtener los mejores tiempos para cada número de juego de Tango
    c.execute('''SELECT nombre, numero_juego, MIN(tiempo) as mejor_tiempo 
                 FROM victorias WHERE juego = 'tango' 
                 GROUP BY numero_juego, nombre
                 ORDER BY numero_juego''')
    tango_victories = c.fetchall()

    # Obtener los mejores tiempos para cada número de juego de Queens
    c.execute('''SELECT nombre, numero_juego, MIN(tiempo) as mejor_tiempo 
                 FROM victorias WHERE juego = 'queens' 
                 GROUP BY numero_juego, nombre
                 ORDER BY numero_juego''')
    queens_victories = c.fetchall()

    # Ahora sumamos las victorias por jugador
    c.execute('''SELECT nombre, COUNT(*) as victorias
                 FROM victorias
                 WHERE juego = 'tango' OR juego = 'queens'
                 GROUP BY nombre
                 ORDER BY victorias DESC''')
    ranking = c.fetchall()

    conn.close()
    return ranking, tango_victories, queens_victories

