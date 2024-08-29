import requests

url = "http://localhost:11434/api/generate"

data = {
    "model": "tinyllama",
    "prompt": "Why is the sky blue?",
    "stream": False
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print("Response from Ollama: \n")
    value = response.json()
    print("The value type of response:", type(value))
    print(value["response"])
else:
    print(f"Error: {response.status_code} - {response.text}")
