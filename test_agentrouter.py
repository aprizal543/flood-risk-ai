import os
import requests
import json

API_KEY = os.getenv("AGENTROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError("AGENTROUTER_API_KEY belum diset.")

url = "https://agentrouter.org/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "claude-opus-4-7",
    "messages": [
        {
            "role": "user",
            "content": "Hello"
        }
    ]
}

print("=" * 60)
print("Mengirim request...")
print("=" * 60)

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    print(f"Status Code : {response.status_code}")
    print()

    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(response.text)

except Exception as e:
    print("ERROR")
    print(e)