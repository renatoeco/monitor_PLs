# app/Dockerfile

FROM python:3.12-slim

WORKDIR /Docker_Testes

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clona o repositório
RUN git clone https://github.com/renatoeco/monitor_PLs.git .

# Instala as dependências do Python
RUN pip3 install -r requirements.txt

# Expõe a porta usada pelo Streamlit
EXPOSE 8501

# Healthcheck para monitorar o app
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Define a entrada do container
ENTRYPOINT ["streamlit", "run", "pls.py", "--server.port=8501", "--server.address=0.0.0.0"]
