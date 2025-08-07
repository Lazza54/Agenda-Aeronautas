import datetime
import pandas as pd
import re
import warnings
warnings.filterwarnings("ignore")
path_to_data = "/"
tabela = pd.read_csv("dados_limpos_escala_ricardo_lazzarini.csv", sep=",")

pd.set_option('display.max_rows', 100)

# FILTRAR OS DADOS PELA DATA SOLICITADA

var_datainicial = '2017-11' #input(' Digite a data da semana que deseja analisar, ')

# CONVERTER A COLUNA 'Checkin' EM DATETIME
sum_jorn_semanal = tabela.loc[(tabela['Checkin'].str.contains(var_datainicial))].copy()
#
sum_jorn_semanal = sum_jorn_semanal.assign(DiaSemana=0).copy()
sum_jorn_semanal['Checkin'] = pd.to_datetime(sum_jorn_semanal['Checkin'])
sum_jorn_semanal['Jornada'] = pd.to_timedelta(sum_jorn_semanal['Jornada'])

# IDENTIFICAR OS DOMINGOS E SÁBADOS DO MES SELECIONADO
for i in range(len(sum_jorn_semanal)):
    diasemana = sum_jorn_semanal['Checkin'].iloc[i].weekday()
    sum_jorn_semanal['DiaSemana'].iloc[i] = diasemana

# VERIFICAR SE NOS DOMINGOS (INICIO DA SEMANA) SELECIONADOS A JORNADA INICIOU-SE DENTRO DO DIA EM QUESTÃO
    # caso positivo, nenhuma ação adicional requerida, caso contrário determinar o ínício da jornada a ZERO HORA
    # DO DOMINGO EM QUESTÃO
### GERAR DF APENAS COM AS COLUNAS NECESSÁRIOA
filtered_inicial = sum_jorn_semanal[['Activity','Checkin','Jornada']]
### GERAR DF APENAS COM O INTERVALO DE DATAS NECESSÁRIAS
filtered_intermediaria = filtered_inicial.loc[(filtered_inicial['Checkin'] >= '2017-11-05')\
            & (filtered_inicial['Checkin'] <= '2017-11-12')].copy()
### GERAR DF APENAS COM AS ATIVIDADES DE FINAL DE CHAVE
filtered_final = filtered_intermediaria.loc[filtered_intermediaria['Activity'].str.contains("-F")]

soma_jornada = filtered_final['Jornada'].sum()

print(filtered_inicial)
print('-------------------------------------------------------------------------------------------------------------------')
print(filtered_intermediaria)
print('-------------------------------------------------------------------------------------------------------------------')
print(filtered_final)
print('-------------------------------------------------------------------------------------------------------------------')
print(' Horas de jornada na semana =   ', soma_jornada)
print('--------------------------------------------------------------------------------------------')
print(' O limite de jornada de trabalho semanal é de 44 horas, podendo ir até 60 hors, desde que,')
print(' haja pagamento de horas extras ou compensação do pagamento. E o limite de 176 horas do mes, não seja ultrapassado.' )
print('-------------------------------------------------------------------------------------------------------------------')

#
# # VERIFICAR SE NOS SÁBADOS (FINAL DA SEMANA) SELECIONADOS A JORNADA TERMINA DENTRO DO DIA EM QUESTÃO
#     # caso positivo, nenhuma ação adicional requerida, caso contrário determinar o final da jornada a ZERO HORA
#     # DO SÁBADO EM QUESTÃO
#
#
# #sumario_horasespeciais_anuais.to_csv(path_or_buf=os.path.join(path_to_data, "calculos_anual_horasespeciais_e_ricardo_lazzarini.csv"), index=False)