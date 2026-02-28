import prompt
import time

if __name__ == "__main__":
    
    from resources import ResourceHistoric
    historic = ResourceHistoric(capacity=5)
    context = f"No hay contexto todavia"
    interval = 5  # seconds between samples
    
    from resources import save_process_data
    from prompt import generate_response
        
    while True:
        # get top 10 most consuming processses data
        processes = save_process_data()[:10]
        
        # save info in the historic
        historic.save_sample(processes)
        
        if historic.is_ready():
            samples = f"Samples con intervalos de {interval}s, ordenados por uso de CPU:" + historic.build_samples()
            
            context = prompt.analyze_samples(context, samples)
            print(context)
            
        time.sleep(interval)