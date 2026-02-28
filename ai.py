from openai import OpenAI
import time
import os
from dotenv import load_dotenv


def generate_response(prompt: str, api_key: str) -> str:
    
    if not api_key:
        raise ValueError("Environment variable GROQ_API_KEY is not set.")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API execution failed: {str(e)}"

def analyze_samples(context: str, samples: str, api_key: str) -> str:
    prompt = (
        f"Eres un experto en sistemas operativos. Debes ayudar a un usuario a identificar posibles problemas de rendimiento con un análisis de datos\n"
        f"REGLAS DE ORO:\n"
        f"1. El usuario NO no sabe practicamente nada: NO uses tecnicismos\n"
        f"2. Sé breve: tu respuesta es un texto de unas líneas para ser integrado en una interfaz de monitoreo. No cabeceras u organizadores\n"
        f"3. NUNCA JAMAS menciones los samples, el usuario no debe saber que tipo de datos tienes\n"
        f"4. Si concluyes en comportamiento SOSPECHOSO, empieza con la palabra 'ALERTA:'\n"
        f"5. IMPORTANTE: un pico de uso de recurso NO es obligatoriamente sospechoso. Necesitas comprobar TODOS los samples y el contexto\n"
        f"Información adicional: contexto anterior para tu análisis: {context}\n"
        f"Estos son los samples:\n{samples}\n"
    )
    try:
        response = generate_response(prompt, api_key) 
        return response
    except Exception:
        return "No se pudo conectar con el analista de IA en este momento."

def get_advice():
    from resources import ResourceHistoric
    historic = ResourceHistoric(capacity=5)
    context = f"No hay contexto todavia"
    interval = 5  # seconds between samples
    
    from resources import save_process_data
        
    while True:
        # get top 10 most consuming processses data
        processes = save_process_data()[:10]
        
        # save info in the historic
        historic.save_sample(processes)
        
        if historic.is_ready():
            samples = f"Samples con intervalos de {interval}s, ordenados por uso de CPU:" + historic.build_samples()
            
            context = analyze_samples(context, samples)
            
            return context
            
        time.sleep(interval)