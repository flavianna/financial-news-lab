import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("MAKE_WEBHOOK_URL")

with open("boletim.json", "r", encoding="utf-8") as arquivo:
    boletim = json.load(arquivo)

resposta = requests.post(url, json=boletim, timeout=30)

print(resposta.status_code)
print(resposta.text)
