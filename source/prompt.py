from openai import OpenAI
import os

def generate_response(prompt: str) -> str:
    """
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("Environment variable GROQ_API_KEY is not set.")
    """
    api_key="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"
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

def analyze_samples(context: str, samples: str) -> str:
    prompt = (
        f"Actúa como un experto en sistemas operativos, que quiere ayudar a un usuario a identificar posibles problemas de rendimiento."
        f"Es muy importante, ten en cuenta, que el usuario no sabe prácticamente nada, por tanto evita los tecnicismos."
        f"Además, sé breve, es un texto de unas líneas integrado en una interfaz de monitoreo, no un informe detallado."
        f"Del último análisis de procesos, has enviado la siguiente ayuda al usuario, utilízala como contexto para tu análisis:\n{context}\n"
        f"Ahora, con base en los siguientes samples de procesos (cada uno con su PID, nombre, uso de CPU y RAM), analiza brevemente si hay alguna" 
        f"tendencia preocupante o proceso que esté aumentando constantemente en uso de recursos:\n{samples}\n"
    )
    try:
        response = generate_response(prompt) 
        return response
    except Exception:
        return "No se pudo conectar con el analista de IA en este momento."
