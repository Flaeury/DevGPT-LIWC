from automacao import webdriver
from selenium.webdriver.common.by import By
import time

# Configuração do driver (garanta que você tem o ChromeDriver instalado)
driver = webdriver.Chrome()

# Lista de links
links = [
    "https://chat.openai.com/share/53b38605-68e5-4922-81fe-e4588fb28d8a",
    "https://chat.openai.com/share/bb0d35d9-0239-492e-9ec2-49505aae202b"
]

# Arquivo para salvar o conteúdo extraído
with open("conversas_extraidas.txt", "w", encoding="utf-8") as f_output:
    for link in links:
        try:
            # Abrir o link no navegador
            driver.get(link)
            time.sleep(5)  # Aguardar o carregamento da página

            # Extrair o texto da conversa
            chat_content = driver.find_element(By.TAG_NAME, "body").text

            # Exibir e salvar o texto
            print(f"Dados extraídos de {link}:\n{chat_content}\n")
            f_output.write(f"Dados extraídos de {link}:\n{chat_content}\n\n")
        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")

# Fechar o navegador
driver.quit()
