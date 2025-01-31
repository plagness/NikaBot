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
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": False  # Если вам нужен стриминг, обновите это значение
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '')
        else:
            raise Exception(f"Ошибка при генерации текста: {response.text}")

    def generate_image(self, prompt):
        url = f"{self.api_url}/api/generate/image"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "model": self.model_name,
            "prompt": prompt
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data  # Предполагается, что ответ содержит изображение в base64 или ссылку
        else:
            raise Exception(f"Ошибка при генерации изображения: {response.text}")

    def get_billing_usage(self):
        url = f"{self.api_url}/api/billing"
        headers = {'Content-Type': 'application/json'}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Ошибка при получении информации о биллинге: {response.text}")