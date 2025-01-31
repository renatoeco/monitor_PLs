# app/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências do Chrome e WebDriver
RUN apt-get install -y \
    wget unzip gnupg libgconf-2-4 libnss3 libxss1 libappindicator1 libindicator7 \
    fonts-liberation xdg-utils libgbm1 libasound2 libu2f-udev

# Baixa e instala o Google Chrome
RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get install -y google-chrome-stable

# Define variáveis de ambiente para o Chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_BIN=/root/.wdm/drivers/chromedriver/linux64/latest/chromedriver

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
