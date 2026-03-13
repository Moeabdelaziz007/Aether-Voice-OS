import os

from google import genai

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"), http_options={"api_version": "v1beta"})

print("Listing models for v1beta with full details...")
try:
    for model in client.models.list():
        if "flash" in model.name.lower():
            # Convert to dict to see all fields
            model_dict = model.model_dump()
            print(f" - {model.name}: {model_dict.get('supported_generation_methods')}")
except Exception as e:
    print(f"Error: {e}")
