import psutil
import datetime
import time
from collections import deque
import datetime

def save_process_data():
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


class ResourceHistoric:
    def __init__(self, capacity=5):
        # Mantiene el historial de muestreos
        self.samples = deque(maxlen=capacity)
        self.capacity = capacity

    def save_sample(self, processes):
        """Guarda los 10 procesos actuales en el historial."""
        sample = {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "procesos": processes 
        }
        self.samples.append(sample)

    def is_ready(self):
        """Verifica si ya tenemos los 5 samples requeridos."""
        return len(self.samples) == self.capacity

    def build_samples(self):
        """Genera el texto estructurado para el prompt."""
        text = f""
        for i, m in enumerate(self.samples):
            text += f"\nSample {i+1} [{m['timestamp']}]:\n"
            
            for p in m['procesos']:
                text += f"- {p['name']} (PID: {p['pid']}): CPU {p['cpu_percent']}%, RAM {p['mem_percent']}MB\n"
            # cleanup after building the text to avoid keeping old samples in memory
            self.samples = []
        return text


    #python class HistorialBloque: def __init__(self, capacidad=5): self.muestreos = [] ... def registrar(self, datos): # Guarda hasta 5 samples def limpiar(self): self.muestreos = [] # BORRA los datos


   
