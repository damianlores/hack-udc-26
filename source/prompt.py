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

def resource_analyze(cpu, ram, procesos):
    prompt = (
        f"Actúa como un experto en sistemas operativos. "
        f"Estado actual: CPU al {cpu}%, RAM al {ram}%, y {procesos} procesos activos. "
        "Dime de forma breve (máximo 2 frases) si el consumo es normal o si "
        "hay algo sospechoso, y da un consejo práctico."
    )
    try:
        response = generate_response(prompt) 
        return response
    except Exception:
        return "No se pudo conectar con el analista de IA en este momento."
