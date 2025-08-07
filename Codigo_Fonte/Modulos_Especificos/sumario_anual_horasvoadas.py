import pandas as pd
import os
from tkinter import filedialog

##### CONVERTER VALORES DE HORA
def converterhoras(valor):

    valor_dia = str(valor)[0:3] # entra com o primeiro valor do timedelta exemplo 1 days 05:00
    valor_horas = str(valor)[8:11] # entra com o valor de horas que está em valor
    valor_minutos = str(valor)[12:14] # estava [11:13]
    compara_dia = int(valor_dia) # transforma o valor em inteiro

    if valor_dia == 0 and valor_horas == 0 and valor_minutos == 0:
        print(' TUDO ZERADO')
        retorno_horas = valor
        return retorno_horas

    if compara_dia > 4: # se for menor que 4 serão 2 digitos na composição da hora que retornará formatada
        valor_dia_para_horas = compara_dia * 24 # isto retorna por exemplo 3 dias para 72 horas
        valor_total_em_horas = int(valor_dia_para_horas)+int(valor_horas)
        valor_total_em_horas_e_minutos = str(valor_total_em_horas)+':'+str(valor_minutos)
        retorno_horas = valor_total_em_horas_e_minutos
        return retorno_horas

    if compara_dia < 4 and compara_dia > 0:                                 # se for maior que 4 serão 3 digitos na composição da hora que retornará formatada
        valor_dia = str(valor)[0:1] # entra com o primeiro valor do timedelta exemplo 1 days 05:00
        valor_horas = str(valor)[7:9] # entra com o valor de horas que está em valor
        valor_dia_para_horas = compara_dia * 24 # isto retorna por exemplo 3 dias para 72 horas
        valor_total_em_horas = int(valor_dia_para_horas)+int(valor_horas)
        valor_total_em_horas_e_minutos = str(valor_total_em_horas)+':'+str(valor_minutos)
        retorno_horas = valor_total_em_horas_e_minutos
        return retorno_horas
    else:
        valor_dia = str(valor)[0:1] # entra com o primeiro valor do timedelta exempl 1 days 05:00
        valor_horas = str(valor)[7:9] # entra com o valor de horas que está em valor
        valor_dia_para_horas = compara_dia * 24 # isto retorna por exemplo 3 dias para 72 horas
        valor_total_em_horas = int(valor_dia_para_horas)+int(valor_horas)
        valor_total_em_horas_e_minutos = str(valor_total_em_horas)+':'+str(valor_minutos)
        retorno_horas = valor_total_em_horas_e_minutos
        return retorno_horas

##### OBTER OS NOMES DOS ARQUIVOS A SEREM PROCESSADOS
entrada = str(filedialog.askopenfilenames())
print(f' Primeira entrada : {entrada}')
print(f' Entrada corrigida : {entrada[2:-3]}')
entrada = entrada[2:-3]
saida = entrada[1:-7]
saida = 'E' + saida +"_FASE_C.csv'"
print(f' Saida desejada : {saida}')

path_to_data = "/"
tabela = pd.read_csv(entrada, sep=",")

# FILTRAR OS DADOS PELA DATA SOLICITADA
# var_datainicial = input(' Digite o ano para pesquisa; exemplo 2017: ')
# sumario_horas_anuais = tabela[tabela['Checkin'].str.contains(var_datainicial)].copy()
sumario_horas_anuais = tabela

# SOMAR OS VALORES CONTIDOS EM OPERAÇÃO E TOTALIZAR
# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS

sumario_horas_anuais['Operacao'] = pd.to_timedelta(sumario_horas_anuais['Operacao'])
sumario_horas_anuais['Diurno'] = pd.to_timedelta(sumario_horas_anuais['Diurno'])
sumario_horas_anuais['Noturno'] = pd.to_timedelta(sumario_horas_anuais['Noturno'])
sumario_horas_anuais['Especial'] = pd.to_timedelta(sumario_horas_anuais['Especial'])
sumario_horas_anuais['EspecialNoturno'] = pd.to_timedelta(sumario_horas_anuais['EspecialNoturno'])

soma_sumario_horas_anuais_diurna = sumario_horas_anuais['Operacao'].sum()
soma_sumario_horas_anuais_noturna = sumario_horas_anuais['Noturno'].sum()
soma_sumario_horas_anuais_especial = sumario_horas_anuais['Especial'].sum()
soma_sumario_horas_anuais_especial_noturna = sumario_horas_anuais['EspecialNoturno'].sum()

##### LEVAR VALOR PARA CONVERSÃO DE HORAS

retorno_horas=' '
valor = soma_sumario_horas_anuais_diurna
retorno_horas = converterhoras(valor)
print(f"TOTAL HORAS VOADAS DIURNO:              {soma_sumario_horas_anuais_diurna} - {retorno_horas} hs")

retorno_horas=' '
valor = soma_sumario_horas_anuais_noturna
retorno_horas = converterhoras(valor)
print(f"TOTAL HORAS VOADAS NOTURNO:             {soma_sumario_horas_anuais_noturna} - {retorno_horas} hs")

retorno_horas=' '
valor = soma_sumario_horas_anuais_especial
retorno_horas = converterhoras(valor)
print(f"TOTAL HORAS VOADAS ESPECIAL:            {soma_sumario_horas_anuais_especial} - {retorno_horas} hs")

retorno_horas=' '
valor = soma_sumario_horas_anuais_especial_noturna
retorno_horas = converterhoras(valor)
print(f"TOTAL HORAS VOADAS ESPECIAL NOTURNA:    {soma_sumario_horas_anuais_especial_noturna} - {retorno_horas} hs")

#sumario_horas_anuais.to_csv(path_or_buf=os.path.join(path_to_data, "calculos_horas_voadas_e_ricardo_lazzarini.csv"), index=False)