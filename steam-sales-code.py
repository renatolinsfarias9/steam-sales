import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from google.cloud import bigquery

# Configuração do ChromeDriver
base_path = os.path.dirname(os.path.abspath(__file__))
driver_path = os.path.join(base_path, 'chromedriver.exe')

if not os.path.isfile(driver_path):
    raise FileNotFoundError(f"Não foi possível encontrar o chromedriver.exe em {driver_path}")

service = Service(driver_path)
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')  # Executa com interface gráfica ativa

driver = webdriver.Chrome(service=service, options=options)

# URL do site SteamDB Sales
url = "https://steamdb.info/sales/"
driver.get(url)

# Adicionar WebDriverWait para garantir o carregamento inicial da tabela
wait = WebDriverWait(driver, 5)
try:
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[2]/table/tbody")))
except Exception as e:
    driver.quit()
    raise RuntimeError("Os dados não carregaram no tempo esperado.") from e

# Função para buscar elementos com XPath dinâmico e rolar a página
def get_column_data(base_xpath, column_name):
    data = []
    index = 1
    while True:
        try:
            full_xpath = base_xpath.format(index=index)
            element = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, full_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView();", element)
            data.append(element.text)
            index += 1
        except Exception:
            break
    print(f"{column_name}: {len(data)} itens coletados nesta página.")
    return data

# Configurações dos XPaths base para cada coluna
xpaths = {
    "Nome": "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[2]/table/tbody/tr[{index}]/td[3]/a",
    "Porcentagem": "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[2]/table/tbody/tr[{index}]/td[4]",
    "Preço": "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[2]/table/tbody/tr[{index}]/td[5]",
    "Avaliação": "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[2]/table/tbody/tr[{index}]/td[6]",
    "Liberado": "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[2]/table/tbody/tr[{index}]/td[7]",
    "Termina": "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[2]/table/tbody/tr[{index}]/td[8]",
    "Iniciado": "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[2]/table/tbody/tr[{index}]/td[9]",
}

# Coletar dados
all_data = {col: [] for col in xpaths.keys()}
pagination_buttons_xpath = "/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[3]/div[2]/nav/button"
pagination_buttons = driver.find_elements(By.XPATH, pagination_buttons_xpath)
total_pages = len(pagination_buttons) - 2

for page_index in range(3, total_pages + 3):
    for col, xpath in xpaths.items():
        all_data[col].extend(get_column_data(xpath, col))
    next_page_button = f"/html/body/div[4]/div[1]/div[2]/div[1]/div[2]/div[4]/div/div[3]/div[2]/nav/button[{page_index}]"
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, next_page_button))
        )
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(3)
    except Exception:
        print("Erro ao tentar navegar para a próxima página.")
        break

# Criar DataFrame
df = pd.DataFrame(all_data)
driver.quit()

# Configuração do BigQuery
def upload_to_bigquery(df, project_id, dataset_id, table_id):
    client = bigquery.Client()
    # Corrigido o formato do ID da tabela
    table_full_id = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Sobrescrever tabela, se existir
    )
    job = client.load_table_from_dataframe(df, table_full_id, job_config=job_config)
    job.result()  # Aguarda conclusão do upload
    print(f"Tabela {table_full_id} criada com sucesso!")

# Configurações do BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/renat/Documents/beAnalytic/beanalytic-442411-dfdba22cf1dc.json"  # Caminho para o JSON de credenciais
PROJECT_ID = "beanalytic-442411"
DATASET_ID = "SteamSales"  # Nome correto do dataset
TABLE_ID = "GameDiscounts"  # Nome correto da tabela

# Enviar para o BigQuery
upload_to_bigquery(df, PROJECT_ID, DATASET_ID, TABLE_ID)
