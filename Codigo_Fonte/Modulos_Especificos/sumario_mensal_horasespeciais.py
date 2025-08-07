import pandas as pd
from tkinter import filedialog

path = filedialog.askopenfilename()
print(path)

tabela = pd.read_csv(path, sep=",")

# FILTRAR OS DADOS PELA DATA SOLICITADA

var_datainicial = input(' Digite o ano e mes para pesquisa; exemplo 2017-11 : ')

sumario_horasespeciais_mensais = tabela[tabela['Checkin'].str.contains(var_datainicial)].copy()

# SOMAR OS VALORES CONTIDOS EM OPERAÇÃO E TOTALIZAR
# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS

sumario_horasespeciais_mensais['Especial'] = pd.to_timedelta(sumario_horasespeciais_mensais['Especial'])

soma_sumario_horasespeciais_mensais_diurna = sumario_horasespeciais_mensais['Especial'].sum()

print(' HORAS ESPECIAIS DIURNAS :               ', soma_sumario_horasespeciais_mensais_diurna)
