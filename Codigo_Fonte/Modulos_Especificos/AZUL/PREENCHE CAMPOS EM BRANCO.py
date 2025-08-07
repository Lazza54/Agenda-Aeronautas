# este código preenche os campos de checkin em branco com o valor do checkin anterior, para atividades de não voo e reservas
# le o csv gerado _PRIMEIRA_VERSAO  e gera um novo _SEM_COLUNAS_EM_BRANCO.csv  

#! pip install tabula-py
#! pip install missingno

#from tabula.io import read_pdf
#import tabula
import numpy as np
import pandas as pd

#import missingno
from dateutil import tz
from datetime import timedelta, time, datetime, date, tzinfo, timezone
import warnings
warnings.filterwarnings("ignore")

from tkinter import filedialog
from tqdm import tqdm

path = filedialog.askopenfilename()

df_merged = pd.read_csv(path, sep=',')

pd.set_option('display.max_rows', None)

var_temp_checkin = ''
reservas=[]
reservas=[
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
##### TODOS OS CHECKIN EM BRANCO TERÃO '-'
df_merged['Checkin'].fillna("-", inplace=True)

start_row = 0 
for i in tqdm(range(start_row, len(df_merged)), desc="Processando"):
    
    ##### AS ATIVIDADES DE NÃO VOO DEVEM TER O MESMO HORÁRIO DE CHECKIN E START
    if df_merged['Activity'].iloc[i][0:3] == 'BUS':
      var_temp_checkin = df_merged['Checkin'].iloc[i]
      print(var_temp_checkin)
    
      #### SE 'Activity' = 'AD' E 'Checkout' = '-' igualar checkout a end
    
      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

for i in range(len(df_merged)):
    
    if df_merged['Activity'].iloc[i] in reservas:
        var_temp_checkin = df_merged['Checkin'].iloc[i]
        print(' ENTREI EM RESERVA')    
        
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin

# TODAS AS COLUNAS QUE TIVEREM VALOR 00:00 OU 00:00:00 SERÃO SUBSTITUIDAS POR '-'
df_merged.replace('00:00', '-', inplace=True)
df_merged.replace('00:00:00', '-', inplace=True)

df_merged.reset_index(drop=True, inplace=True)
    
print(len(df_merged))

path = path.replace('_PRIMEIRA_VERSAO.csv', '_SEM_COLUNAS_EM_BRANCO.csv')
print(path)

df_merged.to_csv(path, index=False)

print('TAREFA CONCLUIDA')