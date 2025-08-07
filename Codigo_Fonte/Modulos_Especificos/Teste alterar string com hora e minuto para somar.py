import pandas as pd
import os
import openpyxl
from datetime import datetime as dt
from tkinter import filedialog

# Limpar o terminal antes de executar o código
def limpar_terminal():
    # Verificar o sistema operacional e usar o comando apropriado
    if os.name == 'nt':  # Para Windows
        os.system('cls')
    else:  # Para macOS e Linux
        os.system('clear')

limpar_terminal()

# SELECIONAR O ARQUIVO COMPLETO DAS ESCALAS COM TODOS OS CÁLCULOS
path = filedialog.askopenfilename()
tabela = pd.read_csv(path, sep=",")

# SELECIONAR A TABELA QUE POSSUI AS SIGLAS DO SISTEMA SABRE
path = filedialog.askopenfilename()
atividades_pagas = pd.read_excel(path)

atividades_pagas = atividades_pagas.dropna(how="all", axis=0)
atividades_pagas = atividades_pagas.dropna(how="all", axis=1)
atividades_pagas.columns = atividades_pagas.iloc[0]
atividades_pagas = atividades_pagas[1:]

atividades_pagas.reset_index(drop=True, inplace=True)

# Filtrar os valores da coluna1 onde o valor é 'S'
valores_com_S = atividades_pagas[atividades_pagas['PGTO'] == 'S']['SIGLA'].tolist()

##### ------ FILTRAR O DATAFRAME E DEPOIS CONCATENAR 

# Data inicial para filtrar
var_datainicial = '2018-01'

df_filtrado1 = tabela[
    (tabela['Checkin'].str.startswith(var_datainicial)) &
    (tabela['Activity'].isin(valores_com_S))
]

df_filtrado2 = tabela[
    (tabela['Checkin'].str.startswith(var_datainicial)) &
    (tabela['Activity'].str.startswith('AD'))
]

### JUNTAR OS DATAFRAMES FILTRADOS
sumario_horas_mensais = pd.concat([df_filtrado1, df_filtrado2], axis=0)
sumario_horas_mensais = sumario_horas_mensais.sort_values(by='Checkin')

soma_horas_operacao = 0
soma_sumario_horas_mensais_diurna = 0
soma_sumario_horas_mensais_noturna = 0
soma_sumario_horas_especial_diurna = 0
soma_sumario_horas_especial_noturna = 0

for i in range(len(sumario_horas_mensais)):
    hora_operacao = sumario_horas_mensais['Operacao'].iloc[i]
    horas, minutos = map(int, hora_operacao.split(':'))
    sumario_horas_mensais['Operacao'].iloc[i] = (horas * 60) + minutos
    soma_horas_operacao += sumario_horas_mensais['Operacao'].iloc[i]

    hora_diurno = sumario_horas_mensais['Diurno'].iloc[i]  
    horas, minutos = map(int, hora_diurno.split(':'))
    sumario_horas_mensais['Diurno'].iloc[i] = (horas * 60) + minutos
    soma_sumario_horas_mensais_diurna += sumario_horas_mensais['Diurno'].iloc[i]
        
    hora_noturno = sumario_horas_mensais['Noturno'].iloc[i]  
    horas, minutos = map(int, hora_noturno.split(':'))
    sumario_horas_mensais['Noturno'].iloc[i] = (horas * 60) + minutos
    soma_sumario_horas_mensais_noturna += sumario_horas_mensais['Noturno'].iloc[i]

    #sumario_horas_mensais['Especial'] = sumario_horas_mensais['Especial']
    hora_especial_diurna = sumario_horas_mensais['Especial'].iloc[i]  
    horas, minutos = map(int, hora_especial_diurna.split(':'))
    sumario_horas_mensais['Especial'].iloc[i] = (horas * 60) + minutos
    soma_sumario_horas_especial_diurna += sumario_horas_mensais['Especial'].iloc[i]
    
    #sumario_horas_mensais['EspecialNoturno'] = sumario_horas_mensais['EspecialNoturno']
    hora_especial_noturna = sumario_horas_mensais['EspecialNoturno'].iloc[i]  
    horas, minutos = map(int, hora_especial_noturna.split(':'))
    sumario_horas_mensais['EspecialNoturno'].iloc[i] = (horas * 60) + minutos
    soma_sumario_horas_especial_noturna += sumario_horas_mensais['EspecialNoturno'].iloc[i]

# Se desejar converter a soma total de volta para o formato HH:MM
#total_horas = soma_sumario_horas_mensais_diurna // 60
#total_minutos = soma_sumario_horas_mensais_diurna % 60

total_horas_operacao = soma_horas_operacao // 60
total_minutos_operacao = soma_horas_operacao % 60

total_horas_operacao_diurno = soma_sumario_horas_mensais_diurna // 60
total_minutos_operacao_diurno = soma_sumario_horas_mensais_diurna % 60

total_horas_operacao_noturno = soma_sumario_horas_mensais_noturna // 60
total_minutos_operacao_noturno = soma_sumario_horas_mensais_noturna % 60

total_horas_operacao_especial_diurna = soma_sumario_horas_especial_diurna // 60
total_minutos_operacao_especial_diurna = soma_sumario_horas_especial_diurna % 60

total_horas_operacao_especial_noturna = soma_sumario_horas_especial_noturna // 60
total_minutos_operacao_especial_noturna = soma_sumario_horas_especial_noturna % 60

##### ----------- ESCREVER OS DADOS EM ARQUIVO TXT
###
with open('rel_horas_operacao.txt', 'w') as arquivo:
    for linha in range(len(sumario_horas_mensais)):
        arquivo.write(
            sumario_horas_mensais['Activity'].iloc[linha].ljust(15,) + ' ' +
            sumario_horas_mensais['Checkin'].iloc[linha].ljust(20) + ' ' +
            sumario_horas_mensais['Start'].iloc[linha].ljust(10) + ' ' +
            sumario_horas_mensais['End'].iloc[linha].ljust(10) + ' ' +
            sumario_horas_mensais['Checkout'].iloc[linha].ljust(20) + '\n')
             
    # Escrever o total de horas de operação
    arquivo.write(
        f"\nTotal HORAS DE OPERACAO: {total_horas_operacao:02}:{total_minutos_operacao:02}\n"
        f"Total HORAS DE OPERACAO DIRUNAS : {total_horas_operacao_diurno:02}:{total_minutos_operacao_diurno:02}\n"
        f"Total HORAS DE OPERACAO NOTURNAS : {total_horas_operacao_noturno:02}:{total_minutos_operacao_noturno:02}\n"
        f"Total HORAS DE OPERACAO ESPECIAIS DIURNAS : {total_horas_operacao_especial_diurna:02}:{total_minutos_operacao_especial_diurna:02}\n"
        f"Total HORAS DE OPERACAO ESPECIAIS NOTURNAS : {total_horas_operacao_especial_noturna:02}:{total_minutos_operacao_especial_noturna:02}\n"
    )

print('-------------------------------------------------------------------')
print(f"Total HORAS DE OPERAÇÃO : {total_horas_operacao:02}:{total_minutos_operacao:02}")
print('-------------------------------------------------------------------')
print(f"Total HORAS DE OPERAÇÃO DIURNAS : {total_horas_operacao_diurno:02}:{total_minutos_operacao_diurno:02}")
print('-------------------------------------------------------------------')
print(f"Total HORAS DE OPERAÇÃO NOTURNAS : {total_horas_operacao_noturno:02}:{total_minutos_operacao_noturno:02}")
print('-------------------------------------------------------------------')
print(f"Total HORAS DE OPERAÇÃO ESPECIAIS DIURNAS : {total_horas_operacao_especial_diurna:02}:{total_minutos_operacao_especial_diurna:02}")
print('-------------------------------------------------------------------')
print(f"Total HORAS DE OPERAÇÃO ESPECIAIS NOTURNAS : {total_horas_operacao_especial_noturna:02}:{total_minutos_operacao_especial_noturna:02}")
print('-------------------------------------------------------------------')

print(' TAREFA FINALIZADA COM SUCESSO :')
