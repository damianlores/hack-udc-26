import prompt
import time

if __name__ == "__main__":
    
    from resources import ResourceHistoric
    historic = ResourceHistoric(capacity=5)
    context = f"Por ahora no hay contexto previo, pues es el primer análisis."
    
    from resources import save_process_data
    from prompt import generate_response
        
    while True:
        # 1. Recopila los datos usando save_process_data
        processes = save_process_data()[:10]
            
        # 2. Almacena el sample actual
        historic.save_sample(processes)
            
        # 3. Solo pide el prompt si ya hay 5 samples
        if historic.is_ready():
            samples = historic.build_samples()
            context = prompt.analyze_samples(context, samples)
            
            print(context)
            
        time.sleep(1)