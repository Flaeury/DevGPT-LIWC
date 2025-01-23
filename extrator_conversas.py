from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configuração do driver (garanta que você tem o ChromeDriver instalado)
driver = webdriver.Chrome()

# Lista de links
links = [
    "https://chat.openai.com/share/53b38605-68e5-4922-81fe-e4588fb28d8a",
    "https://chat.openai.com/share/bb0d35d9-0239-492e-9ec2-49505aae202b",
    "https://chat.openai.com/share/46ff149e-a4c7-4dd7-a800-fc4a642ea389",
    "https://chat.openai.com/share/ac7a769a-696f-447a-b123-a3e8ee585858",
    "https://chat.openai.com/share/d24ce24f-283a-4f76-bacb-6e0740c234a1"
]

# Arquivo para salvar o conteúdo extraído
with open("conversas_extraidas.txt", "w", encoding="utf-8") as f_output:
    for link in links:
        try:
            # Abrir o link no navegador
            driver.get(link)
            time.sleep(5)  # Aguardar o carregamento da página

            user_messages = []
            bot_messages = []

            # Extrair o texto da conversa
            # chat_content = driver.find_element(By.TAG_NAME, "article").text # BUSCA SOMENTE O QUE É DO USER
            chat_content = driver.find_element(By.TAG_NAME, "div").text

            for conversation in chat_content:
                try:
                    # Tentar pegar a mensagem do usuário
                    user_message_elem = conversation.find_element(
                        By.XPATH, ".//h5[text()='You said:']/following-sibling::div"
                    )
                    user_message = user_message_elem.text
                    # Adicionando debug para a mensagem do usuário
                    print(f"User Message: {user_message}")
                    user_messages.append(user_message)

                    # Tentar pegar a mensagem do ChatGPT
                    bot_message_elem = conversation.find_element(
                        By.XPATH, ".//h6[text()='ChatGPT said:']/following-sibling::div"
                    )
                    bot_message = bot_message_elem.text
                    # Adicionando debug para a mensagem do bot
                    print(f"Bot Message: {bot_message}")
                    bot_messages.append(bot_message)

                except Exception as inner_e:
                    print(f"Erro ao extrair uma mensagem: {inner_e}")

            # Exibir e salvar o texto
            print(f"Dados extraídos de {link}:\n{chat_content}\n")
            f_output.write(f"Dados extraídos de {link}:\n{chat_content}\n\n")
        except Exception as e:
            print(f"Erro ao processar o link {link}: {e}")

# Fechar o navegador
driver.quit()
