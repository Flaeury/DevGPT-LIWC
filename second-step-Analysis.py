import csv


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


def analisar_mensagem_liwc(mensagem, liwc_dict):
    categorias_contadas = {i: 0 for i in range(1, 50)}
    for palavra in mensagem.split():
        palavra = palavra.lower().strip(",.?!;:'\"()[]{}")
        if palavra in liwc_dict:
            for categoria in liwc_dict[palavra]:
                categorias_contadas[categoria] += 1
    return categorias_contadas


def processar_arquivo(input_csv, output_csv, liwc_dict_path):
    liwc_dict = carregar_dicionario_liwc(liwc_dict_path)

    with open(input_csv, "r", encoding="utf-8") as infile, open(output_csv, "w", encoding="utf-8", newline="") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["LIWC_User", "LIWC_ChatGPT"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            user_analysis = analisar_mensagem_liwc(
                row["UserMessage"], liwc_dict)
            bot_analysis = analisar_mensagem_liwc(
                row["ChatGPTMessage"], liwc_dict)

            row["LIWC_User"] = sum(user_analysis.values())
            row["LIWC_ChatGPT"] = sum(bot_analysis.values())

            writer.writerow(row)


if __name__ == "__main__":
    processar_arquivo("CSV/extracted_data.csv",
                      "CSV/analyzed_data.csv", "LIWC.dic")
