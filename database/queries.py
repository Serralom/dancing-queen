import sqlite3
from datetime import datetime
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
    conn.commit()
    conn.close()


def save_results(nombre, juego_queens, juego_tango):
    # Obtener la fecha y hora actual
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Conectar a la base de datos
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Intentar eliminar el registro anterior del mismo día (si existe)
    c.execute('''DELETE FROM resultados WHERE nombre = ? AND fecha_hora >= ?''', (nombre, get_start_of_day().to_datetime_string()))

    # Guardar los nuevos resultados en la base de datos
    c.execute('''INSERT INTO resultados (nombre, juego_queens, juego_tango, fecha_hora)
                 VALUES (?, ?, ?, ?)''', (nombre, juego_queens, juego_tango, fecha_hora))
    conn.commit()
    conn.close()



def get_ranking(user_name):
    # Obtener el inicio del "día" (9 AM a 9 AM)
    start_of_day = get_start_of_day().to_datetime_string()

    # Conectar a la base de datos y filtrar los resultados solo para el "día"
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Seleccionar los tiempos del usuario para el día actual
    c.execute('''SELECT nombre, juego_queens, juego_tango 
                 FROM resultados
                 WHERE nombre = ? AND fecha_hora >= ?
                 ORDER BY fecha_hora DESC LIMIT 1''', (user_name, start_of_day))
    
    ranking = c.fetchall()
    conn.close()

    # Imprimir para depuración (esto ayudará a entender qué devuelve la consulta)
    print(f"Ranking de {user_name}: {ranking}")
    
    return ranking

