# Usar uma imagem oficial do Python como base
FROM python:3.9-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos do projeto para o container
COPY . /app

# Comando para rodar o script
CMD ["python", "proxy.py"]
