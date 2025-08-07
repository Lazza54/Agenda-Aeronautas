# ESTE CÓDIGO ALTERA O FORMATO DAS COLUNAS DATETIME PARA HORA NORMAL
##### GRAVAR ARQUIVO FINAL
# path = path.replace('\_CALCULOS_ADICIONAIS SAI \_DATAS_CORRIGIDAS')

import numpy as np
import pandas as pd
from datetime import timedelta
import warnings
import missingno
from tkinter import filedialog
from tabulate import tabulate
from tqdm import tqdm

warnings.filterwarnings("ignore")

##### SELECIONAR O ARQUIVO DESEJADO
path = filedialog.askopenfilename()

##### LEITURA DO ARQUIVO SELECIONADO
escala = pd.read_csv(path, encoding="utf-8", sep=',')

print(path)

# DESCREVER CADA COLUNA
print(escala.columns)

##### RETIRA O 'NaN' DE TODAS AS COLUNAS
escala['Operacao'].fillna('00:00:00', inplace = True)
escala['Tempo Solo'].fillna('00:00:00', inplace = True)
escala['Jornada'].fillna('00:00:00', inplace = True)
escala['Repouso'].fillna('00:00:00', inplace = True)
escala['Repouso Extra'].fillna('00:00:00', inplace = True)
escala['Diurno'].fillna('00:00:00', inplace = True)
escala['Noturno'].fillna('00:00:00', inplace = True)
escala['Especial'].fillna('00:00:00', inplace = True)
escala['EspecialNoturno'].fillna('00:00:00', inplace = True)

#######
# EXCLUIR AS COLUNAS AcVer,Prefix, DD, CAT, Crew do dataframe escala
escala = escala.drop(columns=['AcVer', 'Prefix', 'DD', 'CAT', 'Crew'])

start_row = 0 
for i in tqdm(range(start_row, len(escala)), desc="Processando"):  
  str_tempo = (escala['Operacao'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['Operacao'].iloc[i] = horas_minutos

  str_tempo = (escala['Tempo Solo'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['Tempo Solo'].iloc[i] = horas_minutos

  str_tempo = (escala['Jornada'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['Jornada'].iloc[i] = horas_minutos

  str_tempo = (escala['Repouso'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['Repouso'].iloc[i] = horas_minutos

  str_tempo = (escala['Repouso Extra'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['Repouso Extra'].iloc[i] = horas_minutos

  str_tempo = (escala['Diurno'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['Diurno'].iloc[i] = horas_minutos

  str_tempo = (escala['Noturno'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['Noturno'].iloc[i] = horas_minutos
  
  str_tempo = (escala['Especial'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['Especial'].iloc[i] = horas_minutos
  
  str_tempo = (escala['EspecialNoturno'].iloc[i])
  tempo = pd.Timedelta(str_tempo)
  # Obtendo o total de horas e minutos
  total_horas = tempo.total_seconds() // 3600  # Total de horas
  total_minutos = (tempo.total_seconds() % 3600) // 60  # Total de minutos
  # Formatando em HH:MM
  horas_minutos = f"{int(total_horas):02}:{int(total_minutos):02}"
  escala['EspecialNoturno'].iloc[i] = horas_minutos

##### MOSTRAR E GRAVAR ARQUIVO FINAL COM TODOS OS CÁLCULOS
colunas = ["Operacao", "Tempo Solo", "Jornada", "Repouso", "Repouso Extra", "Diurno", "Noturno", "Especial", "EspecialNoturno"]
print(tabulate(escala[colunas].head(), headers= 'firstrow', tablefmt='fancy_grid'))

##### GRAVAR ARQUIVO FINAL
path = path.replace('_CALCULOS_ADICIONAIS.csv', '_DATAS_CORRIGIDAS.csv')

escala.info()

escala.to_csv(path, index=False)

print(' TAREFA REALIZADA COM SUCESSO :')  