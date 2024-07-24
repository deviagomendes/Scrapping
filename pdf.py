import pdfplumber
import csv
import re

# Função para processar o texto de uma página do PDF
def process_page_text(text):
    lines = text.split('\n')
    data = []
    for line in lines:
        # Ignorar linhas que não contêm dados
        if re.match(r'^\d{5}', line):
            columns = line.split()
            if len(columns) >= 9:
                data.append(columns)
    return data

# Função principal para converter PDF para CSV
def pdf_to_csv(pdf_path, csv_path):
    with pdfplumber.open(pdf_path) as pdf:
        all_data = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                page_data = process_page_text(text)
                all_data.extend(page_data)

        # Escrever dados em um arquivo CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            # Escrever cabeçalho do CSV
            writer.writerow(['BIC', 'DI', 'SE', 'ZO', 'QUA', 'LOT', 'UNI', 'NOME', 'QUADRA', 'LOTE', 'MATRÍCULA', 'BAIRRO'])
            # Escrever linhas de dados
            writer.writerows(all_data)

# Caminho para o arquivo PDF e CSV
pdf_path = 'L:\Documentos\Scrapping\pdf.pdf'
csv_path = 'L:\Documentos\Scrapping\dados.csv'

# Chamar a função para converter PDF para CSV
pdf_to_csv(pdf_path, csv_path)
