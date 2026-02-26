import requests

api_key = "AIzaSyDYiZDepdqVUgkiZHVflEzO4aqu4JGVy3k"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
