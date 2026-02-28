import resources
import json
import time

if __name__ == "__main__":
    
    from resources import ResourceHistoric
    historial = ResourceHistoric(capacidad=5)
    
    
    from resources import save_process_data
    from prompt import generate_response
        
    while True:
        # 1. Recopila los datos usando save_process_data
        datos_completos = save_process_data()
        top_10 = datos_completos[:10]
            
        # 2. Almacena el sample actual
        historial.save_sample(top_10)
            
        analisis_ia = "Recopilando datos iniciales (Muestreo {}/5)...".format(len(historial.samples))
            
            # 3. Solo pide el prompt si ya hay 5 samples
        if historial.is_ready():
            prompt_input = historial.formatear_para_ia()
            print(prompt_input)
            instruccion = (
                f"Analiza estos 5 samples de procesos:\n{prompt_input}\n"
                "Determina si hay algún proceso cuya CPU o RAM esté aumentando constantemente. "
                "Responde brevemente."
            )
            print(generate_response(instruccion))
        
        time.sleep(1)