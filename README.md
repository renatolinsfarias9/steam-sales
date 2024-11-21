# Steam Sales Data Pipeline

Este repositório contém a solução para o case técnico proposto pela **beAnalytic** para a vaga de Engenheiro de Dados Júnior. A solução inclui a extração de dados de promoções do site [SteamDB Sales](https://steamdb.info/sales/), armazenamento no **Google BigQuery** e a conexão desses dados com uma planilha do **Google Sheets**, que está publicamente acessível.

---

## 🛠️ Funcionalidades

1. **Extração de Dados**:
   - Os dados das promoções do SteamDB são extraídos usando **Selenium** para automatizar o navegador.
   - As informações coletadas incluem:
     - Nome do jogo.
     - Porcentagem de desconto.
     - Preço final.
     - Avaliação.
     - Data de início e término da promoção.

2. **Armazenamento no BigQuery**:
   - Os dados extraídos são armazenados em uma tabela no **Google BigQuery**, permitindo consultas escaláveis e rápidas.
   - O nome do dataset é `SteamSales` e a tabela é `GameDiscounts`.

3. **Conexão com Google Sheets**:
   - A base de dados armazenada no BigQuery foi conectada a uma planilha do **Google Sheets** para visualização pública.
   - Qualquer pessoa com o link pode acessar a planilha:
     [Acesse a planilha aqui](https://docs.google.com/spreadsheets/d/1iuwkt84pKxbmRQ2VDI64EwVqoeFzsriOu_9jDDTypxg/edit?usp=sharing).

---

## 📁 Estrutura do Repositório

- `steam_sales_code.py`: Código principal para extração, processamento e upload dos dados.
- `chromedriver.exe`: Driver utilizado na automação da extração dos dados com Selenium.
