"""
import psutil
import datetime
import time

def obtain_process_data():
    attributes = ['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'create_time']
    active_processes = list(psutil.process_iter(attributes))
    
    for proc in active_processes:
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    time.sleep(1)
    
    processes = []
    
    for proc in active_processes:
        try:
            info = proc.info
            
            cpu_usage = proc.cpu_percent(interval=None)
            
            creation_time = datetime.datetime.fromtimestamp(info['create_time']).strftime("%Y-%m-%d %H:%M:%S")
            
            memoria_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0.0
            
            processes.append({
                "pid": info['pid'],
                "name": info['name'],
                "cpu_percent": round(cpu_usage, 2),
                "mem_percent": round(info['memory_percent'], 2) if info['memory_percent'] else 0.0,
                "mem_mb": round(memoria_mb, 2),
                "creation_time": creation_time
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
    return processes
    """
import psutil

def obtain_process_data():
    """Retorna los 10 procesos con mayor consumo de CPU."""
    processes = []
    # Iteración sobre procesos activos con atributos específicos
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # interval=None evita el bloqueo del hilo de ejecución
            cpu = proc.info['cpu_percent'] or 0.0
            mem = proc.info['memory_percent'] or 0.0
            
            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": cpu,
                "mem_percent": round(mem, 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    # Ordenación descendente por uso de CPU
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]