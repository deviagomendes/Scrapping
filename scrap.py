import csv
import base64
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Função para formatar o código com pontos
def format_code(parts):
    return f"{parts[0]}.{parts[1]}.{parts[2]}.{parts[3]}.{parts[4]}.{parts[5]}"

# Função para salvar o PDF com um nome específico
def save_pdf(driver, filename):
    print_options = {
        "paperWidth": 8.27,  # A4 paper width in inches
        "paperHeight": 11.69, # A4 paper height in inches
        "scale": 0.5,  # Scale the content to 50%
        "printBackground": True,
        "landscape": False
    }
    # Salvar a página como PDF e obter o conteúdo em base64
    result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
    pdf_data = base64.b64decode(result['data'])
    
    # Especificar o local onde salvar o PDF
    save_path = os.path.join(results_dir, filename)
    with open(save_path, "wb") as f:
        f.write(pdf_data)

# Função para extrair os totais do HTML usando busca por texto
def extract_totals(driver):
    try:
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        
        # Busca pelos totais na página
        total_vencidos_index = body_text.find('Total vencidos')
        total_a_vencer_index = body_text.find('Total a vencer')
        
        # Extrair valores com base no texto encontrado
        if total_vencidos_index != -1:
            total_vencidos_start = body_text.find('R$', total_vencidos_index)
            total_vencidos_end = body_text.find('\n', total_vencidos_start)
            total_vencidos = body_text[total_vencidos_start:total_vencidos_end].strip()
        else:
            total_vencidos = "N/A"
        
        if total_a_vencer_index != -1:
            total_a_vencer_start = body_text.find('R$', total_a_vencer_index)
            total_a_vencer_end = body_text.find('\n', total_a_vencer_start)
            total_a_vencer = body_text[total_a_vencer_start:total_a_vencer_end].strip()
        else:
            total_a_vencer = "N/A"
        
        return total_vencidos, total_a_vencer
    except Exception as e:
        print(f"Erro ao extrair os totais: {e}")
        return "N/A", "N/A"

# Criar pasta de resultados se não existir
documents_dir = os.path.expanduser("~/Documentos")
results_dir = os.path.join(documents_dir, "results")
os.makedirs(results_dir, exist_ok=True)

# Configurando as opções do Chrome
options = ChromeOptions()
options.add_argument("--start-maximized")  # Inicia o Chrome em tela cheia
options.add_experimental_option("prefs", {
    "printing.print_preview_sticky_settings.appState": json.dumps({
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        "pageSize": "A4",
        "scaling": "DEFAULT",
        "isHeaderFooterEnabled": False,
        "isBackgroundGraphicsEnabled": False,
    })
})
options.add_argument("--kiosk-printing")  # Permite impressão sem diálogo

# Inicializando o Chrome WebDriver com as opções configuradas
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Carregar o arquivo CSV original e criar o novo CSV com a coluna de totais
try:
    with open('dados.csv', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        rows = list(csvreader)  # Carregar todas as linhas do CSV original
        header = rows[0]  # Cabeçalho do CSV original
        data_rows = rows[1:]  # Dados do CSV original

        # Criar um novo arquivo CSV para resultados com totais
        results_csv_path = os.path.join(results_dir, 'resultados.csv')
        with open(results_csv_path, mode='w', newline='', encoding='utf-8') as results_file:
            results_writer = csv.writer(results_file)
            results_writer.writerow(header + ['Total Vencidos', 'Total a Vencer'])  # Adiciona o cabeçalho com as novas colunas

            try:
                for row in data_rows:
                    # Formatar o código com as partes
                    code_base = format_code(row[:6])
                    
                    # Tentar com final .0 e .1
                    for suffix in ['.0', '.1']:
                        code = f"{code_base}{suffix}"
                        
                        driver.get("https://e-gov.betha.com.br/cdweb/resource.faces?params=FzKTkvNNaxrljKCe99HGiFN24zbCAH8Y")
                        driver.implicitly_wait(5)

                        try:
                            # Interagir com os elementos da página
                            element = driver.find_element(By.CLASS_NAME, 'inscImobiliaria')
                            driver.implicitly_wait(5)
                            element.click()

                            element = driver.find_element(By.ID, 'mainForm:inscrImob')
                            element.send_keys(code)
                            element.send_keys(Keys.ENTER)
                            
                            # Verificar se há erro na página imediatamente após enviar a consulta
                            try:
                                error_element = driver.find_element(By.CSS_SELECTOR, '.fieldError')
                                if error_element:
                                    print(f"Erro detectado com código {code}. Tentando com {code_base}.1")
                                    continue
                            except:
                                pass

                            # Esperar o carregamento dos resultados
                            WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located((By.ID, 'totais'))
                            )

                            # Se não houver erro, esperar 3 segundos e salvar o PDF
                            time.sleep(3)  # Esperar 3 segundos para garantir que o conteúdo esteja totalmente carregado
                            filename = f"resultado_{code}.pdf"
                            save_pdf(driver, filename)
                            total_vencidos, total_a_vencer = extract_totals(driver)
                            results_writer.writerow(row + [total_vencidos, total_a_vencer])
                            print(f"Consulta bem-sucedida com código {code}. PDF salvo como {filename} e resultado salvo no CSV.")
                            break
                        except Exception as e:
                            print(f"Erro na consulta com código {code}: {e}")

            finally:
                driver.quit()
except Exception as e:
    print(f"Erro ao processar o arquivo CSV: {e}")
