# app/Dockerfile

FROM python:3.12-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo requirements.txt
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta usada pelo Streamlit
EXPOSE 8501

# Healthcheck para monitorar o app
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Define a entrada do container
ENTRYPOINT ["streamlit", "run", "pls.py", "--server.port=8501", "--server.address=0.0.0.0"]






# FROM python:3.12-slim

# WORKDIR /app

# # Instala dependências do sistema
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     software-properties-common \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# # Clona o repositório
# RUN git clone https://github.com/renatoeco/monitor_PLs.git .

# # Instala as dependências do Python
# RUN pip3 install -r requirements.txt

# # Expõe a porta usada pelo Streamlit
# EXPOSE 8501

# # Healthcheck para monitorar o app
# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# # Define a entrada do container
# ENTRYPOINT ["streamlit", "run", "pls.py", "--server.port=8501", "--server.address=0.0.0.0"]
