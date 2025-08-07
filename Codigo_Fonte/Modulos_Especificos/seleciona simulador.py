import csv
from datetime import datetime
import pandas as pd
import numpy as np
import os
from Tools.scripts.dutree import display

path_to_data = "/"

tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023.csv", sep=",")

# DATAFRAME QUE CONTEM APENAS LINHAS DE RESERVA
simulador = tabela[tabela['Activity'].str[2] == 'X'].copy()

# APAGAR AS COLUNAS DE REUNIÃO
index_names = simulador[simulador['Activity'] == 'REX-I'].index
simulador.drop(index_names, inplace=True)

# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS
simulador['Operacao'] = pd.to_timedelta(simulador['Operacao'])
simulador['Diurno'] = pd.to_timedelta(simulador['Diurno'])
simulador['Noturno'] = pd.to_timedelta(simulador['Noturno'])
simulador['Especial'] = pd.to_timedelta(simulador['Especial'])
simulador['Especial Noturno'] = pd.to_timedelta(simulador['EspecialNoturno'])

soma_simulador_diurna = simulador['Diurno'].sum()
soma_simulador_noturna = simulador['Noturno'].sum()
soma_simulador_especial = simulador['Especial'].sum()
soma_simulador_especial_noturna = simulador['EspecialNoturno'].sum()

print(' TOTAL SIMULADOR DIURNO:               ', soma_simulador_diurna)
print(' TOTAL SIMULADOR NOTURNO:              ', soma_simulador_noturna)
print(' TOTAL SIMULADOR ESPECIAL:             ', soma_simulador_especial)
print(' TOTAL SIMULADOR ESPECIAL NOTURNA:     ', soma_simulador_especial_noturna)
#
print(simulador)

simulador.to_csv(path_or_buf=os.path.join(path_to_data, "calculos_simulador_e_ricardo_lazzarini.csv"), index=False)