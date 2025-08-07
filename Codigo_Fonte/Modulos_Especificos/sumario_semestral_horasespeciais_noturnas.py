import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
path_to_data = "/"
tabela = pd.read_csv("../escala_e_ricardo_lazzarini_vcp_3394_112017_022023.csv", sep=",")

# FILTRAR OS DADOS PELA DATA SOLICITADA

var_mes1 = '2017-11' #input(' Digite o ano e mes do início da pesquisa; exemplo 2017-11 : ')
var_mes2 = '2017-12' #input(' Digite o ano e mes do meio da pesquisa; exemplo 2017-12 : ')
var_mes3 = '2018-01' #input(' Digite o ano e mes do meio da pesquisa; exemplo 2018-01 : ')
var_mes4 = '2018-02' #input(' Digite o ano e mes do meio da pesquisa; exemplo 2018-02 : ')
var_mes5 = '2018-03' #input(' Digite o ano e mes do meio da pesquisa; exemplo 2018-03 : ')
var_mes6 = '2018-04' #input(' Digite o ano e mes do final da pesquisa; exemplo 2018-04 : ')

### REFERENCIAS PARA OS FILTROS
# https://www.learndatasci.com/solutions/python-valueerror-truth-value-series-ambiguous-use-empty-bool-item-any-or-all/
# https://www.youtube.com/watch?v=nOxgV1AqbjU&t=62s&ab_channel=AmandaLemette
##### A PESQUISA COM MAIS DE UM MES ESTÁ PRODUZINDO EFEITO DESCONHECIDO ######
sumario_horasespeciaisnoturnas_semestrais = tabela.loc[(tabela['Checkin'].str.contains(var_mes1)) | (tabela['Checkin'].str.contains(var_mes2)) | (tabela['Checkin'].str.contains(var_mes3))\
    | (tabela['Checkin'].str.contains(var_mes4)) | (tabela['Checkin'].str.contains(var_mes5)) | (tabela['Checkin'].str.contains(var_mes6))]

pd.set_option('display.max_rows', 600)
#
#print(sumario_horasespeciaisnoturnas_semestrais ['EspecialNoturno'])
#
# # SOMAR OS VALORES CONTIDOS EM OPERAÇÃO E TOTALIZAR
# # SOMAR OS TEMPOS DE RESERVA DIURNAS, NOTURNAS E ESPECIAIS
#
sumario_horasespeciaisnoturnas_semestrais['EspecialNoturno'] = pd.to_timedelta(sumario_horasespeciaisnoturnas_semestrais['EspecialNoturno'])
# sumario_horasespeciaisnoturnas_semestrais['Diurno'] = pd.to_timedelta(sumario_horasespeciaisnoturnas_semestrais['Diurno'])
# sumario_horasespeciaisnoturnas_semestrais['Noturno'] = pd.to_timedelta(sumario_horasespeciaisnoturnas_semestrais['Noturno'])
# sumario_horasespeciaisnoturnas_semestrais['Especial'] = pd.to_timedelta(sumario_horasespeciaisnoturnas_semestrais['Especial'])
# sumario_horasespeciaisnoturnas_semestrais['Especial Noturno'] = pd.to_timedelta(sumario_horasespeciaisnoturnas_semestrais['EspecialNoturno'])
#
soma_sumario_horasespeciaisnoturnas_semestrais = sumario_horasespeciaisnoturnas_semestrais['EspecialNoturno'].sum()
# soma_sumario_horasespeciaisnoturnas_semestrais = sumario_horasespeciaisnoturnas_semestrais['Noturno'].sum()
# soma_sumario_horasespeciaisnoturnas_semestrais = sumario_horasespeciaisnoturnas_semestrais['Especial'].sum()
# soma_sumario_horasespeciaisnoturnas_semestrais = sumario_horasespeciaisnoturnas_semestrais['EspecialNoturno'].sum()
#
print(' TOTAL HORAS ESPECIAIS NOTURNAS:                ', soma_sumario_horasespeciaisnoturnas_semestrais)
# print(' TOTAL HORAS ESPECIAIS NOTURNO:              ', soma_sumario_horasespeciais_semestrais_noturna)
# print(' TOTAL HORAS ESPECIAL:             ', soma_sumario_horasespeciais_semestrais_especial)
# print(' TOTAL HORAS ESPECIAL NOTURNA:     ', soma_sumario_horasespeciais_semestrais_especial_noturna)
#
sumario_horasespeciaisnoturnas_semestrais.to_csv(path_or_buf=os.path.join(path_to_data,
                                                                          "calculos_semestrais_horasespeciaisnoturnas_e_ricardo_lazzarini.csv"), index=False)