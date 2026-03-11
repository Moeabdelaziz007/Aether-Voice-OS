import os
from google import genai
import sys

# Ensure validation
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key missing")
    sys.exit(1)
    
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})

print("Available Models:")
for model in client.models.list():
    print(f" - {model.name}")
