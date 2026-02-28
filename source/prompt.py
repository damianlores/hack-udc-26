from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)

import os

def generate_gemini_response(prompt: str, model_name: str = "gemini-1.5-pro") -> str:
    """
    Passes a string prompt to the Gemini API and returns the text response.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Environment variable GEMINI_API_KEY is not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"API execution failed: {str(e)}"