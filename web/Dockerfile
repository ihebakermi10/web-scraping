FROM python:3.9.13
WORKDIR /web

# 1. Installer les dépendances globales
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copier le code Web
COPY web/ ./

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
