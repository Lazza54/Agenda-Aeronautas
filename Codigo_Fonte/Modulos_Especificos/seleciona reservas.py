##### ------------- ESTE CÓDIGO SUMARIZA RESERVAS POR PERÍODO SELECIONADO

import csv
import pandas as pd
import numpy as np
import os
#from Tools.scripts.dutree import display
from datetime import datetime
from tkinter import filedialog

path = filedialog.askopenfilename()
print(path)

tabela = pd.read_csv(path, sep=",")
#print(tabela)

###--------- VARIÁVEL COM AS RESERVAS EXISTENTE
var_reservas=[]
var_reservas=[
'RE', 
'RES',
'R0',
'R04',
'R05',
'R06',
'R07',
'R08',
'R09',
'R10',
'R11',
'R12',
'R13',
'R15',
'R16',
'R17',
'R18',
'R19',
'R21',
'R22',
]

reunioes = []
reunioes = [
'REU',
'ROP',  
]

# DATAFRAME QUE CONTEM APENAS LINHAS DE RESERVA
reservas = tabela[tabela['Activity'].str[0:3] != 'REU'].copy()
#reservas = tabela[tabela['Activity'] in var_reservas].copy()
print(reservas)

# APAGAR AS COLUNAS DE REUNIÃO
index_names = reservas[reservas['Activity'] == 'REU'].index
reservas.drop(index_names, inplace=True)

# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS
#reservas['Operacao'] = pd.to_timedelta(reservas['Operacao'], format='%HH:%MM:SS')
#reservas['Diurno'] = pd.to_timedelta(reservas['Diurno'], format='%HH:%MM:SS')
#reservas['Noturno'] = pd.to_timedelta(reservas['Noturno'], format='%HH:%MM:SS')
#reservas['Especial'] = pd.to_timedelta(reservas['Especial'], format='%HH:%MM:SS')
#reservas['Especial Noturno'] = pd.to_timedelta(reservas['EspecialNoturno'], format='%HH:%MM:SS')

soma_reserva_diurna = reservas['Operacao'].sum()
soma_reserva_noturna = reservas['Noturno'].sum()
soma_reserva_especial = reservas['Especial'].sum()
soma_reserva_especial_noturna = reservas['EspecialNoturno'].sum()

print(' TOTAL RESERVA DIURNA:               ', soma_reserva_diurna)
print(' TOTAL RESERVA NOTURNA:              ', soma_reserva_noturna)
print(' TOTAL RESERVA ESPECIAL:             ', soma_reserva_especial)
print(' TOTAL RESERVA ESPECIAL NOTURNA:     ', soma_reserva_especial_noturna)

print(reservas)

reservas.to_csv(path_or_buf=os.path.join(path_to_data, "calculos_reservas_e_ricardo_lazzarini.csv"), index=False)