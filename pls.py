import pandas as pd
import streamlit as st
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import time


# comparar o número da proposição para achar os erros PL/Link

# def raspar_camara():
#     instruções

# def raspar senado():
#     instruções

# cria o dataframe vazio com a estruta final: Tema Sub-Tema	Proposições	Ementa	Casa	Autor	UF	Partido	Apresentação	Data da Situação   Situação	 Link    

# for que percorre todo o dataframe
#     se no link contiver "camara.leg.br" entao ele vai para a funcao camara

#         casa = 'Câmara Federal'

#     se no link contiver "senado.leg.br" entao ele vai para a funcao senado

#         casa = 'Senado Federal'

# Nível 1 de apresentação:        
# exportar o xls com tudo atualizado


# Nível 2 de apresentação:

# salvar o df em um banco de dados

# quando percorrer, encontrar aquele link no BD, comparar a situação do BD com a situação raspada, se for diferente, mostrar na tela quem teve andamento.
    




# Configuração do Chromium
opcoes = Options()
opcoes.binary_location = '/usr/bin/chromium-browser'
opcoes.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
opcoes.add_argument('--start-maximized')  # Adiciona a opção para maximizar a janela

# Configuração do serviço do Chromium WebDriver
servico = ChromiumService('/usr/lib/chromium-browser/chromedriver')
navegador = webdriver.Chrome(service=servico, options=opcoes)


# ///////////////////////////////////////////////////



# criar um dataframe a partir do csv de links
df_pls = pd.read_csv('dados/lista_pls.csv', sep=',')

st.write('Meu dataframe')
st.write(df_pls)

    



try:

    for i, linha in df_pls.iterrows():

        
        navegador.get(linha['Link'])
        

        # Aguarde o carregamento do conteúdo (se necessário)
        time.sleep(2)  # Ajuste o tempo conforme necessário

        # Localizar o número da proposição
        numero_pl_raspado = navegador.find_element(By.CSS_SELECTOR, "h3 > span.nomeProposicao").text
       
        st.write(numero_pl_raspado)



# fazer essa conferência antes de tudo
        if numero_pl_raspado == linha['Proposições']:
            st.write('igual')
        else:
            st.write('diferente')

        



finally:

    # Fechar o navegador
    navegador.quit()

