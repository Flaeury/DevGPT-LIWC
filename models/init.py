import pandas as pd
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from tqdm import tqdm

# Configurações globais
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
DATABASE = 'conversas.db'
LOG_ERROS = 'log_erros.txt'

# 1. Ler o CSV
df = pd.read_csv('DevGPT/snapshot_20230727/ChatGPT_Link_Sharing.csv')

# 2. Filtrar somente Status == 200
df = df[df['Status'] == 200]

# 3. Conectar ao banco SQLite
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# 4. Criar a tabela
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

# 5. Função para raspar conversas


def raspar_conversa(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar todos os blocos de mensagem
        blocos = soup.find_all('div', class_='overflow-hidden')

        mensagens = []
        for bloco in blocos:
            texto = bloco.get_text(strip=True)
            if texto:
                mensagens.append(texto)

        return mensagens
    except Exception as e:
        with open(LOG_ERROS, 'a', encoding='utf-8') as log:
            log.write(f'Erro ao raspar {url}: {e}\n')
        return []


# 6. Processar as URLs com barra de progresso
for index, row in tqdm(df.iterrows(), total=len(df), desc="Processando conversas"):
    url = row['URL']
    user_name = row['MentionedAuthor']
    genero = ''  # vazio por enquanto

    mensagens = raspar_conversa(url)

    # A lógica assume que mensagens pares são usuário e ímpares são IA
    ordem = 1
    for i in range(0, len(mensagens), 2):
        texto_usuario = mensagens[i] if i < len(mensagens) else None
        texto_ia = mensagens[i+1] if (i+1) < len(mensagens) else None

        if texto_usuario and texto_ia:  # Insere só se tiver ambos
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

    conn.commit()
    time.sleep(0.5)  # Pequena pausa entre as raspagens

# 7. Fechar a conexão
conn.close()

print("\nProcessamento concluído! ✅ Verifique o banco e o arquivo de log para eventuais erros.")
