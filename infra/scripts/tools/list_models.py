import os

import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("Listing supported models:")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)
