import requests

from config import apikey

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {apikey}",
    "Content-Type": "application/json"
}
data = {
    "model": "llama3-70b-8192",
    "messages": [{"role": "user", "content": "Write a short story about a space cat."}],
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)
print(response.json()["choices"][0]["message"]["content"])

