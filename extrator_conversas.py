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

# Função para contar a presença de categorias LIWC em uma mensagem


# Dicionário com as categorias
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

# Função para analisar a mensagem e retornar o nome das categorias com base nas contagens


def analisar_mensagem_liwc(mensagem, liwc_dict):
    # Inicializa com os nomes das categorias
    categorias_contadas = {categorias[i]: 0 for i in range(1, 50)}

    # Dividir a mensagem em palavras e analisar
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
        fieldnames = reader.fieldnames + \
            ["UserMessage", "ChatGPTMessage", "UserLIWC", "BotLIWC"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            for row in reader:
                try:
                    # Abrir o link no navegador
                    driver.get(row["URL"])
                    time.sleep(5)  # Aguardar o carregamento da página

                    # Inicializar variáveis para as mensagens
                    user_messages = []
                    bot_messages = []

                    try:
                        # Buscar as seções de conversa
                        conversations = driver.find_elements(
                            By.TAG_NAME, "body")

                        # Iterar sobre as conversas e separar o conteúdo
                        for conversation in conversations:
                            try:
                                # Tentar pegar a mensagem do usuário
                                user_message_elem = conversation.find_element(
                                    By.XPATH, ".//h5[text()='You said:']/following-sibling::div"
                                )
                                user_message = user_message_elem.text
                                user_messages.append(user_message)

                                # Tentar pegar a mensagem do ChatGPT
                                bot_message_elem = conversation.find_element(
                                    By.XPATH, ".//h6[text()='ChatGPT said:']/following-sibling::div"
                                )
                                bot_message = bot_message_elem.text
                                bot_messages.append(bot_message)

                            except Exception as inner_e:
                                print(
                                    f"Erro ao extrair uma mensagem específica: ")
                                # Apenas pular para a próxima mensagem, sem interromper o loop principal

                    except Exception as conv_error:
                        print(f"Erro ao buscar as conversas: {conv_error}")
                        # Caso não consiga encontrar conversas, definir como N/A
                        user_messages = ["N/A"]
                        bot_messages = ["N/A"]

                    # Analisar as mensagens usando o LIWC
                    try:
                        user_liwc = [analisar_mensagem_liwc(
                            msg, liwc_dict) for msg in user_messages]
                        bot_liwc = [analisar_mensagem_liwc(
                            msg, liwc_dict) for msg in bot_messages]
                    except Exception as liwc_error:
                        print(f"Erro ao analisar as mensagens com LIWC: {
                              liwc_error}")
                        user_liwc = ["N/A"]
                        bot_liwc = ["N/A"]

                    # Escrever a linha no arquivo CSV
                    row["UserMessage"] = " || ".join(
                        user_messages) if user_messages else "N/A"
                    row["ChatGPTMessage"] = " || ".join(
                        bot_messages) if bot_messages else "N/A"
                    row["UserLIWC"] = str(user_liwc)
                    row["BotLIWC"] = str(bot_liwc)

                    writer.writerow(row)

                except Exception as e:
                    print(f"Erro ao processar o link {row['URL']}: {e}")
                    row["UserMessage"] = "Erro ao acessar o link"
                    row["ChatGPTMessage"] = "Erro ao acessar o link"
                    row["UserLIWC"] = "N/A"
                    row["BotLIWC"] = "N/A"
                    writer.writerow(row)

            # Fechar o navegador
driver.quit()


# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time

# # Configuração do driver (garanta que você tem o ChromeDriver instalado)
# driver = webdriver.Chrome()

# # Lista de links
# links = [
#     "https://chat.openai.com/share/53b38605-68e5-4922-81fe-e4588fb28d8a",
#     "https://chat.openai.com/share/bb0d35d9-0239-492e-9ec2-49505aae202b",
#     "https://chat.openai.com/share/46ff149e-a4c7-4dd7-a800-fc4a642ea389",
#     "https://chat.openai.com/share/ac7a769a-696f-447a-b123-a3e8ee585858",
#     "https://chat.openai.com/share/d24ce24f-283a-4f76-bacb-6e0740c234a1"
# ]

# # Arquivo para salvar o conteúdo extraído
# with open("conversas_extraidas.txt", "w", encoding="utf-8") as f_output:
#     for link in links:
#         try:
#             # Abrir o link no navegador
#             driver.get(link)
#             time.sleep(5)  # Aguardar o carregamento da página

#             user_messages = []
#             bot_messages = []

#             # Extrair o texto da conversa
#             # chat_content = driver.find_element(By.TAG_NAME, "article").text # BUSCA SOMENTE O QUE É DO USER
#             chat_content = driver.find_element(By.TAG_NAME, "div").text

#             for conversation in chat_content:
#                 try:
#                     # Tentar pegar a mensagem do usuário
#                     user_message_elem = conversation.find_element(
#                         By.XPATH, ".//h5[text()='You said:']/following-sibling::div"
#                     )
#                     user_message = user_message_elem.text
#                     # Adicionando debug para a mensagem do usuário
#                     print(f"User Message: {user_message}")
#                     user_messages.append(user_message)

#                     # Tentar pegar a mensagem do ChatGPT
#                     bot_message_elem = conversation.find_element(
#                         By.XPATH, ".//h6[text()='ChatGPT said:']/following-sibling::div"
#                     )
#                     bot_message = bot_message_elem.text
#                     # Adicionando debug para a mensagem do bot
#                     print(f"Bot Message: {bot_message}")
#                     bot_messages.append(bot_message)

#                 except Exception as inner_e:
#                     print(f"Erro ao extrair uma mensagem: {inner_e}")

#             # Exibir e salvar o texto
#             print(f"Dados extraídos de {link}:\n{chat_content}\n")
#             f_output.write(f"Dados extraídos de {link}:\n{chat_content}\n\n")
#         except Exception as e:
#             print(f"Erro ao processar o link {link}: {e}")

# # Fechar o navegador
# driver.quit()
