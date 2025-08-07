# objetivo: extrair tabela com principais aeroportos do Brasil
# https://www.monolitonimbus.com.br/mapa-com-aeroportos-e-siglas-icaoiata/

import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.monolitonimbus.com.br/mapa-com-aeroportos-e-siglas-icaoiata/'

# Fazendo a requisição da página
page = requests.get(url)

# Criando o objeto BeautifulSoup
soup = BeautifulSoup(page.content, 'html.parser')

# Encontrando a tabela específica na página
tabela = soup.find('table')

# Verificando se a tabela foi encontrada
if tabela is None:
    print("Tabela não encontrada na página.")
else:
    # Extraindo os dados da tabela
    data = []
    for row in tabela.find_all('tr'):
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if cols:
            data.append(cols)

    # Extraindo os cabeçalhos da tabela
    headers = []
    for th in tabela.find_all('th'):
        headers.append(th.text.strip())

    # Criando o DataFrame
    df_aeroportos_brasil = pd.DataFrame(data, columns=headers)

    # Exibindo o DataFrame
    print(df_aeroportos_brasil)
    
    # Salvando o DataFrame em um arquivo CSV
    df_aeroportos_brasil.to_csv('aeroportos_brasil.csv', index=False)
    print("Arquivo CSV salvo com sucesso.")