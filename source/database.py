import sqlite3
import psutil
import time

DB_NAME = "system_resources.db"

def init_database():
    """
    Creates the SQLite database and the necessary table if it doesn't exist.
    Executes at application startup.
    """
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metric_historic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_global REAL,
            ram_global REAL,
            total_procesos INTEGER
        )
    ''')
    conexion.commit()
    return conexion

def metric_register(conexion):
    """
    Collects current system metrics and inserts them into the database.
    """
    # Recolección de datos
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    procesos = len(psutil.pids())
    
    # Inserción en SQLite
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO historico_metricas (cpu_global, ram_global, total_procesos)
        VALUES (?, ?, ?)
    ''', (cpu, ram, procesos))
    
    conexion.commit()
    print(f"Registro guardado: CPU {cpu}% | RAM {ram}% | Procesos {procesos}")

# --- Ejecución de prueba ---
if __name__ == "__main__":
    conn = inicializar_base_datos()
    
    # Simulación de recolección continua (ejecutar 3 veces)
    for _ in range(3):
        registrar_metricas(conn)
        time.sleep(1)
        
    conn.close()