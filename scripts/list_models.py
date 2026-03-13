import os
from google import genai

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"), http_options={"api_version": "v1beta"})

print("Listing models for v1beta...")
try:
    for model in client.models.list():
        print(f" - {model.name}")
except Exception as e:
    print(f"Error listing models for v1beta: {e}")

print("\nListing models for v1alpha...")
client_alpha = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"), http_options={"api_version": "v1alpha"})
try:
    for model in client_alpha.models.list():
        print(f" - {model.name}")
except Exception as e:
    print(f"Error listing models for v1alpha: {e}")
