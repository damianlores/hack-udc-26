import psutil
import datetime
import time
from collections import deque
import datetime

def save_processes_data():
    # gets active processes with specific attributes
    attributes = ['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'create_time']
    active_processes = list(psutil.process_iter(attributes))
    
    # exclude processes that have terminated or are inaccessible
    for proc in active_processes:
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    # delay to allow CPU percent calculation
    time.sleep(1)
    
    processes = []
    
    for proc in active_processes:
        try:
            info = proc.info
            cpu_usage = proc.cpu_percent(interval=None)
            creation_time = datetime.datetime.fromtimestamp(info['create_time']).strftime("%Y-%m-%d %H:%M:%S")
            memoria_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0.0
            # save of process data in list
            processes.append({
                "pid": info['pid'],
                "name": info['name'],
                "cpu_percent": round(cpu_usage, 2),
                "mem_percent": round(info['memory_percent'], 2) if info['memory_percent'] else 0.0,
                "mem_mb": round(memoria_mb, 2),
                "creation_time": creation_time
            })
        # handle processes that have terminated or are inaccessible during data retrieval
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    # return sorted list of processes by CPU usage, limited to top 10
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]

def obtain_processes_data():
    # similar to save_process_data but without sleep time as it will be regularly called by thread of execution, so it needs to be non-blocking
    processes = []
    
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
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
            
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]

class ResourceHistoric:
    def __init__(self, capacity):
        # initializes a set of samples with a maximum capacity
        self.samples = deque(maxlen=capacity)
        self.capacity = capacity

    def save_sample(self, processes):
        # saves a sample (top 10 most CPU consuming processes) with a timestamp
        sample = {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "procesos": processes 
        }
        self.samples.append(sample)

    def is_ready(self):
        # checks if the historic has reached its capacity of samples
        return len(self.samples) == self.capacity

    def build_samples(self):
        # joins samples to be sent as a single string to  AI, then clears the samples to free memory
        text = f""
        for i, m in enumerate(self.samples):
            text += f"Sample {i+1}:\n"
            
            for p in m['procesos']:
                text += f" {p['name']} CPU {p['cpu_percent']}% RAM {p['mem_percent']}MB\n"
            # cleanup after building the text to avoid keeping old samples in memory
            self.samples.clear()
        return text