from datetime import datetime, timedelta
from pendulum import now, yesterday, tomorrow, timezone
import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings("ignore")
path_to_data = "/"
tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023_FASE_C.csv", sep=",")

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 15)

### ESTABELECER A DATA PARA EMISSÃO DO RELATÓRIO
var_datainicial = '2018-01-10' #input(' Digite a data pesquisa; exemplo 2017-11-11: ')

## FILTRAR O DIA SELECIONADO ACIMA
# CONVERTER A COLUNA 'Checkin' EM DATETIME
filtrada_mes = tabela.loc[(tabela['Checkin'].str.contains(var_datainicial))].copy()
filtrada_mes['Operacao'] = pd.to_timedelta(filtrada_mes['Operacao'])
print('____________________ ATIVIDADE DIÁRIA NA ESCALA -----------------------------------')

print(filtrada_mes[['Activity', 'Start', 'Dep', 'Arr', 'End', 'Operacao', 'Repouso', 'Jornada', 'Noturno', 'Especial', 'EspecialNoturno' ]])

## IMPRIMIR OS LIMITES REGULAMENTARES NA LEGISLAÇÃO PARA A TAREFA DIÁRIA
# BUSCAR DEV ONDE SEJAM FEITOS OS CÁLCULOS DE LIMITES DE HORAS DE VOO E JORNADA DE TRABALHO
print('----------------------------------------------------------------------------------------------------------')
print('============================== CALCULOS DE ATIVIDADE DIÁRIA ==============================================')
print('------------------------------                              ----------------------------------------------')

print(' Limite de voo dia, tripulaçao SIMPLES = 8:00   ')
operacao_dia = filtrada_mes['Operacao'].sum()
operacao_dia = str(operacao_dia)
print('Você voou no dia = ', operacao_dia)
print('----------------------------------------------------------------------------------------------------------')

print(' Limite de voo dia, tripulaçao COMPOSTA = 14:00  ')
operacao_dia = filtrada_mes['Operacao'].sum()
operacao_dia = str(operacao_dia)
print('Você voou no dia =', operacao_dia)
print('----------------------------------------------------------------------------------------------------------')

print(' Limite de voo dia, tripulaçao REVEZAMENTO = 16:00')
operacao_dia = filtrada_mes['Operacao'].sum()
operacao_dia = str(operacao_dia)
print('Você voou no dia =', operacao_dia)
print('----------------------------------------------------------------------------------------------------------')

print(' Limite de jornada para o dia, tripulaçao SIMPLES =      11:00')
jornada_dia = filtrada_mes['Jornada'].iloc[-1]
jornada_dia = str(jornada_dia)
print(' Sua jornada no dia foi =', jornada_dia)
print('----------------------------------------------------------------------------------------------------------')

print(' Limite de jornada para o dia, tripulaçao COMPOSTA =    16:00')
jornada_dia = filtrada_mes['Jornada'].iloc[-1]
jornada_dia = str(jornada_dia)
print(' Sua jornada no dia foi =', jornada_dia)
print('----------------------------------------------------------------------------------------------------------')

print(' Limite de jornada para o dia, tripulaçao REVEZAMENTO = 20:00')
jornada_dia = filtrada_mes['Jornada'].iloc[-1]
jornada_dia = str(jornada_dia)
print(' Sua jornada no dia foi =', jornada_dia)
print('----------------------------------------------------------------------------------------------------------')

print(' Seu repouso previsto será de = ', filtrada_mes['Repouso'].iloc[-1])
print('----------------------------------------------------------------------------------------------------------')
print(' Foram realizados ', len(filtrada_mes), '  pousos')
print('----------------------------------------------------------------------------------------------------------')

var_sextodia = datetime.strptime(filtrada_mes['Checkin'].iloc[0], '%Y-%m-%d %H:%M:%S')
print(' O limite do seu sexto período será = ', (var_sextodia + timedelta(+4.5)))
print('----------------------------------------------------------------------------------------------------------')
