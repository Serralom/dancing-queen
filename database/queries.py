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
    # Obtener el inicio del día (9 AM del día actual o de ayer si es antes de las 9 AM)
    start_of_day = get_start_of_day().to_datetime_string()

    # Obtener la fecha y hora actual en formato adecuado
    fecha_hora = pendulum.now().to_datetime_string()

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Eliminar resultados anteriores del mismo día para el usuario
    c.execute('''DELETE FROM resultados WHERE nombre = ? AND fecha_hora >= ?''', (nombre, start_of_day))

    # Insertar los nuevos resultados en la tabla 'resultados'
    c.execute('''INSERT INTO resultados (nombre, juego_queens, juego_tango, fecha_hora)
                 VALUES (?, ?, ?, ?)''', (nombre, juego_queens, juego_tango, fecha_hora))
    conn.commit()

    # Guardar el número de juego correspondiente en la tabla de victorias
    # Obtener las fechas base de Tango y Queens
    tango_base_date = pendulum.parse('2024-10-08')  # Fecha de referencia de Tango
    queens_base_date = pendulum.parse('2024-04-30')  # Fecha de referencia de Queens

    # Calcular el número de días transcurridos desde la fecha base de cada juego
    tango_game_number = pendulum.now().diff(tango_base_date).in_days()
    queens_game_number = pendulum.now().diff(queens_base_date).in_days()

    # Eliminar las victorias anteriores del mismo día para el usuario en ambos juegos
    c.execute('''DELETE FROM victorias WHERE nombre = ? AND numero_juego = ? AND juego = 'tango' ''', (nombre, tango_game_number))
    c.execute('''DELETE FROM victorias WHERE nombre = ? AND numero_juego = ? AND juego = 'queens' ''', (nombre, queens_game_number))

    # Guardar los nuevos resultados en la tabla 'victorias'
    c.execute('''INSERT INTO victorias (nombre, juego, numero_juego, tiempo)
                 VALUES (?, ?, ?, ?)''', (nombre, 'tango', tango_game_number, juego_tango))
    c.execute('''INSERT INTO victorias (nombre, juego, numero_juego, tiempo)
                 VALUES (?, ?, ?, ?)''', (nombre, 'queens', queens_game_number, juego_queens))

    # Confirmar los cambios y cerrar la conexión
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

    return ranking_hoy


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


def get_top_precoces():
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Obtener el menor tiempo en Queens
    c.execute('''SELECT MIN(tiempo) FROM victorias WHERE juego = 'queens' ''')
    best_queens_time = c.fetchone()[0]

    # Obtener el menor tiempo en Tango
    c.execute('''SELECT MIN(tiempo) FROM victorias WHERE juego = 'tango' ''')
    best_tango_time = c.fetchone()[0]

    # Obtener todos los jugadores que lograron el mejor tiempo en Queens
    c.execute('''SELECT nombre FROM victorias WHERE juego = 'queens' AND tiempo = ?''', (best_queens_time,))
    best_queens_players = [row[0] for row in c.fetchall()]

    # Obtener todos los jugadores que lograron el mejor tiempo en Tango
    c.execute('''SELECT nombre FROM victorias WHERE juego = 'tango' AND tiempo = ?''', (best_tango_time,))
    best_tango_players = [row[0] for row in c.fetchall()]

    conn.close()

    return best_queens_time, best_queens_players, best_tango_time, best_tango_players


def get_average_times():
    # Conectar a la base de datos y obtener los tiempos promedio por juego
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Consultar los tiempos promedio para 'queens' y 'tango'
    c.execute('''
        SELECT nombre,
               AVG(CASE WHEN juego = 'queens' THEN tiempo END) AS avg_queens,
               AVG(CASE WHEN juego = 'tango' THEN tiempo END) AS avg_tango
        FROM victorias
        GROUP BY nombre
    ''')
    average_times = c.fetchall()

    conn.close()

    # Crear un diccionario con los tiempos promedio por jugador
    avg_times_dict = {nombre: {"avg_queens": avg_queens, "avg_tango": avg_tango}
                      for nombre, avg_queens, avg_tango in average_times}

    return avg_times_dict
