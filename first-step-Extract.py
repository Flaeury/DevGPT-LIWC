import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


def extract_conversations(input_csv, output_csv):
    driver = webdriver.Chrome()

    with open(input_csv, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        with open(output_csv, "w", encoding="utf-8", newline="") as outfile:
            fieldnames = ["URL", "UserMessage", "ChatGPTMessage"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

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
                                user_message = user_message_elem[i].text
                                bot_message = bot_message_elem[i].text

                                row_data = {
                                    "URL": row["URL"],
                                    "UserMessage": user_message,
                                    "ChatGPTMessage": bot_message,
                                }
                                writer.writerow(row_data)

                        except Exception as inner_e:
                            print(f"Erro ao extrair mensagens: {inner_e}")

                except Exception as e:
                    print(f"Erro ao processar o link {row['URL']}: {e}")

    driver.quit()


if __name__ == "__main__":
    extract_conversations(
        "DevGPT/snapshot_20230727/ChatGPT_Link_Sharing2.csv", "CSV/extracted_data.csv")
