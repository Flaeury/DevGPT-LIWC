import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def login_github(driver):
    """Função para abrir a página de login e esperar o usuário autenticar manualmente."""
    driver.get("https://github.com/login")
    input("Faça login no GitHub e pressione Enter para continuar...")


def extract_github_pronouns(input_csv, output_csv, driver, processed_authors):
    with open(input_csv, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        with open(output_csv, "a", encoding="utf-8", newline="") as outfile:
            fieldnames = ["Author", "Gender"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            if os.stat(output_csv).st_size == 0:
                writer.writeheader()

            for row in reader:
                mentioned_url = row.get("MentionedURL", "").strip()
                mentioned_author = row.get("MentionedAuthor", "").strip()

                if mentioned_url.startswith("https://github.com"):
                    author = mentioned_url.split('/')[3]
                else:
                    author = mentioned_author

                if not author or author in processed_authors:
                    continue

                print(f"Processando: {author}")

                url = f"https://github.com/{author}"
                driver.get(url)
                time.sleep(3)

                try:
                    pronoun_element = driver.find_element(
                        By.XPATH, "//span[contains(@class, 'p-nickname')]//following-sibling::span"
                    )
                    pronoun = pronoun_element.text.strip()
                except:
                    pronoun = "Null"

                print(f"Encontrado: {author} - {pronoun}")

                writer.writerow({"Author": author, "Gender": pronoun})
                outfile.flush()

                processed_authors.add(author)


def process_all_snapshots(base_dir, output_csv):
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    login_github(driver)

    processed_authors = set()

    if os.path.exists(output_csv):
        with open(output_csv, "r", encoding="utf-8") as outfile:
            reader = csv.DictReader(outfile)
            for row in reader:
                processed_authors.add(row["Author"])

    # Listar todas as pastas de snapshot e ordená-las
    snapshot_folders = sorted(
        [f for f in os.listdir(base_dir) if f.startswith("snapshot_")],
        reverse=False  # Garante que processe na ordem crescente
    )

    for folder in snapshot_folders:
        input_csv = os.path.join(base_dir, folder, "ChatGPT_Link_Sharing.csv")

        if os.path.exists(input_csv):
            print(f"\n>>> Processando snapshot: {folder}")
            extract_github_pronouns(
                input_csv, output_csv, driver, processed_authors)
        else:
            print(f"Arquivo não encontrado em {folder}, pulando...")

    driver.quit()


# Diretório base onde os snapshots estão localizados
base_directory = "DevGPT"
output_csv_path = "CSV/github_pronouns.csv"

process_all_snapshots(base_directory, output_csv_path)
