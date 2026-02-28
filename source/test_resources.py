import resources

if __name__ == "__main__":
    datos = resources.obtain_process_data()
    
    # Filtrar opcionalmente aquellos con 0.0% de CPU para omitir overhead nulo
    procesos_relevantes = [p for p in datos if p['cpu'] > 0.0]
    
    for d in datos[:10]: # Muestra el Top 10
        print(f"PID: {d['pid']} | {d['nombre']} | CPU: {d['cpu']}% | Mem: {d['memoria_mb']} MB ({d['memoria_porcentaje']}%)")