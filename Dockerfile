# app/Dockerfile

# FROM python:3.12-slim
FROM selenium/standalone-chrome:latest

WORKDIR /app

# # Instala dependências do sistema
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     software-properties-common \
#     git \
#     && rm -rf /var/lib/apt/lists/*


# # Instala as dependências do Chrome
# RUN apt-get update && apt-get install -y \
#     libgl1 \
#     libglib2.0-0 \
#     libxext6 \
#     libxrender1 \
#     xvfb \
#     xauth \
#     wget \
#     unzip

# # Instala o Chrome
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
#     dpkg -i google-chrome-stable_current_amd64.deb; apt-get install -f -y


# Remove a pasta antiga e clona o repositório
RUN git clone https://github.com/renatoeco/monitor_PLs.git .

# Instala as dependências do Python
RUN pip3 install -r requirements.txt

# Expõe a porta usada pelo Streamlit
EXPOSE 8501

# Healthcheck para monitorar o app
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Define a entrada do container
ENTRYPOINT ["streamlit", "run", "pls.py", "--server.port=8501", "--server.address=0.0.0.0"]
