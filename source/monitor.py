import psutil
import time
import database

def iniciar_vigilancia():
    print("🕵️ Vigilante iniciado en segundo plano...")
    while True:
        # Buscamos los procesos que más consumen
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            try:
                nombre = proc.info['name']
                cpu = proc.info['cpu_percent']
                
                # Solo nos interesan apps con actividad (> 1%)
                if cpu > 1.0:
                    database.guardar_dato(nombre, cpu)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Cada 5 segundos tomamos una muestra
        time.sleep(5)

if __name__ == "__main__":
    iniciar_vigilancia()
