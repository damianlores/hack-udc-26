import prompt
import database
import time

# --- Ejecución de prueba ---
if __name__ == "__main__":
    conn = database.init_database()
    
    # Simulación de recolección continua (ejecutar 3 veces)
    for _ in range(3):
        database.metric_register(conn)
        time.sleep(1)
    
    metrics = database.get_latest_metrics(conn)
    if metrics:
        cpu, ram, procesos = metrics
        print("\nIniciando análisis de IA con los últimos datos...")
        resultado_ia = prompt.resource_analyze(cpu, ram, procesos)
        print("\n--- Respuesta de IA ---")
        print(resultado_ia)
        
    conn.close()