import sqlite3
import psutil
import time
from datetime import datetime

# === 1. CONFIGURACIÓN DE LA BASE DE DATOS ===
def iniciar_base_de_datos():
    # Crea el archivo 'historial_ia.db' si no existe
    conexion = sqlite3.connect('historial_ia.db')
    cursor = conexion.cursor()
    
    # Creamos la tabla con las 5 columnas que definimos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            app_name TEXT,
            cpu_uso REAL,
            ram_uso REAL,
            contexto TEXT
        )
    ''')
    conexion.commit()
    return conexion

# === 2. FUNCIÓN PARA GUARDAR UN DATO ===
def guardar_en_historial(conexion, app, cpu, ram, contexto):
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO historial (app_name, cpu_uso, ram_uso, contexto)
        VALUES (?, ?, ?, ?)
    ''', (app, cpu, ram, contexto))
    conexion.commit()

# === 3. FUNCIÓN DE LIMPIEZA (Para no saturar el disco) ===
def limpiar_datos_viejos(conexion):
    cursor = conexion.cursor()
    # Borra todo lo que tenga más de 7 días
    cursor.execute("DELETE FROM historial WHERE timestamp < datetime('now', '-7 days')")
    conexion.commit()
    print("Limpieza completada: Solo quedan los últimos 7 días.")

# === 4. EL VIGILANTE (Bucle principal) ===
def ejecutar_vigilancia():
    db = iniciar_base_de_datos()
    print("El detective está vigilando... Pulsa Ctrl+C para parar.")
    
    try:
        while True:
            # Detectar si estamos en batería o enchufe (Contexto)
            # Nota: psutil.sensors_battery() puede devolver None en algunos PCs de sobremesa
            bateria = psutil.sensors_battery()
            estado_energia = "Enchufado"
            if bateria and not bateria.power_plugged:
                estado_energia = "Batería"

            # Revisar los procesos abiertos
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    nombre = proc.info['name']
                    cpu = proc.info['cpu_percent']
                    ram = proc.info['memory_percent']

                    # Solo guardamos si la app está "haciendo algo" (> 1% CPU)
                    # Esto ahorra muchísimo espacio en disco
                    if cpu > 1.0:
                        guardar_en_historial(db, nombre, cpu, ram, estado_energia)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Una vez al día (o cada vez que arranques), limpiamos lo viejo
            limpiar_datos_viejos(db)

            # Esperar 10 segundos antes de la siguiente foto del sistema
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n Vigilancia detenida por el usuario.")
        db.close()

# Lanzar el proceso
if __name__ == "__main__":
    ejecutar_vigilancia()
