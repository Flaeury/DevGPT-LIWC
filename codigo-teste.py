import csv
import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By


def extract_conversations(input_csv, db_path):
    # Conecta ou cria o banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Cria a tabela se não existir
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

    driver = webdriver.Chrome()

    with open(input_csv, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                driver.get(row["URL"])
                time.sleep(5)

                conversations = driver.find_elements(By.TAG_NAME, "body")
                for conversation in conversations:
                    try:
                        user_message_elem = conversation.find_elements(
                            By.XPATH, ".//h5[text()='You said:']/following-sibling::div"
                        )
                        bot_message_elem = conversation.find_elements(
                            By.XPATH, ".//h6[text()='ChatGPT said:']/following-sibling::div"
                        )

                        for i in range(len(user_message_elem)):
                            texto_usuario = user_message_elem[i].text
                            texto_ia = bot_message_elem[i].text

                            # Definindo valores fixos ou derivados
                            user_name = "desconhecido"  # ou pode puxar de outro lugar se quiser
                            genero = "desconhecido"     # idem
                            # ordem da conversa na página (começando em 1)
                            ordem = i + 1

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

                        conn.commit()

                    except Exception as inner_e:
                        print(f"Erro ao extrair mensagens: {inner_e}")

            except Exception as e:
                print(f"Erro ao processar o link {row['URL']}: {e}")

    driver.quit()
    conn.close()


if __name__ == "__main__":
    extract_conversations(
        "DevGPT/snapshot_20230727/ChatGPT_Link_Sharing.csv",
        "banco_de_conversas.db"
    )

    print("Processamento concluído! ✅ Conversas salvas no banco de dados.")
