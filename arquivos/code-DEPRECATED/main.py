import csv
import requests
from bs4 import BeautifulSoup
import time

# Caminho do dicionário LIWC
liwc_dict_path = "LIWC.dic"

# Nome do arquivo de saída
input_csv = "DevGPT/snapshot_20230727/ChatGPT_Link_Sharing.csv"
output_txt = "output_liwc_analysis.txt"

# Função para carregar um dicionário LIWC mais avançado


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

# Função para analisar uma mensagem com o LIWC


def analisar_mensagem_liwc(mensagem, liwc_dict):
    categorias_contadas = {i: 0 for i in range(1, 70)}

    for palavra in mensagem.split():
        palavra = palavra.lower().strip(",.?!;:'\"()[]{}")
        if palavra in liwc_dict:
            for categoria in liwc_dict[palavra]:
                categorias_contadas[categoria] += 1

    return categorias_contadas

# Função para extrair mensagens do ChatGPT e do usuário


def extrair_mensagens(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erro ao acessar {url} - Código {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")

        # Atualização na busca dos elementos
        user_messages = [msg.get_text(strip=True) for msg in soup.find_all(
            "h5", class_="sr-only") if msg.get_text(strip=True) == "You said:"]
        bot_messages = [msg.get_text(strip=True) for msg in soup.find_all(
            "h6", class_="sr-only") if msg.get_text(strip=True) == "ChatGPT said:"]

        if not user_messages or not bot_messages:
            print(f"Nenhuma conversa encontrada em {url}")
        return user_messages, bot_messages
    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        return None, None


# Carregar o dicionário LIWC
liwc_dict = carregar_dicionario_liwc(liwc_dict_path)

# Categorias avançadas do LIWC
categorias_dict = {
    1: "Pronouns",
    2: "Articles",
    3: "Past tense",
    4: "Present tense",
    5: "Future tense",
    6: "Prepositions",
    7: "Negations",
    8: "Social Processes",
    9: "Emotions",
    10: "Cognitive Processes",
    11: "Perceptual Processes",
    12: "Social Interactions",
    13: "Personal Identification",
    14: "Time and Space",
    15: "Work and Achievements",
    16: "Biological and Health",
    17: "Death and Existential Concepts",
    18: "Swear Words",
    19: "Metaphors and Abstract Concepts",
    20: "Technology and Digital Culture",
    21: "Creative Processes",
    22: "Sociopolitical and Cultural"
}

# Abrir o CSV para leitura e escrever no arquivo de texto com análise
with open(input_csv, "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    with open(output_txt, "w", encoding="utf-8") as outfile:
        for row in reader:
            url = row["URL"]
            print(f"🔍 Extraindo conversa de: {url}")

            user_messages, bot_messages = extrair_mensagens(url)
            if not user_messages or not bot_messages:
                continue

            for user_message, bot_message in zip(user_messages, bot_messages):
                user_liwc_counts = analisar_mensagem_liwc(
                    user_message, liwc_dict)
                bot_liwc_counts = analisar_mensagem_liwc(
                    bot_message, liwc_dict)

                # Escrever as mensagens no arquivo de texto
                outfile.write(f"URL: {url}\n")
                outfile.write(f"User Message: {user_message}\n")
                outfile.write(f"ChatGPT Message: {bot_message}\n")

                # Criar a lista de categorias para o usuário e para o bot
                user_categories = [
                    f"{categorias_dict[k]}: {user_liwc_counts[k]}" for k in range(1, 70)]
                bot_categories = [
                    f"{categorias_dict[k]}: {bot_liwc_counts[k]}" for k in range(1, 70)]

                # Escrever as categorias no arquivo de texto
                outfile.write(
                    f"User LIWC Counts: [{', '.join(user_categories)}]\n")
                outfile.write(
                    f"Bot LIWC Counts: [{', '.join(bot_categories)}]\n\n")

            time.sleep(2)

print("✅ Extração finalizada!")
