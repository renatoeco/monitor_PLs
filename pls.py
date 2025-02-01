import pandas as pd
import streamlit as st
from pymongo import MongoClient
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager  # Automatiza a configuração do ChromeDriver
import time
from datetime import datetime, timedelta
import os


# ###################################################################################################
# CONFIGURAÇÕES INICIAIS
# ###################################################################################################

# Configurações do Streamlit
st.set_page_config(layout="wide")
# Set nome do app
st.set_page_config(page_title="Harpia - ISPN")



# Adiciona um estilo CSS para mudar a cor da barra lateral (sidebar) no Streamlit
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
    </style>
    """,
    unsafe_allow_html=True  # Permite o uso de HTML não seguro para customizar o layout
)

# Criação de um DataFrame vazio com as colunas finais desejadas, que serão preenchidas mais tarde
colunas = ['Tema', 'Sub-Tema', 'Proposições', 'Ementa', 'Casa', 'Autor', 'UF', 'Partido',
        'Apresentação', 'Situação', 'Data da Última Ação Legislativa', 'Última Ação Legislativa', 'Link']
df_final = pd.DataFrame(columns=colunas)  # Cria o DataFrame com as colunas definidas

# Configuração do Selenium
opcoes = Options()
# opcoes.add_argument('--start-maximized')  # Descomentando essa linha, o navegador abriria maximizado
opcoes.add_argument("--headless")  # Modo headless
opcoes.add_argument("--no-sandbox")
opcoes.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória
opcoes.add_argument("--disable-gpu")  # Desabilita a GPU
opcoes.add_argument("--disable-software-rasterizer")  # Desabilita o rasterizador de software
opcoes.add_argument("--disable-extensions")  # Desabilita extensões
opcoes.add_argument("--disable-background-networking")  # Desabilita networking em segundo plano
opcoes.add_argument("--disable-background-timer-throttling")
opcoes.add_argument("--disable-backgrounding-occluded-windows")
opcoes.add_argument("--disable-breakpad")
opcoes.add_argument("--disable-component-update")
opcoes.add_argument("--disable-default-apps")
opcoes.add_argument("--disable-domain-reliability")
opcoes.add_argument("--disable-features=AudioServiceOutOfProcess")
opcoes.add_argument("--disable-hang-monitor")
opcoes.add_argument("--disable-ipc-flooding-protection")
opcoes.add_argument("--disable-popup-blocking")
opcoes.add_argument("--disable-prompt-on-repost")
opcoes.add_argument("--disable-renderer-backgrounding")
opcoes.add_argument("--disable-sync")
opcoes.add_argument("--force-color-profile=srgb")
opcoes.add_argument("--metrics-recording-only")
opcoes.add_argument("--safebrowsing-disable-auto-update")
opcoes.add_argument("--enable-automation")
opcoes.add_argument("--password-store=basic")
opcoes.add_argument("--use-mock-keychain")



# ###################################################################################################
# FUNÇÕES AUXILIARES
# ###################################################################################################

# Função para ajustar a altura do dataframe automaticamente no Streamlit
def ajustar_altura_dataframe(df_nao_atualizado, linhas_adicionais=0, use_container_width=True, hide_index=True, column_config={
        "Link": st.column_config.Column(
            # label="Link",
            width="medium"  # Ajusta a largura da coluna "Link", pode ser alterado para "100px" ou outros valores
        ),
        "Data da Última Ação Legislativa": st.column_config.Column(
            label="Última ação",  # Ajusta o nome da coluna para "Última ação"
            # width="medium"  # Ajusta a largura da coluna, pode ser configurado para "100px" ou outros valores
        )
    }):
    """
    Ajusta a altura da exibição de um DataFrame no Streamlit com base no número de linhas e outros parâmetros.
    
    Args:
        df_nao_atualizado (pd.DataFrame): O DataFrame a ser exibido.
        linhas_adicionais (int): Número adicional de linhas para ajustar a altura. (padrão é 0)
        use_container_width (bool): Se True, usa a largura do container. (padrão é True)
        hide_index (bool): Se True, oculta o índice do DataFrame. (padrão é True)
        column_config (dict): Configurações adicionais das colunas, se necessário. (padrão é None)
    """
    
    # Define a altura em pixels de cada linha
    altura_por_linha = 35  
    # Calcula a altura total necessária para exibir o DataFrame, considerando as linhas adicionais e uma margem extra
    altura_total = ((df_nao_atualizado.shape[0] + linhas_adicionais) * altura_por_linha) + 2
    
    # Exibe o DataFrame no Streamlit com a altura ajustada
    st.dataframe(
        df_nao_atualizado,
        height=altura_total,  # Define a altura do DataFrame no Streamlit
        use_container_width=use_container_width,  # Define se deve usar a largura do container
        hide_index=hide_index,  # Define se o índice do DataFrame deve ser oculto
        column_config=column_config  # Configurações adicionais para as colunas, como largura personalizada
    )


# Função para excluir um item da coleção
def excluir_pls(numero_pl):
    # Exclui um item com o número da proposição fornecido
    colecao.delete_one({"Proposições": numero_pl})

    # Exibe uma mensagem de sucesso
    st.success(f"{numero_pl} excluído com sucesso!")  

    # Aguarda 3 segundos antes de reiniciar o aplicativo Streamlit
    time.sleep(3)
    # Recarrega o app
    st.rerun()  


# Inicializa a flag para controlar o acesso à Câmara
acessa_camara_foi_acessado = False

# Função para acessar links da Câmara e extrair informações sobre a proposição
def acessa_links_camara(link, tema, sub_tema):
    # Variável global para controlar se o link foi acessado
    global acessa_camara_foi_acessado
    
    # Acessa o link da proposição no navegador (utilizando o Selenium)
    navegador.get(link)
    # Aguarda 2 segundos para garantir que a página carregue completamente
    time.sleep(2)  
    
    # Extrai o número da proposição da página HTML
    numero_proposicao = navegador.find_element(By.CSS_SELECTOR, "h3 > span.nomeProposicao").text
    
    # Extrai a ementa (resumo) da proposição
    ementa = navegador.find_element(By.CSS_SELECTOR, "p > span.textoJustificado").text
    
    # Extrai informações sobre o autor, UF (Unidade Federativa) e partido
    autor_uf_e_partido = navegador.find_element(By.CSS_SELECTOR, "p#colunaPrimeiroAutor").text
    autor_uf_e_partido = autor_uf_e_partido.replace("Autor\n", "").strip()

    # Processa o formato das informações do autor, partido e UF
    if autor_uf_e_partido.count(" - ") == 1 and "/" in autor_uf_e_partido:
        # Formato "Zé Vitor - PL/MG"
        partes = autor_uf_e_partido.split(" - ")
        nome_deputado = partes[0].strip()  # Nome do deputado
        partido_uf = partes[1].split("/")  # Parte que contém partido e UF
        partido = partido_uf[0].strip() if len(partido_uf) > 0 else "Não disponível"
        uf = partido_uf[1].strip() if len(partido_uf) > 1 else "Não disponível"
    
    elif autor_uf_e_partido.count(" - ") == 2 and "/" in autor_uf_e_partido:
        # Formato "Senado Federal - Antonio Russo - PR/MS"
        partes = autor_uf_e_partido.split(" - ")
        nome_deputado = partes[1].strip()  # Nome do deputado
        partido_uf = partes[2].split("/")  # Parte que contém partido e UF
        partido = partido_uf[0].strip() if len(partido_uf) > 0 else "Não disponível"
        uf = partido_uf[1].strip() if len(partido_uf) > 1 else "Não disponível"
    
    elif "Senado Federal -" in autor_uf_e_partido:
        # Formato "Senado Federal - Comissão de Meio Ambiente"
        nome_deputado = autor_uf_e_partido.split(" - ")[1].strip()
        partido = "Não disponível"
        uf = "Não disponível"
        
    else:
        # Caso seja "Poder Executivo" ou "Comissão"
        nome_deputado = autor_uf_e_partido
        partido = "Não disponível"
        uf = "Não disponível"

    # Extrai a data de apresentação da proposição
    data_da_apresentacao = navegador.find_element(By.CLASS_NAME, "col-md-3").find_element(By.TAG_NAME, "p")
    # Pega a data da segunda linha do texto
    apresentacao = data_da_apresentacao.text.split('\n')[1]  

    # Localiza o <tbody> da tabela de trâmites legislativos e extrai a última ação
    tbody = navegador.find_element(By.CSS_SELECTOR, "div#tramitacoes table tbody")
    trs = tbody.find_elements(By.TAG_NAME, "tr")
    # Pega o último <tr> que contém a última ação legislativa
    ultimo_tr = trs[-1]  
    
    # Localiza o <td> com a data da última ação
    ultimo_td = ultimo_tr.find_element(By.TAG_NAME, "td")  
    # Obtém a data da última ação
    data_da_ultima_acao_legislativa = ultimo_td.text  
    
    # Localiza todos os <td> com a classe "textoJustificado"
    elementos_td = navegador.find_elements(By.CSS_SELECTOR, "td.textoJustificado")  
    ultimo_td = elementos_td[-1]  # Pega o último <td>
    # Localiza o <ul> com a última ação
    ul_element = ultimo_td.find_element(By.CSS_SELECTOR, "ul.ulTabelaTramitacoes")  
    # Obtém o texto da última ação legislativa
    ultima_acao_legislativa = ul_element.text  
    
    # Tenta localizar a situação da proposição
    try:
        situacao = navegador.find_element(By.CSS_SELECTOR, "div#subSecaoSituacaoOrigemAcessoria p span").text
    except Exception:
        try:
            # Caso não encontre o <span>, tenta localizar um <a> dentro do <p>
            situacao = navegador.find_element(By.CSS_SELECTOR, "div#subSecaoSituacaoOrigemAcessoria p a").text
        except Exception:
            # Caso não encontre nenhum dos dois, define como "Não disponível"
            situacao = "Não disponível"  
    
    # Cria um dicionário com todas as informações extraídas da proposição
    dados = {
        'Tema': tema,
        'Sub-Tema': sub_tema,
        'Proposições': numero_proposicao,
        'Ementa': ementa,
        'Casa': 'Câmara dos Deputados',
        'Autor': nome_deputado,
        'UF': uf,
        'Partido': partido,
        'Apresentação': apresentacao,
        'Situação': situacao,
        'Data da Última Ação Legislativa': data_da_ultima_acao_legislativa,
        'Última Ação Legislativa': ultima_acao_legislativa,
        'Link': link,
    }
    
    # Adiciona ao banco de dados MongoDB apenas se o número da proposição não existir
    if not colecao.find_one({"Proposições": numero_proposicao}):
        colecao.insert_one(dados)

    # Adiciona os dados extraídos ao DataFrame global `df_final`
    global df_final
    df_final = pd.concat([df_final, pd.DataFrame([dados])], ignore_index=True)
    
    # Marca que a Câmara foi acessada
    acessa_camara_foi_acessado = True

# Função para abrir o navegador Chrome utilizando o WebDriver
def abrir_navegador():
    # Define a variável global 'navegador' para que possa ser acessada em outras funções
    global navegador  
    # Inicia o navegador Chrome com as opções configuradas
    navegador = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opcoes)
    #navegador.get("https://www.google.com")  # Exemplo: abre o Google


# Flag para verificar se o Senado foi acessado
acessa_senado_foi_acessado = False

# Função para lidar com links do Senado e coletar informações sobre as proposições
def acessa_links_senado(link, tema, sub_tema):
    
    # Variável global que controla se o Senado foi acessado
    global acessa_senado_foi_acessado
    
    # Acessa o link da proposição no navegador
    navegador.get(link)
    # Aguarda 2 segundos para garantir que a página carregue completamente
    time.sleep(2)  
    
    try:
        # Extrai o número da proposição
        numero_proposicao = navegador.find_element(By.CSS_SELECTOR, "ul > li.active.last.breadcrumb-truncate").text

        # Extrai a ementa da proposição
        ementa = navegador.find_element(By.XPATH, "//p[strong[contains(text(),'Ementa:')]]/span").text

        # Extrai informações sobre o autor, partido e UF
        autor_uf_e_partido_senado = navegador.find_element(By.XPATH, "//p[strong[contains(text(),'Autoria:')]]/span").text
        # Remove as palavras "Senador" e "Deputado Federal"
        autor_uf_e_partido_senado = autor_uf_e_partido_senado.replace("Senador", "").replace("Deputado Federal", "").strip()

        # Verifica e extrai o nome, partido e UF caso o formato seja "Senador Fulano (PL/MT)"
        if "(" in autor_uf_e_partido_senado and "/" in autor_uf_e_partido_senado:
            nome_senador = autor_uf_e_partido_senado.split(" (")[0].strip()  # Pega o nome antes do "("
            partido_uf_senado = autor_uf_e_partido_senado.split(" (")[1].replace(")", "")  # Pega o texto entre "(" e ")"
            partido, uf_senado = partido_uf_senado.split("/")  # Divide o texto por "/"
            partido = partido.strip()
            uf_senado = uf_senado.strip()

        else:
            # Caso o formato não seja reconhecido, assume que as informações não estão disponíveis
            nome_senador = autor_uf_e_partido_senado
            partido = "Não disponível"
            uf_senado = "Não disponível"

        # Script para extrair a data de apresentação da proposição
        script_apresentacao = """
        var resultado = null;
        var dlElements = document.querySelectorAll('dl.dl-horizontal.tramitacao-lista__sem_margem.sf-lista-tramitacao-item--borda__plenario');
        var ultimaDl = dlElements[dlElements.length - 1];
        var dts = ultimaDl.querySelectorAll('dt');
        for (var j = 0; j < dts.length; j++) {
            if (dts[j].textContent.trim() === '1ª autuação' && j + 1 < dts.length) {
                resultado = dts[j + 1].textContent.trim();
                return resultado;
            }
            if (dts[j].textContent.trim() === '2ª autuação' && j + 1 < dts.length) {
                resultado = dts[j + 1].textContent.trim();
                return resultado;
            }
        }
        var firstDate = ultimaDl.querySelector('dt');
        if (firstDate) {
            resultado = firstDate.textContent.trim();
        }
        return resultado || "Texto não encontrado ou elemento vazio";
        """
        # Executa o script para obter a data de apresentação
        apresentacao = navegador.execute_script(script_apresentacao)
        if not apresentacao:
            apresentacao = "Texto não encontrado ou elemento vazio"

        # Script para capturar a última situação e o estado da proposição
        script_situacao_e_data = """
        let situacao_final = null;
        document.querySelectorAll('dl.dl-horizontal dt').forEach((dt) => {
            if (dt.textContent.trim() === 'Último estado:') {
                situacao_final = dt.nextElementSibling.textContent.trim();
            }
        });
        if (!situacao_final) {
            document.querySelectorAll('dl.dl-horizontal dd strong').forEach((strong) => {
                if (strong.textContent.trim() === 'Última situação:') {
                    situacao_final = strong.nextElementSibling.textContent.trim();
                }
            });
        }
        return situacao_final || "Situação não encontrada";
        """
        # Executa o script para obter a situação e a data da última ação
        situacao_bruta = navegador.execute_script(script_situacao_e_data)

        # Divide a situação e a data da última ação (se presente)
        if " - " in situacao_bruta:
            data, situacao = situacao_bruta.rsplit(" - ", 1)  # Divide a string no último " - "
            data_da_ultima_acao_legislativa = data.strip()
            situacao = situacao.strip().capitalize()  # Capitaliza a primeira letra da situação
        else:
            data, situacao = None, situacao_bruta.strip()

        # Script para extrair a última ação legislativa
        script_ultima_acao_legislativ = """
        var divs = document.querySelectorAll(
            'div[data-local="OUTROS"] dl.dl-horizontal.tramitacao-lista__sem_margem, ' +
            'div[data-local="COMISSOES"] dl.dl-horizontal.tramitacao-lista__sem_margem, ' +
            'div[data-local="PLENARIO"] dl.dl-horizontal.tramitacao-lista__sem_margem'
        );
        for (var i = 0; i < divs.length; i++) {
            var div = divs[i];
            var dts = div.querySelectorAll('dt');
            for (var j = 0; j < dts.length; j++) {
                if (dts[j].textContent.trim() === 'Ação:') {
                    return dts[j].nextElementSibling.textContent.trim();
                }
            }
        }
        return "Nenhuma seção com 'Ação:' encontrada";
        """
        # Executa o script para obter a última ação legislativa
        ultima_acao_legislativa = navegador.execute_script(script_ultima_acao_legislativ)
        
        # Cria um dicionário com os dados coletados
        dados = {
            'Tema': tema,  
            'Sub-Tema': sub_tema,  
            'Proposições': numero_proposicao,
            'Ementa': ementa,  
            'Casa': 'Senado Federal',
            'Autor': nome_senador,  
            'UF': uf_senado,  
            'Partido': partido,  
            'Apresentação': apresentacao, 
            'Situação': situacao, 
            'Data da Última Ação Legislativa': data_da_ultima_acao_legislativa,  
            'Última Ação Legislativa': ultima_acao_legislativa,  
            'Link': link ,
        }
    
        # Adiciona os dados ao banco de dados MongoDB apenas se o número da proposição não existir
        if not colecao.find_one({"Proposições": numero_proposicao}):
            colecao.insert_one(dados)

        # Adiciona os dados extraídos ao DataFrame global
        global df_final
        df_final = pd.concat([df_final, pd.DataFrame([dados])], ignore_index=True)
        
        # Marca que o Senado foi acessado
        acessa_senado_foi_acessado = True

    except Exception as e:
        # Exibe uma mensagem de erro caso ocorra algum problema
        st.error(f"Erro ao processar link do Senado: {e}")

# Função para verificar atualizações entre o DataFrame e o banco de dados MongoDB
def verificar_atualizacoes(df, colecao):
    # Lista para armazenar as alterações detectadas
    alteracoes_detectadas = []  
    # Flag para verificar se houve alguma alteração
    nenhuma_alteracao = True  

    # Itera sobre cada linha do DataFrame
    for index, row in df.iterrows():
        # Busca o registro correspondente no MongoDB usando o 'Link' como identificador
        registro_mongo = colecao.find_one({"Link": row['Link']})
        
        if registro_mongo:  # Caso o registro seja encontrado no MongoDB
            # Dicionário para armazenar as alterações
            alteracoes = {}  

            # Verifica as alterações para campos específicos
            for campo in ['Situação', 'Data da Última Ação Legislativa', 'Última Ação Legislativa']:
                if registro_mongo.get(campo) != row[campo]:  # Se o valor no MongoDB for diferente do DataFrame
                    alteracoes[campo] = {
                        "Antes": registro_mongo.get(campo, "(N/A)"),  # Valor anterior (do MongoDB)
                        "Depois": row[campo]  # Valor novo (do DataFrame)
                    }

            # Se houver alterações detectadas, adiciona na lista de alterações
            if alteracoes:
                alteracoes_detectadas.append({
                    "Tema": row['Tema'],
                    "Sub-Tema": row['Sub-Tema'],
                    "Casa": row['Casa'],
                    "Autor": row['Autor'],
                    "UF": row['UF'],
                    "Partido": row['Partido'],
                    "Apresentação": row['Apresentação'],
                    "Situação": row['Situação'],
                    "Data da Última Ação Legislativa": row['Data da Última Ação Legislativa'],
                    "Última Ação Legislativa": row['Última Ação Legislativa'],
                    "Link": row['Link'],
                    "Proposições": row['Proposições'],
                    "Ementa": row['Ementa'],  
                    "Alteracoes": alteracoes
                })

                # Atualiza os dados no MongoDB com os novos valores
                colecao.update_one({"Link": row['Link']}, {"$set": {k: v["Depois"] for k, v in alteracoes.items()}})

                # Marca que houve alterações
                nenhuma_alteracao = False

        else:  # Se o registro não for encontrado no MongoDB
                st.write(f"Registro com Link {row['Link']} não encontrado no banco de dados.")

    # Mensagem de verificação concluída
    st.success("Verificação concluída.", icon=":material/check_circle:")

    # Exibe um aviso se nenhuma alteração foi detectada
    if nenhuma_alteracao:
        resultado_comparacao.warning('Nenhuma proposição teve andamento desde a ultima verificação.')

    # Salva as alterações detectadas no estado da sessão
    st.session_state["alteracoes"] = alteracoes_detectadas


# Função para exibir as alterações detectadas
def exibir_alteracoes():
    # Verifica se há alterações para exibir
    if "alteracoes" in st.session_state:

        st.subheader(f"{len(st.session_state['alteracoes'])} atualizações desde a última verificação.")

        # Itera sobre as alterações detectadas e exibe os detalhes
        for alteracao in st.session_state["alteracoes"]:
            # Exibe as informações gerais sobre a alteração
            resultado_comparacao.subheader(alteracao['Proposições'])
            # Exibe a ementa da proposição
            resultado_comparacao.write(f"**Ementa**: {alteracao['Ementa']}")

            # Cria duas colunas para exibir os valores 'Antes' e 'Depois'
            col1, col2 = resultado_comparacao.columns(2)  
            col1.markdown("### Antes:")  # Cabeçalho para a coluna 'Antes'
            col2.markdown("### Depois:")  # Cabeçalho para a coluna 'Depois'
            
            # Exibe os valores anteriores e posteriores para cada campo alterado
            for campo, valores in alteracao["Alteracoes"].items():
                col1.write(f"{campo}: **{valores['Antes']}**")
                col2.write(f"{campo}: **{valores['Depois']}**")

            # Exibe um popover com mais detalhes sobre a alteração
            with resultado_comparacao.popover("Ver detalhes", icon=":material/info:"):

                # Exibe um link para a proposição e outros detalhes
                st.markdown(f'**Link do PL:** <a href="{alteracao["Link"]}" target="_blank">clique aqui</a>', unsafe_allow_html=True)
                st.markdown(f"**Tema**: {alteracao['Tema']}")
                st.markdown(f"**Sub-Tema**: {alteracao['Sub-Tema']}")
                st.markdown(f"**Ementa**: {alteracao['Ementa']}")
                st.markdown(f"**Casa**: {alteracao['Casa']}")
                st.markdown(f"**Autor**: {alteracao['Autor']}")
                st.markdown(f"**UF**: {alteracao['UF']}")
                st.markdown(f"**Partido**: {alteracao['Partido']}")
                st.markdown(f"**Data de apresentação**: {alteracao['Apresentação']}")
                st.markdown(f"**Situação**: {alteracao['Situação']}")
                st.markdown(f"**Data da Última Ação Legislativa**: {alteracao['Data da Última Ação Legislativa']}")
                st.markdown(f"**Última Ação Legislativa**: {alteracao['Última Ação Legislativa']}")

            # Adiciona um divisor entre as alterações
            resultado_comparacao.divider()

    else:
        # Exibe uma mensagem caso nenhuma alteração tenha sido detectada
        resultado_comparacao.write("Nenhuma alteração detectada.")



# ###################################################################################################
# CONEXÃO MONGO DB
# ###################################################################################################

# # CONEXÃO NO DOCKER --------------------------------------------------------------------------------------------------------------

# String de conexão do mongo atlas está na variável de ambiente do container. Precisa ser declarada no comando de run do container.
# Exemplo: docker run -e MONGO_ATLAS_STRING_CONEXAO="<minha string>" --name <nome do container> -p 8501:8501 <nome da imagem>

mongo_uri = os.getenv("MONGO_ATLAS_STRING_CONEXAO")

if not mongo_uri:
    raise ValueError("O segredo do MongoDB não foi encontrado!")

# Conecta ao MongoDB usando o cliente
cliente = MongoClient(mongo_uri)
  

# CONEXÃO LOCAL -------------------------------------------------------------------------------------------------------------------
# cliente = MongoClient(st.secrets["mongo_atlas"]["string_conexao"])

# ---------------------------------------------------------------------------------------------------------------------------------

db = cliente['db_pls']
colecao = db['PLS']
colecao_2 = db['estatistica']

# Verifica se o documento de contador existe
contador = colecao_2.find_one({"_id": "contador_cliques"})
if contador is None:
    # Caso não exista, cria um com valor inicial 0
    colecao_2.insert_one({"_id": "contador_cliques", "cliques": 0})




# ###################################################################################################
# INTERFACE PRINCIPAL
# ###################################################################################################

# Exibe o título e subtítulo da plataforma na interface
st.markdown(
    """
    <div style='text-align: center; margin-top: -25px;'>
        <h1>Harpia</h1>
        <h3><strong>Plataforma de monitoramento de PLs</strong></h3>
    </div>
    """, unsafe_allow_html=True
)

# Exibe o logo da plataforma
st.logo("https://ispn.org.br/site/wp-content/uploads/2021/04/logo_ISPN_2021.png", size="large")


# Criando a interface de gerenciamento de PLs com uma caixa de diálogo
@st.dialog("Gerenciar PLs")
def dial_gerenciar_pls():

    # Cria as abas: Adicionar, Editar e Excluir PLs
    tab1, tab2, tab3 = st.tabs([":material/add: Adicionar", ":material/edit: Editar", ":material/delete: Excluir"])

    # ADICIONAR //////////////////////////////////////////////////////
    # Interface para adicionar novos PLs
    with tab1:
        
        # Conecta ao banco de dados e busca os temas disponíveis
        temas_disponiveis = sorted(list(colecao.distinct("Tema")))

        # Cria selectbox para escolher o tema do PL
        tema_pl = st.selectbox("Qual o tema do PL?", temas_disponiveis)

        # Busca subtemas relacionados ao tema selecionado
        sub_temas_disponiveis = sorted(list(colecao.distinct("Sub-Tema", {"Tema": tema_pl})))

        # Cria selectbox para escolher o sub-tema do PL
        sub_tema_pl = st.selectbox("Qual o sub-tema do PL?", sub_temas_disponiveis)

        # Cria campo de entrada para o link do PL
        link_pl = st.text_input("Qual o link do PL?")
        
        # Variável de feedback temporário
        feedback = st.empty()

        # Verifica se o botão de adicionar foi pressionado
        if st.button("Adicionar PL", use_container_width=True, icon=":material/add:", type="primary"):
            if tema_pl and sub_tema_pl and link_pl:  
                try:
                    # Configura o navegador Chrome para raspagem de dados
                    abrir_navegador()

                    # Verifica se o link já existe no banco de dados
                    link_repetido = colecao.find_one({"Link": link_pl})

                    if link_repetido:
                        feedback.warning("Essa proposição já está cadastrada no banco de dados!")
                    else:
                        # Verifica o tipo de link e chama a função apropriada
                        if "camara.leg.br" in link_pl or "camara.gov.br" in link_pl:
                            acessa_links_camara(link_pl, tema_pl, sub_tema_pl)
                            
                        elif "senado.leg.br" in link_pl:
                            acessa_links_senado(link_pl, tema_pl, sub_tema_pl)

                finally:
                    # Fecha o navegador após a execução
                    navegador.quit()
                    # Verifica se uma das funções de acesso foi executada
                    if acessa_camara_foi_acessado or acessa_senado_foi_acessado:
                        feedback.success("PL adicionado com sucesso!")
                        time.sleep(6)  
                        feedback.empty()
                        st.rerun()
                    elif not (acessa_camara_foi_acessado or acessa_senado_foi_acessado or link_repetido):
                        st.warning("O link não pôde ser acessado, verifique a URL inserida.")

    # EDITAR /////////////////////////////////////////////////////////
    # Interface para editar um PL existente
    with tab2:
        # Carrega as proposições do banco de dados
        pls = list(colecao.find({}, {"Proposições": 1, "Tema": 1, "Sub-Tema": 1, "Link": 1, "Ementa": 1}))

        if pls:
            # Cria selectbox para selecionar qual PL editar
            pl_selecionado = st.selectbox(
                "Escolha o PL para editar", 
                pls, 
                format_func=lambda x: f"{x['Proposições']}"
            )

            # Se um PL for selecionado, exibe os detalhes para edição
            if pl_selecionado:
                st.write(f"{pl_selecionado.get('Ementa', 'Sem ementa disponível')}")

                # Consulta para buscar os temas únicos no banco
                temas_unicos = list(colecao.distinct("Tema"))
                
                # Cria selectbox para selecionar o novo tema
                tema_selecionado = st.selectbox(
                    "Tema",
                    temas_unicos,
                    index=temas_unicos.index(pl_selecionado['Tema']) if pl_selecionado['Tema'] in temas_unicos else 0
                )

                # Consulta para buscar subtemas relacionados ao tema selecionado
                sub_tema_opcoes = list(colecao.find({"Tema": tema_selecionado}, {"Sub-Tema": 1}))
                sub_tema_opcoes = [st.get("Sub-Tema") for st in sub_tema_opcoes]  # Obtém apenas os subtemas

                # Cria selectbox para selecionar o sub-tema
                sub_tema_selecionado = st.selectbox(
                    "Sub-Tema",
                    sub_tema_opcoes,
                    index=sub_tema_opcoes.index(pl_selecionado['Sub-Tema']) if pl_selecionado['Sub-Tema'] in sub_tema_opcoes else 0
                )

                # Botão para salvar as alterações no banco de dados
                if st.button("Salvar alterações", use_container_width=True, icon=":material/save:", type="primary"):
                    # Atualiza o banco de dados com os novos valores
                    colecao.update_one(
                        {"_id": pl_selecionado['_id']},  
                        {"$set": {
                            "Tema": tema_selecionado,
                            "Sub-Tema": sub_tema_selecionado,
                        }}
                    )
                    st.success(f"'{pl_selecionado['Proposições']}' atualizada com sucesso!")

                    # Aguarda e atualiza a interface
                    time.sleep(2)
                    st.rerun()

        else:
            # Caso não haja PLs cadastrados, exibe um aviso
            st.warning("Nenhuma proposição encontrada no banco de dados.")

    # EXCLUIR ////////////////////////////////////////////////////////
    # Interface para excluir um PL existente
    with tab3:
        # Carrega as proposições do banco de dados
        pls = list(colecao.find({}, {"Proposições": 1, "Tema": 1, "Sub-Tema": 1, "Link": 1}))

        # Exibe os itens em um formato de lista
        if pls:
            # Cria selectbox para escolher qual PL excluir
            pls = st.selectbox("Escolha o PL para excluir", pls, format_func=lambda x: f"{x['Proposições']}")
            
            if st.button("Excluir PL", icon=":material/delete:", use_container_width=True, type="primary"):
                # Exclui o PL selecionado do banco de dados
                excluir_pls(pls["Proposições"])
        else:
            # Caso não haja PLs para excluir, exibe uma mensagem
            st.write("Nenhum PL encontrado no banco de dados.")



# ABAS DA INTERFACE PRINCIPAL

aba1, aba2 = st.tabs(["Proposições Legislativas", "Verificar atualizações"])

# Aba 1 - Proposições ////////////////////////////////////////////////////////////////
with aba1:

    col1, col2 = st.columns([4,1])

    contagem_pls = col1.container()

    col2.button("Gerenciar PLs", icon=":material/settings:", use_container_width=True, on_click=dial_gerenciar_pls)

    # Consulta todos os documentos da coleção
    documentos = colecao.find()  # Você pode adicionar filtros no find() se necessário

    # Converter para DataFrame 
    df = pd.DataFrame(list(colecao.find()))
    df_sem_id = df.drop(columns=['_id'])  # Remove a coluna _id, se necessário

    # Converte a coluna 'Data da Última Ação Legislativa' para o formato datetime
    df_sem_id["Data da Última Ação Legislativa"] = pd.to_datetime(
        df_sem_id["Data da Última Ação Legislativa"], dayfirst=True, errors="coerce"
    )

    # Cria opções de filtro para o usuário
    opcoes_filtro = ["Todos os PLs", "Atualizados no último mês", "Atualizados na última semana"]
    selecionado = st.radio("Teste", opcoes_filtro, index=0, label_visibility="collapsed")

    # Aplica o filtro selecionado pelo usuário
    hoje = datetime.now()
    if selecionado == "Todos os PLs":
        df_filtrado_nao_atualizado = df_sem_id.copy()
        
    elif selecionado == "Atualizados no último mês":
        inicio_mes = hoje - timedelta(days=30)
        df_filtrado_nao_atualizado = df_sem_id[df_sem_id["Data da Última Ação Legislativa"] >= inicio_mes]
        
    elif selecionado == "Atualizados na última semana":
        inicio_semana = hoje - timedelta(days=7)
        df_filtrado_nao_atualizado = df_sem_id[df_sem_id["Data da Última Ação Legislativa"] >= inicio_semana]

    # Ordena os dados pela data da última ação
    df_nao_atualizado = df_filtrado_nao_atualizado.sort_values(by="Data da Última Ação Legislativa", ascending=False)

    # Formata as datas para exibição no formato desejado
    df_nao_atualizado["Data da Última Ação Legislativa"] = df_filtrado_nao_atualizado["Data da Última Ação Legislativa"].dt.strftime("%d/%m/%Y")

    # Definindo a nova ordem das colunas
    nova_ordem = [
        'Tema', 'Sub-Tema', 'Data da Última Ação Legislativa', 'Proposições',
        'Ementa', 'Situação', 'Última Ação Legislativa', 'Casa',
        'Autor', 'UF', 'Partido', 'Apresentação', 'Link'
    ]

    # Reorganizando as colunas do DataFrame
    df_nao_atualizado = df_nao_atualizado[nova_ordem]

    # Renomear a coluna Apresentação para Data de apresentação
    df_nao_atualizado = df_nao_atualizado.rename(columns={"Apresentação": "Data de apresentação"})
    
    contagem_pls.subheader(f'{len(df_nao_atualizado)} PLs monitorados')

    ajustar_altura_dataframe(df_nao_atualizado, 1)



# Aba 2: Verificar atualizações ////////////////////////////////////////////////////////////
with aba2:

    st.write('')

    st.markdown(
    """
    <div style="margin-left: 6px;">
       Escolha temas e sub-temas para verificar atualizações:
    </div>
    """,
    unsafe_allow_html=True
    )

    pls = list(colecao.find({}, {"Tema": 1, "Sub-Tema": 1, "Link": 1}))

    st.write('')

    col1, col2 = st.columns([1, 2])

    # Carregar os temas disponíveis no banco de dados
    temas_disponiveis = sorted(colecao.distinct("Tema"))

    # Interface com multiselect para seleção de temas
    temas_selecionados = col1.multiselect("Tema(s):", temas_disponiveis, placeholder="Todos os temas selecionados", label_visibility="collapsed")

    # Atualiza os sub-temas disponíveis com base no tema selecionado
    # subtemas_disponiveis = sorted(colecao.distinct("Sub-Tema", {"Tema": {"$in": temas_selecionados}}))
    
    # Interface com multiselect para seleção de sub-temas
    # subtemas_selecionados = col2.multiselect("Sub-tema(s):", subtemas_disponiveis, placeholder="Todos os sub-temas selecionados", label_visibility="collapsed")

    # Carrega os dados do MongoDB de acordo com os temas e sub-temas selecionados
    # query = {}
    # if temas_selecionados:
    #     query["Tema"] = {"$in": temas_selecionados}
    # if subtemas_selecionados:
    #     query["Sub-Tema"] = {"$in": subtemas_selecionados}

    st.write("")

    # Carrega os dados do CSV para análise
    df_pls = pd.DataFrame(pls)
    df_pls = df_pls[['Tema', 'Sub-Tema', 'Link']]  # Filtra apenas as colunas relevantes

    # Carregar os dados do MongoDB de acordo com os temas selecionados
    if temas_selecionados:
        #df_pls = pd.DataFrame(list(colecao.find({"Tema": {"$in": temas_selecionados}, "Sub-Tema": {"$in": subtemas_selecionados}})))
         df_pls = pd.DataFrame(list(colecao.find({"Tema": {"$in": temas_selecionados}})))
    else:
        df_pls = pd.DataFrame(list(colecao.find()))  # Caso o usuário não escolha temas, todos os PLs serão verificados

    total_links = len(df_pls)  # Total de links a serem processados

    # Calcula o tempo estimado (4.2 segundos por link)
    tempo_estimado_segundos = total_links * 4.2

    # Converte para minutos e segundos
    minutos = int(tempo_estimado_segundos // 60)  # Divisão inteira para obter os minutos
    segundos = int(tempo_estimado_segundos % 60)  # Resto da divisão para obter os segundos

    @st.dialog("Atualizações")
    def dial_verificar_atualizacoes():

        # Exibe a caixa de confirmação com o tempo estimado
        st.write(f"O sistema visitará a página de **{len(df_pls)} PLs** na internet.")
        st.write(f"Tempo estimado: **{minutos} minutos e {segundos} segundos**.") 
        st.write("**Deseja continuar?**")
        st.write('')

        # Botão que inicia o processo de verificação de atualizações nos PLs
        if st.button("Buscar atualizações", icon=":material/refresh:", type="primary", use_container_width=True, key="botao_verificar_atualizacoes"):

            # Configuração do navegador Chrome para raspagem de dados
            abrir_navegador()

            # Barra de progresso para acompanhar o processamento dos links
            progress = st.progress(0)

            try:
                # Itera sobre cada linha do DataFrame df_pls
                for i, linha in df_pls.iterrows():
                    link = linha['Link']
                    tema = linha['Tema']
                    sub_tema = linha['Sub-Tema']

                    # Calcula e exibe o progresso
                    progress_value = (i + 1) / total_links
                    percent = round(progress_value * 100, 1)
                    progress_text = f"Progresso da atualização: {i + 1}/{total_links} ({percent}%)"
                    progress.progress(progress_value, progress_text)

                    # Verifica o tipo de link e chama a função apropriada para raspagem
                    if "camara.leg.br" in link or "camara.gov.br" in link:
                        acessa_links_camara(link, tema, sub_tema)
                    elif "senado.leg.br" in link:
                        acessa_links_senado(link, tema, sub_tema)
                    else:
                        st.warning(f"URL desconhecida: {link}")
                        continue

            except Exception as e:
                st.error(f"Não foi possível acessar a página {link}")

            finally:
                navegador.quit()
                # Chama a função para verificar as atualizações
                verificar_atualizacoes(df_final, colecao)
                # Exibe as alterações persistidas após a verificação
                exibir_alteracoes()
                # Incrementa o contador diretamente no MongoDB
                colecao_2.update_one(
                    {"_id": "contador_cliques"},
                    {"$inc": {"cliques": 1}}
                )
                       

    col2.button("Verificar atualizações", icon=":material/refresh:", use_container_width=False, on_click=dial_verificar_atualizacoes, type="primary", key="botao_abrir_dialogo")

    # Verifica se a chave 'alteracoes' já existe na sessão. Caso não exista, cria uma lista vazia.
    if "alteracoes" not in st.session_state:
        st.session_state["alteracoes"] = []

    st.write("")

    resultado_comparacao = st.container()



# CARREGAR O BANCO DE DADOS MONGO -- SÓ PRECISA FAZER UMA VEZ

# Converte o DataFrame para uma lista de dicionários
# dados_para_inserir = df_final.to_dict(orient='records')

# Insere os dados no MongoDB
# if dados_para_inserir:  # Verifica se há dados no DataFrame
#     colecao.insert_many(dados_para_inserir)

# st.write("Dados inseridos com sucesso no MongoDB!")


