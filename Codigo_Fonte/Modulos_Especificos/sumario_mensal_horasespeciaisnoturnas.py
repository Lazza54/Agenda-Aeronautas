import pandas as pd

path_to_data = "/"
tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023.csv", sep=",")

# FILTRAR OS DADOS PELA DATA SOLICITADA

var_datainicial = input(' Digite o ano e mes para pesquisa; exemplo 2017-11 : ')

sumario_horasespeciaisnoturnas_mensais = tabela[tabela['Checkin'].str.contains(var_datainicial)].copy()

# SOMAR OS VALORES CONTIDOS EM OPERAÇÃO E TOTALIZAR
# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS

sumario_horasespeciaisnoturnas_mensais['EspecialNoturno'] = pd.to_timedelta(sumario_horasespeciaisnoturnas_mensais['EspecialNoturno'])

soma_sumario_horasespeciaisnoturnas_mensais_diurna = sumario_horasespeciaisnoturnas_mensais['EspecialNoturno'].sum()

print(' HORAS MENSAIS ESPECIAIS NOTURNAS :               ', soma_sumario_horasespeciaisnoturnas_mensais_diurna)
