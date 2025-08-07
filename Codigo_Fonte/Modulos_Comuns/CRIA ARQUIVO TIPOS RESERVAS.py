import json

# Gerar os códigos R01 a R24
reservas_numericas = [f"R{str(i).zfill(2)}" for i in range(1, 25)]

# Adicionar os códigos extras
reservas_extras = ["RES", "REX", "R0", "RF1", "RF2", "RF3", "RF4", "RF5", "RF6", "RF7", "RF8", "RF9"]

# Combinar todos os tipos de reserva
l_reservas = reservas_numericas + reservas_extras

# Estrutura final do JSON
dados = {
    "tipos_reserva": l_reservas
}

# Salvar em um arquivo JSON
with open("tipos_reserva.json", "w", encoding="utf-8") as arquivo:
    json.dump(dados, arquivo, indent=4, ensure_ascii=False)

print("Arquivo 'tipos_reserva.json' criado com sucesso!")

# copiar o arquivo JSON para o diretório de trabalho
import shutil
shutil.copy("tipos_reserva.json", "G:/PROJETOS PYTHON/aeronautas_azul/ARQUIVOS COMUNS/tipos_reserva.json")

