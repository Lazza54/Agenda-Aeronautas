import csv
from datetime import datetime
import pandas as pd
import os
from Tools.scripts.dutree import display

path_to_data = "/"

tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023.csv", sep=",")

# DATAFRAME QUE CONTEM APENAS LINHAS DE RESERVA
plantoes = tabela[tabela['Activity'].str[0] == 'S'].copy()

# APAGAR AS COLUNAS DE REUNIÃO
index_names = plantoes[plantoes['Activity'] == 'SNA'].index
plantoes.drop(index_names, inplace=True)

# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS
plantoes['Operacao'] = pd.to_timedelta(plantoes['Operacao'])
plantoes['Diurno'] = pd.to_timedelta(plantoes['Diurno'])
plantoes['Noturno'] = pd.to_timedelta(plantoes['Noturno'])
plantoes['Especial'] = pd.to_timedelta(plantoes['Especial'])
plantoes['Especial Noturno'] = pd.to_timedelta(plantoes['EspecialNoturno'])

soma_plantoes_diurna = plantoes['Operacao'].sum()
soma_plantoes_noturna = plantoes['Noturno'].sum()
soma_plantoes_especial = plantoes['Especial'].sum()
soma_plantoes_especial_noturna = plantoes['EspecialNoturno'].sum()

print(' TOTAL PLANTÃO DIURNO:               ', soma_plantoes_diurna)
print(' TOTAL PLANTÃO NOTURNO:              ', soma_plantoes_noturna)
print(' TOTAL PLANTÃO ESPECIAL:             ', soma_plantoes_especial)
print(' TOTAL PLANTÃO ESPECIAL NOTURNA:     ', soma_plantoes_especial_noturna)

print(plantoes)

plantoes.to_csv(path_or_buf=os.path.join(path_to_data, "calculos_plantoes_sobreavisos_e_ricardo_lazzarini.csv"), index=False)