import os
from dotenv import load_dotenv
from google.genai import Client

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = Client(api_key=API_KEY)

# Fetch available models
print("Fetching available models...")
models_list = client.models.list()  # new API
gemini_models = [m.name for m in models_list if "gemini" in m.name.lower()]

if not gemini_models:
    raise ValueError("No Gemini models found.")

model_name = gemini_models[0]
print(f"Using model: {model_name}")

question = "Who is the Prime Minister of India?"
response = client.models.generate_content(model=model_name, contents=question)

print("\nQuestion:", question)
print("Response:", response.text)