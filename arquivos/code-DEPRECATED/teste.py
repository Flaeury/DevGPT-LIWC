import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_static_content(url):
    """Raspa o conteúdo de uma página estática"""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Lança um erro para status HTTP ruins (4xx, 5xx)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except requests.RequestException as e:
        print(f"Erro ao acessar a página: {e}")
        return None


def get_dynamic_content(url):
    """Raspa páginas que carregam conteúdo via JavaScript"""
    options = Options()
    # Executa o navegador sem interface gráfica
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        # Tempo para carregar o JavaScript (ajuste conforme necessário)
        time.sleep(5)
        page_source = driver.page_source
        driver.quit()
        soup = BeautifulSoup(page_source, "html.parser")
        return soup.get_text()
    except Exception as e:
        print(f"Erro ao acessar a página dinamicamente: {e}")
        driver.quit()
        return None


# URL para raspagem
url = "https://chatgpt.com/share/a9e4fb74-5366-4c4c-9998-d6caeb8b5acc"

# Primeiro, tenta scraping estático
content = get_static_content(url)

# Se falhar, tenta scraping dinâmico
if not content:
    content = get_dynamic_content(url)

# Exibe os primeiros 500 caracteres do conteúdo extraído
if content:
    print(content[:500])  # Limita a exibição para não poluir o terminal
else:
    print("Não foi possível extrair o conteúdo.")
