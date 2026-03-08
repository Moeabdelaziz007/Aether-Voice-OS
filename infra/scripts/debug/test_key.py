import os

try:
    import requests
except ImportError:
    print(
        "Error: 'requests' library not installed. "
        "Please install it with 'pip install requests'."
    )
    exit(1)

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # If dotenv is not installed, we continue and rely on environment \
    # variables being set manually
    pass

api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
