async def fetch_page(browser, url):
    page = await browser.newPage()
    await page.setUserAgent(random.choice(USER_AGENTS))
    response = await page.goto(url, waitUntil='domcontentloaded', timeout=200000)
    if response.status != 200:
        await page.close()
        return response.status
    content = await page.content()
    await page.close()
    return content


async def obtain_from_chatgpt_sharing(url, mention):
    revised_url = url.replace(
        'https://chat.openai.com/share/', 'https://chatgpt.com/share/')
    content = await fetch_page(browser, revised_url)
    if isinstance(content, int):
        return {
            "URL": url,
            "Mention": mention,
            "Status": content,
        }
    else:

        try:
            soup = BeautifulSoup(content, "html.parser")
            data = json.loads(
                soup.find('script', type='application/json').text)
        except JSONDecodeError:
            content = await fetch_page(browser, revised_url)
            if isinstance(content, int):
                return {
                    "URL": url,
                    "Mention": mention,
                    "Status": content,
                }
            else:
                try:
                    soup = BeautifulSoup(content, "html.parser")
                    data = json.loads(
                        soup.find('script', type='application/json').text)
                except JSONDecodeError:
                    return {
                        "URL": url,
                        "Mention": mention,
                        "Status": 404,
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
        for mapping in values:
            if 'message' in mapping:
                if 'model_slug' in mapping['message']['metadata'] and model is None:
                    if "text-davinci-002-render-sha" in mapping['message']['metadata']['model_slug']:
                        model = 'GPT-3.5'
                    else:
                        model = mapping['message']['metadata']['model_slug'].upper(
                        )
                if mapping['message']['content']['content_type'] == 'code':
                    continue
                if mapping['message']['author']['role'] == 'user':
                    prompt = mapping['message']['content']['parts'][0]
                    prompts.append(prompt)
                    is_assistant = False
                if mapping['message']['author']['role'] == 'assistant':
                    if 'parts' not in mapping['message']['content']:
                        continue
                    if is_assistant and len(conversations) > 0:
                        last_answer = conversations[-1]['Answer']
                        last_code_blocks = conversations[-1]['ListOfCode']
                        answer = mapping['message']['content']['parts'][0]
                        answer_tokens += get_num_tokens_from_string(answer)
                        code_contents = re.findall(
                            r'```[\s\S]*?```', answer, re.DOTALL)
                        code_blocks = []
                        for code_content in code_contents:
                            code_type = code_content.split('\n')[0][3:]
                            code_type = code_type if code_type != '' else None
                            answer = answer.replace(
                                code_content, f"[CODE_BLOCK_{index}]")
                            code_content = '\n'.join(
                                code_content.split('\n')[1:-1])
                            code_block = {
                                "ReplaceString": f"[CODE_BLOCK_{index}]",
                                "Type": code_type,
                                "Content": code_content
                            }
                            code_blocks.append(code_block)
                            index += 1
                        answer = last_answer + '\n' + answer
                        conversations[-1]['Answer'] = answer
                        last_code_blocks.extend(code_blocks)
                        conversations[-1]['ListOfCode'] = code_blocks
                    else:
                        answer = mapping['message']['content']['parts'][0]
                        answer_tokens += get_num_tokens_from_string(answer)
                        code_contents = re.findall(
                            r'```[\s\S]*?```', answer, re.DOTALL)
                        code_blocks = []
                        index = 0
                        for code_content in code_contents:
                            code_type = code_content.split('\n')[0][3:]
                            code_type = code_type if code_type != '' else None
                            answer = answer.replace(
                                code_content, f"[CODE_BLOCK_{index}]")
                            code_content = '\n'.join(
                                code_content.split('\n')[1:-1])
                            code_block = {
                                "ReplaceString": f"[CODE_BLOCK_{index}]",
                                "Type": code_type,
                                "Content": code_content
                            }
                            code_blocks.append(code_block)
                            index += 1
                    is_assistant = True

            if answer is not None and prompt is not None:
                turn += 1
                conversations.append(
                    {
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
            "DateOfConversation": datetime.datetime.fromtimestamp(data['props']['pageProps']['serverResponse']['data']['create_time']).strftime('%B %-d, %Y'),
            "Title": data['props']['pageProps']['serverResponse']['data']['title'],
            "NumberOfPrompts": len(prompts),
            "TokensOfPrompts": sum([get_num_tokens_from_string(prompt) for prompt in prompts]),
            "TokensOfAnswers": answer_tokens,
            "Model": model,
            "Conversations": conversations,
            "HTMLContent": str(soup)
        }
