import prompt
from database import init_database, metric_register, get_latest_metrics
import time

# --- Ejecución de prueba ---
if __name__ == "__main__":
    conn = init_database()
    
    # Simulación de recolección continua (ejecutar 3 veces)
    for _ in range(3):
        metric_register(conn)
        time.sleep(1)
    
    metrics = get_latest_metrics(conn)
    if metrics:
        cpu, ram, procesos = metrics
        print("\nIniciando análisis de IA con los últimos datos...")
        resultado_ia = analize_resource_usage(cpu, ram, procesos)
        print("\n--- Respuesta de IA ---")
        print(resultado_ia)
        
    conn.close()