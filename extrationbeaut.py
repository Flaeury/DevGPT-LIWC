import os
import random
import re
import json
import datetime
import asyncio
from json.decoder import JSONDecodeError
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


# Lista de User Agents para simular navegação real
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
]

# Função auxiliar para contar "tokens" (simples, por palavras)


def get_num_tokens_from_string(text):
    return len(text.split())

# Gera identificador baseado na URL e turno


def create_hash_index(url, turn):
    return f"{abs(hash(url))}_{turn}"

# Função para fazer o fetch da página


async def fetch_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='domcontentloaded')
        content = await page.content()
        await browser.close()
        return content

# Função para extrair dados do compartilhamento do ChatGPT


async def obtain_from_chatgpt_sharing(browser, url, mention):
    revised_url = url.replace(
        'https://chat.openai.com/share/', 'https://chatgpt.com/share/')
    content = await fetch_page(revised_url)

    if not isinstance(content, str):
        return {
            "URL": url,
            "Mention": mention,
            "Status": content,
        }

    soup = BeautifulSoup(content, "html.parser")
    script_tag = soup.find('script', type='application/json')
    if not script_tag:
        return {
            "URL": url,
            "Mention": mention,
            "Status": 404,
            "Error": "JSON script not found"
        }

    try:
        data = json.loads(script_tag.text)
    except JSONDecodeError:
        return {
            "URL": url,
            "Mention": mention,
            "Status": 404,
            "Error": "Failed to decode JSON"
        }

    values = list(data['props']['pageProps']
                  ['serverResponse']['data']['mapping'].values())
    values.reverse()

    conversations = []
    prompts = []
    answer, prompt = None, None
    answer_tokens = 0
    is_assistant = False
    model = None
    turn = 0
    index = 0

    for mapping in values:
        if 'message' in mapping:
            msg = mapping['message']

            if 'model_slug' in msg['metadata'] and model is None:
                slug = msg['metadata']['model_slug']
                model = 'GPT-3.5' if 'text-davinci-002-render-sha' in slug else slug.upper()

            if msg['content']['content_type'] == 'code':
                continue

            if msg['author']['role'] == 'user':
                prompt = msg['content']['parts'][0]
                prompts.append(prompt)
                is_assistant = False

            elif msg['author']['role'] == 'assistant':
                if 'parts' not in msg['content']:
                    continue

                current_answer = msg['content']['parts'][0]
                answer_tokens += get_num_tokens_from_string(current_answer)

                # Extrair blocos de código
                code_contents = re.findall(
                    r'```[\s\S]*?```', current_answer, re.DOTALL)
                code_blocks = []

                for code_content in code_contents:
                    code_type = code_content.split('\n')[0][3:].strip()
                    code_type = code_type if code_type != '' else None
                    current_answer = current_answer.replace(
                        code_content, f"[CODE_BLOCK_{index}]")
                    code_body = '\n'.join(code_content.split('\n')[1:-1])
                    code_blocks.append({
                        "ReplaceString": f"[CODE_BLOCK_{index}]",
                        "Type": code_type,
                        "Content": code_body
                    })
                    index += 1

                if is_assistant and conversations:
                    conversations[-1]['Answer'] += '\n' + current_answer
                    conversations[-1]['ListOfCode'].extend(code_blocks)
                else:
                    answer = current_answer
                    is_assistant = True

        if answer is not None and prompt is not None:
            turn += 1
            conversations.append({
                "Prompt": prompt,
                "Answer": answer,
                "ListOfCode": code_blocks,
                "ConvIndex": create_hash_index(url, turn)
            })
            answer, prompt = None, None

    return {
        "URL": url,
        "Mention": mention,
        "Status": 200,
        "DateOfConversation": datetime.datetime.fromtimestamp(
            data['props']['pageProps']['serverResponse']['data']['create_time']
        ).strftime('%B %-d, %Y'),
        "Title": data['props']['pageProps']['serverResponse']['data']['title'],
        "NumberOfPrompts": len(prompts),
        "TokensOfPrompts": sum(get_num_tokens_from_string(p) for p in prompts),
        "TokensOfAnswers": answer_tokens,
        "Model": model,
        "Conversations": conversations,
        "HTMLContent": str(soup)
    }

# Função main que executa tudo


async def main():
    base_folder = "data"
    all_urls = []

    # Caminha por todas as subpastas de `data/`
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".csv"):
                csv_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(csv_path)
                    if 'URL' in df.columns:
                        urls = df['URL'].dropna().tolist()
                        all_urls.extend(urls)
                    else:
                        print(f"Coluna 'url' não encontrada em {csv_path}")
                except Exception as e:
                    print(f"❌ Erro ao ler {csv_path}: {e}")

    # Remove duplicadas (opcional)
    all_urls = list(set(all_urls))

    # Inicia o navegador corretamente
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        try:
            for url in all_urls:
                mention = "Extração das subpastas"
                resultado = await obtain_from_chatgpt_sharing(browser, url, mention)
                print(json.dumps(resultado, indent=2, ensure_ascii=False))
        finally:
            await browser.close()

# Executa o script
if __name__ == "__main__":
    asyncio.run(main())
