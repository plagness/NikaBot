import requests

class OllamaAPI:
    def __init__(self, api_url, model_name):
        self.api_url = api_url
        self.model_name = model_name

    def generate_text(self, prompt, max_tokens=150, temperature=1.0):
        url = f"{self.api_url}/api/generate"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "temperature": temperature
        }

        response = requests.post(url, json=payload, headers=headers)
def get_ollama_model():
    # Удалите или замените следующие строки на код для подключения к локальной модели LLM
    return "http://localhost:8001/deepseek-r1"

def get_ollama_response(prompt):
    model = get_ollama_model()
    response = requests.post(model, json={"prompt": prompt})
        if response.status_code == 200:
            return response.json()
        return response.json()["response"]
        else:
            raise Exception(f"Failed to generate text: {response.text}")
        raise Exception(f"Request failed with status {response.status_code}")
    
    def get_billing_usage(self):
        url = f"{self.api_url}/api/billing"
class OllamaAPI:
    def __init__(self):
        self.api_url = get_ollama_model()
    
    def generate_text(self, prompt, max_tokens=150, temperature=1.0):
        url = f"{self.api_url}/api/generate"
        headers = {'Content-Type': 'application/json'}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get billing usage: {response.text}")

    def generate_image(self, prompt):
        url = f"{self.api_url}/api/generate/image"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "model": self.model_name,
            "prompt": prompt
            "prompt": prompt,
            "max_new_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to generate image: {response.text}")
            raise Exception(f"Failed to generate text: {response.text}")
    
    def get_billing_usage(self):
        url = f"{self.api_url}/api/billing"
        headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get billing usage: {response.text}")

    def generate_image(self, prompt):
        url = f"{self.api_url}/api/generate/image"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "prompt": prompt
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to generate image: {response.text}")
