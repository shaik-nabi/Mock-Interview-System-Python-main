import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

with open("gemini_output.txt", "w") as f:
    f.write(f"API Key: {api_key[:5]}...{api_key[-5:] if api_key else ''}\n")
    try:
        genai.configure(api_key=api_key)
        f.write("Listing models...\n")
        models = list(genai.list_models())
        for m in models:
            f.write(f"{m.name}\n")
            
        f.write("\nAttempting generation with gemini-1.5-flash...\n")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        f.write("Success!\n")
        f.write(response.text)
    except Exception as e:
        f.write(f"\nERROR: {e}\n")
