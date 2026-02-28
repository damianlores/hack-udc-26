import psutil
import datetime
import time

def obtain_process_data():

    attributes = ['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time', 'memory_info']
    active_processes = list(psutil.process_iter(attributes))
    
    for proc in active_processes:
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    time.sleep(0.5)
    
    processes = []
    
    for proc in active_processes:
        try:
            info = proc.info
            
            cpu_usage = proc.cpu_percent(interval=None) # / core_count
            
            creation_time = datetime.datetime.fromtimestamp(info['create_time']).strftime("%Y-%m-%d %H:%M:%S")
            
            memoria_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0.0
            
            processes.append({
                "pid": info['pid'],
                "nombre": info['name'],
                "cpu": round(cpu_usage, 2),
                "memoria_porcentaje": round(info['memory_percent'], 2) if info['memory_percent'] else 0.0,
                "memoria_mb": round(memoria_mb, 2),
                "fecha_creacion": creation_time
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Ordenar procesos por uso de CPU (mayor a menor)
    processes.sort(key=lambda x: x['cpu'], reverse=True)
            
    return processes

