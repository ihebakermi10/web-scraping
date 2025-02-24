import requests

headers = {
    "Authorization": "Bearer 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"
}

response = requests.get("https://api.openai.com/v1/models", headers=headers)
print(response.json())
