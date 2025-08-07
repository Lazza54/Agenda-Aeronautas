import requests
from bs4 import BeautifulSoup
import json
import string

# Gerar todos os prefixos de A a Z, incluindo combinações duplas (AA, AB, ..., ZZ)
prefixos = list(string.ascii_uppercase) + [a + b for a in string.ascii_uppercase for b in string.ascii_uppercase]

base_url = "https://airportcodes.aero/iata/"
aeroportos = []

for prefixo in prefixos:
    url = f"{base_url}{prefixo}"
    response = requests.get(url)
    if response.status_code != 200:
        continue  # Pula se a página não existir

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if not table:
        continue

    rows = table.find_all("tr")[1:]  # Ignora cabeçalho
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 3:
            icao = cells[0].get_text(strip=True)
            iata = cells[1].get_text(strip=True)
            name = cells[2].get_text(strip=True)
            aeroportos.append({
                "ICAO": icao,
                "IATA": iata,
                "Name": name
            })

# Salvar como JSON
with open("todos_aeroportos.json", "w", encoding="utf-8") as f:
    json.dump(aeroportos, f, ensure_ascii=False, indent=2)

print(f"Total de aeroportos extraídos: {len(aeroportos)}")