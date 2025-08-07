import pandas as pd
import os
path_to_data = "/"
tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023.csv", sep=",")

# FILTRAR OS DADOS PELA DATA SOLICITADA

var_datainicial = input(' Digite o ano e mes para pesquisa; exemplo 2017-11: ')

sumario_horas_mensais = tabela[tabela['Checkin'].str.contains(var_datainicial)].copy()

print(sumario_horas_mensais['Operacao'])
# SOMAR OS VALORES CONTIDOS EM OPERAÇÃO E TOTALIZAR
# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS

sumario_horas_mensais['Operacao'] = pd.to_timedelta(sumario_horas_mensais['Operacao'])
sumario_horas_mensais['Diurno'] = pd.to_timedelta(sumario_horas_mensais['Diurno'])
sumario_horas_mensais['Noturno'] = pd.to_timedelta(sumario_horas_mensais['Noturno'])
sumario_horas_mensais['Especial'] = pd.to_timedelta(sumario_horas_mensais['Especial'])
sumario_horas_mensais['EspecialNoturno'] = pd.to_timedelta(sumario_horas_mensais['EspecialNoturno'])

soma_sumario_horas_mensais_diurna = sumario_horas_mensais['Operacao'].sum()
soma_sumario_horas_mensais_noturna = sumario_horas_mensais['Noturno'].sum()
soma_sumario_horas_mensais_especial = sumario_horas_mensais['Especial'].sum()
soma_sumario_horas_mensais_especial_noturna = sumario_horas_mensais['EspecialNoturno'].sum()

print(' TOTAL HORAS VOADAS DIURNO:               ', soma_sumario_horas_mensais_diurna)
print(' TOTAL HORAS VOADAS NOTURNO:              ', soma_sumario_horas_mensais_noturna)
print(' TOTAL HORAS VOADAS ESPECIAL:             ', soma_sumario_horas_mensais_especial)
print(' TOTAL HORAS VOADAS ESPECIAL NOTURNA:     ', soma_sumario_horas_mensais_especial_noturna)

sumario_horas_mensais.to_csv(path_or_buf=os.path.join(path_to_data, "calculos_horas_voadas_e_ricardo_lazzarini.csv"), index=False)