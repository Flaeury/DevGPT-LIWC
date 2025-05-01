import csv
import time
import sqlite3
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm  # 📦 Adicionando barra de progresso


def criar_tabela(cursor):
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


def processar_csv(csv_path, cursor, driver, csv_writer):
    with open(csv_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                url = row["URL"]
                user_name = row.get("MentionedAuthor", "desconhecido")

                driver.get(url)
                time.sleep(5)  # tempo de espera para a página carregar

                corpo_pagina = driver.find_elements(By.TAG_NAME, "body")

                for corpo in corpo_pagina:
                    try:
                        mensagens_usuario = corpo.find_elements(
                            By.XPATH, ".//h5[text()='Você disse:']/following-sibling::div"
                        )
                        mensagens_ia = corpo.find_elements(
                            By.XPATH, ".//h6[text()='O ChatGPT disse:']/following-sibling::div"
                        )

                        total_msgs = min(
                            len(mensagens_usuario), len(mensagens_ia))

                        for i in range(total_msgs):
                            texto_usuario = mensagens_usuario[i].text
                            texto_ia = mensagens_ia[i].text

                            # print(f"[{csv_path}] Você: {texto_usuario[:60]}...")
                            # print(f"[{csv_path}] ChatGPT: {texto_ia[:60]}...\n")

                            # Salva no banco
                            cursor.execute('''
                                INSERT INTO conversas (
                                    user_name, genero, ordem_mensagem, texto_usuario, texto_ia,
                                    analytical_thinking, clout, authentic, emotional_tone
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                user_name, "desconhecido", i + 1,
                                texto_usuario, texto_ia,
                                None, None, None, None
                            ))

                            # Salva no CSV
                            csv_writer.writerow({
                                "arquivo_csv_origem": os.path.basename(csv_path),
                                "user_name": user_name,
                                "genero": "desconhecido",
                                "ordem_mensagem": i + 1,
                                "texto_usuario": texto_usuario,
                                "texto_ia": texto_ia,
                                "analytical_thinking": "",
                                "clout": "",
                                "authentic": "",
                                "emotional_tone": ""
                            })

                    except Exception as erro_extracao:
                        print(
                            f"Erro ao extrair mensagens da página: {erro_extracao}")
                        # Captura a tela do erro
                        driver.save_screenshot(f"erro_{int(time.time())}.png")

            except Exception as erro_pagina:
                print(f"Erro ao carregar a URL {row['URL']}: {erro_pagina}")
                # Captura a tela do erro
                driver.save_screenshot(f"erro_{int(time.time())}.png")


def main(lista_csv, db_path, output_csv_path):
    # Conexão com banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    criar_tabela(cursor)

    # Iniciar navegador
    options = Options()
    options.add_argument("--headless")  # ⬅️ evita abrir janela
    driver = webdriver.Chrome(options=options)

    with open(output_csv_path, "w", encoding="utf-8", newline="") as outfile:
        campos = [
            "arquivo_csv_origem", "user_name", "genero", "ordem_mensagem",
            "texto_usuario", "texto_ia", "analytical_thinking", "clout", "authentic", "emotional_tone"
        ]
        csv_writer = csv.DictWriter(outfile, fieldnames=campos)
        csv_writer.writeheader()

        # Barra de progresso com tqdm
        for csv_file in tqdm(lista_csv, desc="Processando arquivos CSV"):
            print(f"📄 Processando: {csv_file}")
            processar_csv(csv_file, cursor, driver, csv_writer)
            conn.commit()

    driver.quit()
    conn.close()
    print("✅ Processamento concluído! Dados salvos no banco de dados e CSV.")


if __name__ == "__main__":
    arquivos_csv = glob.glob("data/**/*.csv")
    main(arquivos_csv, "extracao.db", "conversas_extraidas.csv")
