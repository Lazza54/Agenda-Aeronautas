import os
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

path_to_data = "/"
tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023.csv", sep=",")

# FILTRAR OS DADOS PELA DATA SOLICITADA

var_mes1 = '2017-11' #input(' Digite o ano e mes do início da pesquisa; exemplo 2017-11 : ')
var_mes2 = '2017-12' #input(' Digite o ano e mes do meio da pesquisa; exemplo 2017-12 : ')
var_mes3 = '2018-01' #input(' Digite o ano e mes do final da pesquisa; exemplo 2018-12 : ')


### REFERENCIAS PARA OS FILTROS
# https://www.learndatasci.com/solutions/python-valueerror-truth-value-series-ambiguous-use-empty-bool-item-any-or-all/
# https://www.youtube.com/watch?v=nOxgV1AqbjU&t=62s&ab_channel=AmandaLemette
##### A PESQUISA COM MAIS DE UM MES ESTÁ PRODUZINDO EFEITO DESCONHECIDO ######
sumario_horassolo_trimestrais = tabela.loc[(tabela['Checkin'].str.contains(var_mes1)) | (tabela['Checkin'].str.contains(var_mes2)) | (tabela['Checkin'].str.contains(var_mes3))] #,['Operacao', ['Diurno'], ['Noturno'], ['Especial'], ['EspecialNoturno']]]

pd.set_option('display.max_rows', 200)

#print(sumario_horassolo_trimestrais)
#
# # SOMAR OS VALORES CONTIDOS EM OPERAÇÃO E TOTALIZAR
# # SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS
#
sumario_horassolo_trimestrais['TempoSolo'] = pd.to_timedelta(sumario_horassolo_trimestrais['TempoSolo'])
# sumario_horassolo_trimestrais['Diurno'] = pd.to_timedelta(sumario_horassolo_trimestrais['Diurno'])
# sumario_horassolo_trimestrais['Noturno'] = pd.to_timedelta(sumario_horassolo_trimestrais['Noturno'])
# sumario_horassolo_trimestrais['Especial'] = pd.to_timedelta(sumario_horassolo_trimestrais['Especial'])
# sumario_horassolo_trimestrais['EspecialNoturno'] = pd.to_timedelta(sumario_horassolo_trimestrais['EspecialNoturno'])
#
soma_sumario_horassolo_trimestrais_diurna = sumario_horassolo_trimestrais['TempoSolo'].sum()
# soma_sumario_horassolo_trimestrais_noturna = sumario_horassolo_trimestrais['Noturno'].sum()
# soma_sumario_horassolo_trimestrais_especial = sumario_horassolo_trimestrais['Especial'].sum()
# soma_sumario_horassolo_trimestrais_especial_noturna = sumario_horassolo_trimestrais['EspecialNoturno'].sum()
#
print(' TOTAL HORAS DIURNO:               ', soma_sumario_horassolo_trimestrais_diurna)
# print(' TOTAL HORAS NOTURNO:              ', soma_sumario_horassolo_trimestrais_noturna)
# print(' TOTAL HORAS ESPECIAL:             ', soma_sumario_horassolo_trimestrais_especial)
# print(' TOTAL HORAS ESPECIAL NOTURNA:     ', soma_sumario_horassolo_trimestrais_especial_noturna)
#
sumario_horassolo_trimestrais.to_csv(path_or_buf=os.path.join(path_to_data,
                                                              "calculos_trimestrais_horassolo_e_ricardo_lazzarini.csv"), index=False)