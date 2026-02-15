
import asyncio
import os
from dotenv import load_dotenv
from app.llm.profile_summary import generate_profile_summary
import google.generativeai as genai
from app.models.profile import RepositorySummary

load_dotenv(override=True)

async def test_llm():
    # Inline test with standard model
    model_name = "gemini-2.5-flash"
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"DEBUG: Key Prefix is {api_key[:10] if api_key else 'None'}")
    genai.configure(api_key=api_key)
    
    with open("verification_result.txt", "w", encoding="utf-8") as f:
        try:
            print(f"Trying {model_name} with new key...")
            model = genai.GenerativeModel(model_name)
            prompt = "Write a short summary."
            response = await model.generate_content_async(prompt)
            f.write(f"SUCCESS with {model_name}!\n")
            f.write(response.text)
            print(f"SUCCESS with {model_name}")
        except Exception as e:
            f.write(f"FAILED {model_name}: {e}\n")
            print(f"FAILED {model_name}: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
