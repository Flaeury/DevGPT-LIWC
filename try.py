import pandas as pd
import requests
from bs4 import BeautifulSoup

# Carregar o arquivo CSV
csv_data = pd.read_csv('DevGPT/snapshot_20230727/ChatGPT_Link_Sharing.csv')

# Exibir as primeiras linhas para verificar a coluna que contém os links
print(csv_data.head())

# Supondo que a coluna de links seja chamada 'links', vamos iterar sobre eles
for link in csv_data['URL']:  # Ajuste 'links' para o nome correto da coluna de links
    try:
        # Fazer a requisição HTTP para o link
        response = requests.get(link)

        # Se a requisição for bem-sucedida
        if response.status_code == 200:
            # Parsear o conteúdo HTML da página com BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extrair os dados desejados. Isso vai depender da estrutura da página.
            # Exemplo: para pegar todo o texto dentro de parágrafos <p>
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                print(p.get_text())
        else:
            print(f"Falha ao acessar {link}: Status {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {link}: {e}")
