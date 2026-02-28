import sqlite3

def conectar():
    conn = sqlite3.connect('historial_ia.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            app_name TEXT,
            cpu_uso REAL
        )
    ''')
    conn.commit()
    return conn

def guardar_dato(app, cpu):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO registros (app_name, cpu_uso) VALUES (?, ?)", (app, cpu))
    conn.commit()
    conn.close()

def obtener_historial(app):
    conn = conectar()
    cursor = conn.cursor()
    # Traemos los últimos 50 registros de esa app para la IA
    cursor.execute("SELECT cpu_uso FROM registros WHERE app_name = ? ORDER BY timestamp DESC LIMIT 50", (app,))
    datos = [fila[0] for fila in cursor.fetchall()]
    conn.close()
    return datos
