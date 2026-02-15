
import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

# Force UTF-8 for file writing to avoid Windows console encoding issues
def log(msg):
    with open("diagnostic_result.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

if os.path.exists("diagnostic_result.txt"):
    os.remove("diagnostic_result.txt")

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

log(f"API Key present: {bool(api_key)}")
if api_key:
    log(f"Key prefix: {api_key[:8]}...")

genai.configure(api_key=api_key)

CANDIDATES = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro-001",
    "gemini-pro"
]

log("\n--- Testing Model Candidates ---")

working_model = None

for model_name in CANDIDATES:
    log(f"\nTrying model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, can you hear me?")
        log(f"SUCCESS! Response: {response.text}")
        working_model = model_name
        break
    except Exception as e:
        log(f"FAILED: {type(e).__name__}")
        log(f"Error details: {str(e)}")

log("\n--- Conclusion ---")
if working_model:
    log(f"RECOMMENDATION: Use '{working_model}'")
else:
    log("CRITICAL: No working models found. Check API key permissions/quota.")
