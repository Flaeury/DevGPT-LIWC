import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Função para carregar o dicionário LIWC


def carregar_dicionario_liwc(dicionario_path):
    dicionario = {}
    with open(dicionario_path, "r", encoding="utf-8") as file:
        linhas = file.readlines()

    for linha in linhas:
        if linha.startswith("%") or not linha.strip():
            continue
        partes = linha.split()
        palavra = partes[0]
        try:
            categorias = [int(cat) for cat in partes[1:]]
            dicionario[palavra] = categorias
        except ValueError:
            print(f"Erro ao processar a linha: {linha.strip()} (ignorada)")
            continue

    return dicionario


# Função para analisar a mensagem e retornar o nome das categorias com base nas contagens
categorias = {
    1: "Pronouns",
    2: "Articles",
    3: "Past tense",
    4: "Present tense",
    5: "Future tense",
    6: "Prepositions",
    7: "Negations",
    8: "Numbers",
    9: "Swear words",
    10: "Social Processes",
    11: "Friends",
    12: "Family",
    13: "Humans",
    14: "Affective Processes",
    15: "Positive Emotions",
    16: "Negative Emotions",
    17: "Anxiety",
    18: "Anger",
    19: "Sadness",
    20: "Cognitive Processes",
    21: "Insight",
    22: "Causation",
    23: "Discrepancy",
    24: "Tentative",
    25: "Certainty",
    26: "Inhibition",
    27: "Inclusive",
    28: "Exclusive",
    29: "Perceptual Processes",
    30: "Seeing",
    31: "Hearing",
    32: "Feeling",
    33: "Biological Processes",
    34: "Body",
    35: "Sexuality",
    36: "Relativity",
    37: "Motion",
    38: "Space",
    39: "Time",
    40: "Work",
    41: "Achievement",
    42: "Leisure",
    43: "Home",
    44: "Money",
    45: "Religion",
    46: "Death",
    47: "Assent",
    48: "Nonfluencies",
    49: "Fillers"
}


def analisar_mensagem_liwc(mensagem, liwc_dict):
    categorias_contadas = {categorias[i]: 0 for i in range(1, 50)}

    for palavra in mensagem.split():
        palavra = palavra.lower().strip(",.?!;:'\"()[]{}")
        if palavra in liwc_dict:
            for categoria in liwc_dict[palavra]:
                categorias_contadas[categorias[categoria]] += 1

    return categorias_contadas


# Configuração do driver (garanta que você tenha o ChromeDriver instalado)
driver = webdriver.Chrome()

# Caminhos dos arquivos
input_csv = "snapshot_20230727/ChatGPT_Link_Sharing2.csv"
output_csv = "output_extracted_data.csv"
liwc_dict_path = "LIWC.dic"  # Caminho para o dicionário LIWC

# Carregar o dicionário LIWC
liwc_dict = carregar_dicionario_liwc(liwc_dict_path)

# Abrir o arquivo CSV para leitura
with open(input_csv, "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    # Criar um novo arquivo para salvar os resultados
    with open(output_csv, "w", encoding="utf-8", newline="") as outfile:
        fieldnames = ["URL", "UserMessage",
                      "ChatGPTMessage", "UserLIWC", "BotLIWC"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                # Abrir o link no navegador
                driver.get(row["URL"])
                time.sleep(5)  # Aguardar o carregamento da página

                # Buscar as seções de conversa
                conversations = driver.find_elements(By.TAG_NAME, "body")
                for conversation in conversations:
                    try:
                        user_message_elem = conversation.find_elements(
                            By.XPATH, ".//h5[text()='You said:']/following-sibling::div"
                        )
                        bot_message_elem = conversation.find_elements(
                            By.XPATH, ".//h6[text()='ChatGPT said:']/following-sibling::div"
                        )

                        # Iterar e extrair todas as mensagens e respostas
                        for i in range(len(user_message_elem)):
                            user_message = user_message_elem[i].text
                            bot_message = bot_message_elem[i].text

                            # Analisar mensagens com LIWC
                            user_liwc = analisar_mensagem_liwc(
                                user_message, liwc_dict)
                            bot_liwc = analisar_mensagem_liwc(
                                bot_message, liwc_dict)

                            # Escrever no CSV
                            writer.writerow({
                                "URL": row["URL"],
                                "UserMessage": user_message,
                                "ChatGPTMessage": bot_message,
                                "UserLIWC": str(user_liwc),
                                "BotLIWC": str(bot_liwc)
                            })

                    except Exception as inner_e:
                        print(
                            f"Erro ao extrair mensagens específicas: {inner_e}")

            except Exception as e:
                print(f"Erro ao processar o link {row['URL']}: {e}")

# Fechar o navegador
driver.quit()
