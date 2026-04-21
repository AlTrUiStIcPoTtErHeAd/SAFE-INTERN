import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
else:
    genai.configure(api_key=api_key)
    print("Listing available models to models_list.txt...")
    try:
        with open("models_list.txt", "w") as f:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(f"{m.name}\n")
    except Exception as e:
        print(f"Error listing models: {e}")
