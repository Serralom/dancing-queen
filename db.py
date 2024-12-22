import sqlite3

DB_NAME = 'resultados.db'


# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            juego_queens INTEGER,
            juego_tango INTEGER
        )
    ''')
    conn.commit()
    conn.close()


# Función para guardar los resultados
def save_results(user_name, juego_queens, juego_tango):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO resultados (nombre, juego_queens, juego_tango)
        VALUES (?, ?, ?)
    ''', (user_name, juego_queens, juego_tango))
    conn.commit()
    conn.close()


# Función para obtener el ranking ordenado
def get_ranking():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT nombre, juego_queens, juego_tango FROM resultados ORDER BY juego_queens, juego_tango ASC")
    ranking = c.fetchall()
    conn.close()
    return ranking
