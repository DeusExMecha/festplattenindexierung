import requests
import json

r = requests.get('http://localhost:1234/v1/models', timeout=5)
models = r.json()['data']
model_id = models[0]['id']
print(f'Modell: {model_id}')

payload = {
    'model': model_id,
    'messages': [{'role': 'user', 'content': 'Sag Hallo in einem Satz'}],
    'temperature': 0.4
}

resp = requests.post('http://localhost:1234/v1/chat/completions', json=payload, timeout=60)
print(f'Status: {resp.status_code}')
data = resp.json()
print(json.dumps(data, indent=2, ensure_ascii=False)[:800])