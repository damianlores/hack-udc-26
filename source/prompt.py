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
        response = client.responses.create(
            input=prompt,
            model="llama-3.3-70b-versatile",
        )
        return response.output_text
    except Exception as e:
        return f"API execution failed: {str(e)}"
    
