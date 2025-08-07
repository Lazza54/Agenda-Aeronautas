import pandas as pd
import os
path_to_data = "/"
tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023.csv", sep=",")

# FILTRAR OS DADOS PELA DATA SOLICITADA

var_datainicial = input(' Digite o ano para pesquisa; exemplo 2017: ')

sumario_horassolo_anuais = tabela[tabela['Checkin'].str.contains(var_datainicial)].copy()

pd.set_option('display.max_rows', 600)
#print(sumario_horassolo_anuais ['TempoSolo'])

# SOMAR OS VALORES CONTIDOS EM OPERAÇÃO E TOTALIZAR
# SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS

sumario_horassolo_anuais['TempoSolo'] = pd.to_timedelta(sumario_horassolo_anuais['TempoSolo'])
# sumario_horassolo_anuais['Diurno'] = pd.to_timedelta(sumario_horassolo_anuais['Diurno'])
# sumario_horassolo_anuais['Noturno'] = pd.to_timedelta(sumario_horassolo_anuais['Noturno'])
# sumario_horassolo_anuais['Especial'] = pd.to_timedelta(sumario_horassolo_anuais['Especial'])
# sumario_horassolo_anuais['EspecialNoturno'] = pd.to_timedelta(sumario_horassolo_anuais['EspecialNoturno'])

soma_sumario_horassolo_anuais_diurna = sumario_horassolo_anuais['TempoSolo'].sum()
# soma_sumario_horassolo_anuais_noturna = sumario_horassolo_anuais['Noturno'].sum()
# soma_sumario_horassolo_anuais_especial = sumario_horassolo_anuais['Especial'].sum()
# soma_sumario_horassolo_anuais_especial_noturna = sumario_horassolo_anuais['EspecialNoturno'].sum()

print(' TOTAL HORAS EM SOLO DIURNO:               ', soma_sumario_horassolo_anuais_diurna)
# print(' TOTAL HORAS VOADAS NOTURNO:              ', soma_sumario_horassolo_anuais_noturna)
# print(' TOTAL HORAS VOADAS ESPECIAL:             ', soma_sumario_horassolo_anuais_especial)
# print(' TOTAL HORAS VOADAS ESPECIAL NOTURNA:     ', soma_sumario_horassolo_anuais_especial_noturna)

sumario_horassolo_anuais.to_csv(path_or_buf=os.path.join(path_to_data,
                                                         "calculos_anual_horassolo_e_ricardo_lazzarini.csv"), index=False)