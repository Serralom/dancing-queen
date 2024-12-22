import sqlite3

# Conectar a la base de datos (esto la crea si no existe)
conn = sqlite3.connect('results.db')
c = conn.cursor()

# Crear la tabla si no existe
c.execute('''
CREATE TABLE IF NOT EXISTS resultados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    juego_queens REAL,
    juego_tango REAL
)
''')

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()
