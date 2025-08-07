import pandas as pd
import os
path_to_data = "/"
tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023.csv", sep=",")

# FILTRAR OS DADOS PELA DATA SOLICITADA

var_datainicial = input(' Digite o ano para pesquisa; exemplo 2017: ')

sumario_horasespeciais_anuais = tabela[tabela['Checkin'].str.contains(var_datainicial)].copy()

pd.set_option('display.max_rows', 600)
#print(sumario_horasespeciais_anuais['Especial'])

# SOMAR OS VALORES CONTIDOS EM OPERAÇÃO E TOTALIZAR
# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS

sumario_horasespeciais_anuais['Especial'] = pd.to_timedelta(sumario_horasespeciais_anuais['Especial'])
# sumario_horasespeciais_anuais['Diurno'] = pd.to_timedelta(sumario_horasespeciais_anuais['Diurno'])
# sumario_horasespeciais_anuais['Noturno'] = pd.to_timedelta(sumario_horasespeciais_anuais['Noturno'])
# sumario_horasespeciais_anuais['Especial'] = pd.to_timedelta(sumario_horasespeciais_anuais['Especial'])
# sumario_horasespeciais_anuais['EspecialNoturno'] = pd.to_timedelta(sumario_horasespeciais_anuais['EspecialNoturno'])

soma_sumario_horasespeciais_anuais_diurna = sumario_horasespeciais_anuais['Especial'].sum()
# soma_sumario_horasespeciais_anuais_noturna = sumario_horasespeciais_anuais['Noturno'].sum()
# soma_sumario_horasespeciais_anuais_especial = sumario_horasespeciais_anuais['Especial'].sum()
# soma_sumario_horasespeciais_anuais_especial_noturna = sumario_horasespeciais_anuais['EspecialNoturno'].sum()

print(' TOTAL HORAS EM SOLO DIURNO:               ', soma_sumario_horasespeciais_anuais_diurna)
# print(' TOTAL HORAS VOADAS NOTURNO:              ', soma_sumario_horasespeciais_anuais_noturna)
# print(' TOTAL HORAS VOADAS ESPECIAL:             ', soma_sumario_horasespeciais_anuais_especial)
# print(' TOTAL HORAS VOADAS ESPECIAL NOTURNA:     ', soma_sumario_horasespeciais_anuais_especial_noturna)

sumario_horasespeciais_anuais.to_csv(path_or_buf=os.path.join(path_to_data,
                                                              "calculos_anual_horasespeciais_e_ricardo_lazzarini.csv"), index=False)