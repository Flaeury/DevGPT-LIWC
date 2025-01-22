import pandas as pd
import requests
from bs4 import BeautifulSoup

# Carregar o arquivo CSV
csv_data = pd.read_csv('snapshot_20230727/ChatGPT_Link_Sharing.csv')

# Criar ou abrir o arquivo de saída no modo de escrita
with open("output_extracted_data.txt", "w", encoding="utf-8") as output_file:
    processed_links = set()  # Conjunto para rastrear links processados

    # Iterar sobre os links na coluna especificada
    for link in csv_data['URL']:  # Ajuste 'URL' para o nome correto da coluna de links
        if link in processed_links:
            continue  # Pular links já processados
        processed_links.add(link)

        try:
            # Fazer a requisição HTTP para o link
            response = requests.get(link)

            # Verificar se a resposta foi bem-sucedida
            if response.status_code == 200:
                # Parsear o conteúdo HTML com BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extrair os dados desejados
                paragraphs = soup.find_all('p')
                extracted_data = "\n".join(
                    p.get_text(strip=True) for p in paragraphs)

                # Escrever no arquivo e imprimir no terminal
                output_file.write(f"Dados extraídos de {link}:\n\n")
                output_file.write(extracted_data + "\n\n")
                print(f"Dados extraídos de {link}:\n")
                print(extracted_data + "\n")
            else:
                # Escrever erros no arquivo e no terminal
                error_message = f"Falha ao acessar {link}: Status {response.status_code}\n\n"
                output_file.write(error_message)
                print(error_message)

        except requests.exceptions.RequestException as e:
            # Escrever exceções no arquivo e no terminal
            error_message = f"Erro ao acessar {link}: {e}\n\n"
            output_file.write(error_message)
            print(error_message)
