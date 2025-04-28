import pandas as pd
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import os
from tqdm import tqdm

# Configurações globais
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
DATABASE = 'conversas.db'
LOG_ERROS = 'log_erros.txt'
Pasta_Base = 'DevGPT'  # Caminho base para procurar os arquivos CSV

# Função para encontrar todos os arquivos CSV dentro da pasta DevGPT e suas subpastas


def localizar_csv(pasta_base):
    arquivos_csv = []
    for root, dirs, files in os.walk(pasta_base):
        for file in files:
            if file.endswith('.csv'):
                arquivos_csv.append(os.path.join(root, file))
    return arquivos_csv


# 1. Localizar e ler os arquivos CSV
arquivos_csv = localizar_csv(Pasta_Base)

# 2. Criar a lista de DataFrames com os dados dos arquivos CSV
df_list = []
for arquivo_csv in arquivos_csv:
    try:
        df = pd.read_csv(arquivo_csv)
        df_list.append(df)
    except Exception as e:
        with open(LOG_ERROS, 'a', encoding='utf-8') as log:
            log.write(f'Erro ao ler o arquivo {arquivo_csv}: {e}\n')

# Concatenar todos os DataFrames
df = pd.concat(df_list, ignore_index=True)

# 3. Filtrar somente Status == 200
df = df[df['Status'] == 200]

# 4. Conectar ao banco SQLite
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# 5. Criar a tabela
cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        genero TEXT,
        ordem_mensagem INTEGER,
        texto_usuario TEXT,
        texto_ia TEXT,
        analytical_thinking REAL,
        clout REAL,
        authentic REAL,
        emotional_tone REAL
    )
''')
conn.commit()

# 6. Função para raspar conversas


def raspar_conversa(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar todos os blocos de mensagens (h5 e h6 com sr-only)
        mensagens = []
        h5_tags = soup.find_all('h5', class_='sr-only')  # Mensagens do usuário
        h6_tags = soup.find_all('h6', class_='sr-only')  # Mensagens do ChatGPT

        # Processar as mensagens do usuário
        for h5_tag in h5_tags:
            # Pega a div que vem depois do h5
            div_usuario = h5_tag.find_next('div')
            if div_usuario:
                mensagens.append(('usuario', div_usuario.get_text(strip=True)))

        # Processar as mensagens do ChatGPT
        for h6_tag in h6_tags:
            div_ia = h6_tag.find_next('div')  # Pega a div que vem depois do h6
            if div_ia:
                mensagens.append(('ia', div_ia.get_text(strip=True)))

        return mensagens
    except Exception as e:
        with open(LOG_ERROS, 'a', encoding='utf-8') as log:
            log.write(f'Erro ao raspar {url}: {e}\n')
        return []


# 7. Processar as URLs com barra de progresso
for index, row in tqdm(df.iterrows(), total=len(df), desc="Processando conversas"):
    url = row['URL']
    user_name = row['MentionedAuthor']
    genero = ''  # vazio por enquanto

    mensagens = raspar_conversa(url)

    # A lógica assume que as mensagens alternam entre o usuário e a IA
    ordem = 1
    texto_usuario = None
    texto_ia = None

    for origem, mensagem in mensagens:
        if origem == 'usuario':
            texto_usuario = mensagem
        elif origem == 'ia':
            texto_ia = mensagem

        if texto_usuario and texto_ia:  # Insere só se ambos os textos estiverem presentes
            # Imprimir as informações no terminal
            print(f"\nUsername: {user_name}")
            print(f"Genero: {genero}")
            print(f"Ordem: {ordem}")
            print(f"Texto do usuário: {texto_usuario}")
            print(f"Texto da IA: {texto_ia}")

            # Inserir no banco de dados
            cursor.execute('''
                INSERT INTO conversas (
                    user_name, genero, ordem_mensagem, texto_usuario, texto_ia, 
                    analytical_thinking, clout, authentic, emotional_tone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_name,
                genero,
                ordem,
                texto_usuario,
                texto_ia,
                None, None, None, None
            ))

            ordem += 1
            texto_usuario = None
            texto_ia = None  # Reseta para próxima interação

    conn.commit()
    time.sleep(0.5)  # Pequena pausa entre as raspagens

# 8. Fechar a conexão
conn.close()

print("\nProcessamento concluído! ✅ Verifique o banco e o arquivo de log para eventuais erros.")
