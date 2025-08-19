import pandas as pd
from datetime import timedelta, datetime
import tkinter as tk
from tkinter import filedialog, messagebox, Tk
from tqdm import tqdm
import os
import subprocess
import pdb
import re
import warnings
import logging

warnings.filterwarnings("ignore")

# produzir um popup informando o nome do arquivo a se selecionar
root = tk.Tk()
root.withdraw()

# Trazer a janela para o topo e focar
root.lift()
root.focus_force()

def selecionar_arquivo():
    # 1. Selecionar diretório e armazenar na variável
    diretorio = filedialog.askdirectory(title="Selecione o diretório")
    if not diretorio:
        print("Nenhum diretório selecionado.")
        exit()

    # 2. Selecionar arquivo no diretório escolhido
    #arquivo_path = filedialog.askopenfilename(initialdir=diretorio, title="Selecione o arquivo - CÁLCULOS EM TIMEDELTA")
    arquivo_path = filedialog.askopenfilename(initialdir=diretorio, title="Selecione o arquivo - _QUARTA_VERSAO")

    if not arquivo_path:
        print("Nenhum arquivo selecionado.")
        exit()

    # Extrair nome do arquivo
    nome_arquivo = os.path.basename(arquivo_path)

    #print(f"Diretório selecionado: {diretorio}")
    #print(f"Arquivo original: {nome_arquivo}")
    
    return diretorio, nome_arquivo

######################################

def gravar_arquivo(nome_arquivo, diretorio):
    # 3. Substituir tudo após ')' no nome do arquivo por "novo nome"
    novo_nome = nome_arquivo.split(")")[0] + ") - CALCULOS_EM_TIMEDELTA_COM_TEMPOS_CALCULADOS" #+ os.path.splitext(nome_arquivo)[1]

    # Exibir resultados
    #print(f"Diretório selecionado: {diretorio}")
    #print(f"Arquivo original: {nome_arquivo}")
    #print(f"Novo nome do arquivo: {novo_nome}")

    # 4. gravar o arquivo no mesmo diretório com o novo nome
    df_dados_escala.to_csv(novo_nome, index=False)

    print(" Gravação completada !!!")
        

#######################################

# Chamar a função selecionar_arquivo e armazenar os retornos
diretorio, nome_arquivo = selecionar_arquivo()

nome_arquivo = diretorio + '/' + nome_arquivo 
# Ler o arquivo  CSV, o arquivo é o 
df_dados_escala = pd.read_csv(nome_arquivo, sep=',', encoding='utf-8', parse_dates=['Checkin', 'Checkout'], dayfirst=True)

# Extrair o nome do aeronauta
file_path = nome_arquivo
match = re.search(r'-\s*(.*?)\s*\(', file_path)
extracted_text = match.group(1) if match else "Texto não encontrado"

# CRIAR BARRA DE PROGRESSO
tqdm.pandas()

# MOSTRAR A EVOLUÇÃO DO PROCESSO
print('                                         INICIANDO A TAREFA DE CÁLCULOS BÁSICOS DA ESCALA')
print('                                         AGUARDE ...')

##########################################  TRABALHAR OS FERIADOS ##########################################

# Verificar se a coluna 'Tempo Apresentacao' existe
if 'Tempo Apresentacao' in df_dados_escala.columns:
    # Converter a coluna 'Tempo Apresentacao' para timedelta
    df_dados_escala['Tempo Apresentacao'] = pd.to_timedelta(df_dados_escala['Tempo Apresentacao'])
    
    # Somar as horas da coluna 'Tempo Apresentacao' numa variável com quebra mensal
    
    total_horas = df_dados_escala['Tempo Apresentacao'].sum()
    #print(f"Total de horas de apresentação: {total_horas}")
else:
    print("A coluna 'Tempo Apresentacao' não foi encontrada no arquivo CSV.")

# Criar novas colunas para armazenar tempos de apresentação noturnas, especiais e especiais noturnas
df_dados_escala['Tempo Apresentacao Diurna'] = pd.to_timedelta(0)
df_dados_escala['Tempo Apresentacao Noturna'] = pd.to_timedelta(0)
df_dados_escala['Tempo Apresentacao Especial Diurna'] = pd.to_timedelta(0)
df_dados_escala['Tempo Apresentacao Especial Noturna'] = pd.to_timedelta(0)

# Criar novas colunas para armazenar tempos após o corte final dos motores
df_dados_escala['Tempo Apos Corte'] = pd.to_timedelta(0)
df_dados_escala['Tempo Apos Corte Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Apos Corte Noturno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Apos Corte Especial Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Apos Corte Especial Noturno'] = pd.to_timedelta(0)

# Criar novas colunas para armazenar tempos em solo entre estapas de voo
#df_dados_escala['Tempo Solo'] = pd.to_timedelta(0)
df_dados_escala['Tempo Solo Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Solo Noturno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Solo Especial Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Solo Especial Noturno'] = pd.to_timedelta(0)

# Criar novas colunas para armazenas os tempos de jornada de trabalho
#df_dados_escala['Tempo Jornada'] = pd.to_timedelta(0)
df_dados_escala['Tempo Jornada Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Jornada Noturno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Jornada Especial Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Jornada Especial Noturno'] = pd.to_timedelta(0)

# Criar novas colunas para armazenas tempos de repouso extra repouso regulamentar
#df_dados_escala['Tempo Repouso Extra'] = pd.to_timedelta(0)
df_dados_escala['Tempo Repouso Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Repouso Noturno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Repouso Especial Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Repouso Especial Noturno'] = pd.to_timedelta(0)

# Criar novas colunas para armazenas tempos de repouso extra repouso regulamentar
#df_dados_escala['Tempo Repouso Extra'] = pd.to_timedelta(0)
df_dados_escala['Tempo Repouso Extra Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Repouso Extra Noturno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Repouso Extra Especial Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Repouso Extra Especial Noturno'] = pd.to_timedelta(0)

# Criar novas colunas para armazenar tempos de reserva
#df_dados_escala['Tempo Reserva'] = pd.to_timedelta(0)
df_dados_escala['Tempo Reserva Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Reserva Noturno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Reserva Especial Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Reserva Especial Noturno'] = pd.to_timedelta(0)

# Criar novas colunas para armazenas tempos de plantão ou sobreaviso
df_dados_escala['Tempo Plantao'] = pd.to_timedelta(0)
df_dados_escala['Tempo Plantao Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Plantao Noturno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Plantao Especial Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Plantao Especial Noturno'] = pd.to_timedelta(0)

# Criar novas colunas para armazenar tempos de treinamento
df_dados_escala['Tempo Treinamento'] = pd.to_timedelta(0)
df_dados_escala['Tempo Treinamento Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Treinamento Noturno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Treinamento Especial Diurno'] = pd.to_timedelta(0)
df_dados_escala['Tempo Treinamento Especial Noturno'] = pd.to_timedelta(0)

# Converter as colunas de data para datetime
df_dados_escala['Checkin'] = pd.to_datetime(df_dados_escala['Checkin'])
df_dados_escala['Start'] = pd.to_datetime(df_dados_escala['Start'])
df_dados_escala['End'] = pd.to_datetime(df_dados_escala['End'])
df_dados_escala['Checkout'] = pd.to_datetime(df_dados_escala['Checkout'])

# Criar coluna após a coluna Id_Leg para armazenar o dia da semana sendo domingo = 6 e sábado = 5
df_dados_escala['Dia_Semana'] = df_dados_escala['Checkin'].dt.weekday

# abrir o arquivo feriados.json
feriados = pd.read_json(r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\feriados.json")

# Converter a coluna 'Data' para datetime
feriados['date'] = pd.to_datetime(feriados['date'])

# Criar coluna 'Feriado' no DataFrame se a coluna 'Checkin' .data estiver no arquivo feriados 
df_dados_escala['Feriado'] = df_dados_escala['Checkin'].dt.date.isin(feriados['date'].dt.date)

# Selecionar o arquivo siglas_sabre.xlsx no path atual
path_siglas_sabre = (r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\Siglas Sabre 1.xlsx")

try:
    siglas_sabre = pd.read_excel(path_siglas_sabre, engine='openpyxl')
except FileNotFoundError:
    print(f"Arquivo não encontrado: {path_siglas_sabre}")
    exit(1)
except ValueError as e:
    print(f"Erro ao ler o arquivo Excel: {e}")
    exit(1)

#print(siglas_sabre)

# Criar lista com as reservas possíveis através do arquivo siglas_sabre, tudo o que iniciar com r ou R na coluna SIGLA deve ser carregado na lista
# criar lista l_rerervas
l_reservas = siglas_sabre[siglas_sabre['SIGLA'].str.startswith('R', na=False)]['SIGLA'].tolist()

# Criar lista com plantões possívei
l_plantoes = siglas_sabre[siglas_sabre['SIGLA'].str.startswith('P', na=False)]['SIGLA'].tolist()

# Criar lista com treinamentos possíveis, com as siglas abaixo
l_treinamentos = ['ALA',
'ANC',
'APT',
'ATR',
'AV',
'AVI',
'AVS',
'AVT',
'CA2',
'CA3',
'CAA',
'CAE',
'CAP',
'CB2',
'CB3',
'CBA',
'CBE',
'CCL',
'CEA',
'CFI',
'CI2',
'CI3',
'CIA',
'CIE',
'COL',
'CP2',
'CP3',
'CPA',
'CPE',
'CRM',
'CPT',
'DGR',
'DH',
'DL',
'DOB',
'EGP',
'ENP',
'EPA',
'EPI',
'FIV',
'G3',
'GCI',
'GCI',
'GF',
'GS',
'ICM',
'JJ',
'OPT',
'PC1',
'PC2',
'PC3',
'PIP',
'PIV',
'PP1',
'PP2',
'PSM',
'REI',
'REQ',
'SFX',
'S02',
'S06',
'S10',
'S14',
'S18',
'S22',
'SIT',
'SLC',
'SCL',
'SLF',
'T20',
'T30',
'TAI',
'TEM',
'TFX',
'UA',
'UNI',
'V20',
'V30',
'VAE',
'VAT',
'VEB',
'VFT',
'XEA',
'XQ2',
'XQ3'
]

#################################### DEFINIÇÃO DAS DEFs ##################################################

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO
def calcular_horas_diurnas_noturnas(row): 
    # Definição dos períodos
    hora_diurna_inicio = 6  # 06:00
    hora_diurna_fim = 18    # 18:00

    # Extrair valores de 'Checkin' e 'Checkout' da linha
    inicio = row['Checkout']
    fim = inicio + timedelta(hours=12)

    # Tempo total decorrido
    tempo_total = fim - inicio

    # Inicializar acumuladores
    total_diurno = timedelta()
    total_noturno = timedelta()

    # Iterar sobre cada minuto no intervalo
    atual = inicio
    while atual < fim:
        proximo = atual + timedelta(minutes=1)  # Avança um minuto
        
        # Verifica se está no período diurno ou noturno
        if hora_diurna_inicio <= atual.hour < hora_diurna_fim:
            total_diurno += (proximo - atual)
        else:
            total_noturno += (proximo - atual)

        atual = proximo

    return total_diurno, total_noturno, tempo_total

# Converter timedelta para horas e minutos
def formatar_tempo_em_horas_minutos(td):
    total_segundos = int(td.total_seconds())
    horas, segundos_restantes = divmod(total_segundos, 3600)
    minutos = segundos_restantes // 60
    return f"{horas}h {minutos}min"

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO HORA DE APRESENTAÇÃO
def calcular_tempos_apresentacao_especial_diurno_e_noturno(x):
    # Inicializar os tempos como zero
    tempo_noturno = pd.to_timedelta(0)
    tempo_diurno = pd.to_timedelta(0)

    tempo_noturno_especial = pd.to_timedelta(0)
    tempo_diurno_especial = pd.to_timedelta(0)

    # Definir limites de horários
    seis_horas = x['Checkin'].replace(hour=6, minute=0, second=0)
    dezoito_horas = x['Checkin'].replace(hour=18, minute=0, second=0)
    vinte_uma_horas = x['Checkin'].replace(hour=21, minute=0, second=0)

    # Verificar se a coluna 'Feriado' é True
    if x['Feriado']:
        # Checkin e Start totalmente no período noturno
        if (x['Checkin'] >= dezoito_horas or x['Checkin'] < seis_horas) and (x['Start'] <= seis_horas or x['Start'] >= dezoito_horas):
            tempo_noturno_especial = x['Start'] - x['Checkin']

        # Período dividido entre noturno e diurno
        elif x['Checkin'] < seis_horas and x['Start'] > seis_horas:
            tempo_noturno_especial = seis_horas - x['Checkin']
            tempo_diurno_especial = x['Start'] - seis_horas
        
        # Período totalmente diurno
        elif x['Checkin'] >= seis_horas and x['Start'] <= dezoito_horas:
            tempo_diurno_especial = x['Start'] - x['Checkin']
        
    # Verificar se é domingo e o ID é aplicável
    if (x['Id_Leg'] == '-IF' or x['Id_Leg'] == '-I'):
        
        # Caso 1: Regra para domingos
        if x['Checkin'].weekday() == 6:
            # Checkin e Start totalmente no período noturno
            if (x['Checkin'] >= dezoito_horas or x['Checkin'] < seis_horas) and (x['Start'] <= seis_horas or x['Start'] >= dezoito_horas):
                tempo_noturno_especial = x['Start'] - x['Checkin']

            # Período dividido entre noturno e diurno
            elif x['Checkin'] < seis_horas and x['Start'] > seis_horas:
                tempo_noturno_especial = seis_horas - x['Checkin']
                tempo_diurno_especial = x['Start'] - seis_horas
            
            # Período totalmente diurno
            elif x['Checkin'] >= seis_horas and x['Start'] <= dezoito_horas:
                tempo_diurno_especial = x['Start'] - x['Checkin']

        # Caso 2: Regra para sábados após 21:00
        #AD5503	-I	04/01/2020 20:00	04/01/2020 20:53	REC	VCP
        #AD6994	-I	05/01/2020 18:00	05/01/2020 19:06	REC	BSB

        elif x['Checkin'].weekday() == 5 and x['Checkin'] >= vinte_uma_horas:
            tempo_noturno_especial = x['Start'] - x['Checkin']

    if (x['Checkin'] >= dezoito_horas or x['Checkin'] < seis_horas) and (x['Start'] <= seis_horas or x['Start'] >= dezoito_horas):
        tempo_noturno = x['Start'] - x['Checkin']

        # Período dividido entre noturno e diurno
    elif x['Checkin'] < seis_horas and x['Start'] > seis_horas:
        tempo_noturno = seis_horas - x['Checkin']
        tempo_diurno = x['Start'] - seis_horas
    
    # Período totalmente diurno
    elif x['Checkin'] >= seis_horas and x['Start'] <= dezoito_horas:
        tempo_diurno = x['Start'] - x['Checkin']
    
    #return pd.Series([tempo_noturno, tempo_diurno, tempo_noturno_especial, tempo_diurno_especial])
    return pd.Series({
            'Tempo Apresentacao Noturna': tempo_noturno,
            'Tempo Apresentacao Diurna': tempo_diurno,
            'Tempo Apresentacao Especial Noturna': tempo_noturno_especial,
            'Tempo Apresentacao Especial Diurna': tempo_diurno_especial,
        })

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO APÓS O CORTE FINAL DOS MOTORES
def calcular_tempos_corte_especial_diurno_e_noturno(x):
    
    #Calcula os tempos de apresentação especial diurno e noturno:
    #  - Noturno: 18:00 às 06:00 do dia seguinte.
    #  - Diurno: 06:00 às 18:00.
    #  - Noturno especial adicional: Sábados após 21:00.
    
    # Inicializar os tempos como zero
    tempo_corte = pd.NaT
    tempo_noturno = pd.to_timedelta(0)
    tempo_diurno = pd.to_timedelta(0)
    tempo_noturno_especial = pd.to_timedelta(0)
    tempo_diurno_especial = pd.to_timedelta(0)

    try:
        # Garantir que as colunas são do tipo datetime
        x['Checkout'] = pd.to_datetime(x['Checkout'], errors='coerce')
        x['End'] = pd.to_datetime(x['End'], errors='coerce')

        # Verificar se há valores inválidos
        if pd.isna(x['Checkout']) or pd.isna(x['End']):
            raise ValueError("Valores inválidos em 'Checkout' ou 'End'.")

        # Definir limites de horários
        seis_horas = x['End'].replace(hour=6, minute=0, second=0)
        dezoito_horas = x['End'].replace(hour=18, minute=0, second=0)
        vinte_uma_horas = x['End'].replace(hour=21, minute=0, second=0)

        # Calcular tempo de corte
        tempo_corte = x['Checkout'] - x['End']

        # Verificar períodos (Feriado)
        if x['Feriado']:
            if x['Checkout'] >= dezoito_horas or x['Checkout'] < seis_horas:  # Noturno especial
                tempo_noturno_especial = x['Checkout'] - x['End']
            elif x['End'] < seis_horas and x['Checkout'] > seis_horas:  # Dividido
                tempo_noturno_especial = seis_horas - x['End']
                tempo_diurno_especial = x['Checkout'] - seis_horas
            elif x['Checkout'] >= seis_horas and x['End'] <= dezoito_horas:  # Diurno especial
                tempo_diurno_especial = x['Checkout'] - x['End']

        # Verificar se é domingo e o ID é aplicável
        if x['Id_Leg'] in ['-IF', '-I']:
            # Caso 1: Domingos
            if x['Checkout'].weekday() == 6:
                if x['Checkout'] >= dezoito_horas or x['Checkout'] < seis_horas:
                    tempo_noturno_especial = x['Checkout'] - x['End']
                elif x['End'] < seis_horas and x['Checkout'] > seis_horas:
                    tempo_noturno_especial = seis_horas - x['End']
                    tempo_diurno_especial = x['Checkout'] - seis_horas
                elif x['End'] >= seis_horas and x['Checkout'] <= dezoito_horas:
                    tempo_diurno_especial = x['Checkout'] - x['End']

            # Caso 2: Sábados após 21:00
            if x['End'].weekday() == 5 and x['End'] >= vinte_uma_horas:
                tempo_noturno_especial = x['Checkout'] - x['End']

        # Períodos padrão (Noturno e Diurno)
        if x['End'] >= dezoito_horas or x['End'] < seis_horas:
            if x['Checkout'] >= dezoito_horas or x['Checkout'] < seis_horas:
                tempo_noturno = x['Checkout'] - x['End']
            elif x['Checkout'] >= seis_horas:
                tempo_noturno = seis_horas - x['End']
                tempo_diurno = x['Checkout'] - seis_horas
        elif x['End'] >= seis_horas and x['End'] < dezoito_horas:
            if x['Checkout'] <= dezoito_horas:
                tempo_diurno = x['Checkout'] - x['End']
            elif x['Checkout'] >= dezoito_horas:
                tempo_diurno = dezoito_horas - x['End']
                tempo_noturno = x['Checkout'] - dezoito_horas

    except Exception as e:
        print(f"Erro ao calcular os tempos: {e}")
    
    # Retornar os tempos calculados
    return pd.Series({
        'Tempo Apos Corte': tempo_corte,
        'Tempo Apos Corte Noturno': tempo_noturno,
        'Tempo Apos Corte Diurno': tempo_diurno,
        'Tempo Apos Corte Especial Noturno': tempo_noturno_especial,
        'Tempo Apos Corte Especial Diurno': tempo_diurno_especial,
    })

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO TEMPO EM SOLO
def calcular_tempos_solo_especial_diurno_e_noturno(row):
    # Inicializar os tempos como zero
    tempo_noturno = pd.to_timedelta(0)
    tempo_diurno = pd.to_timedelta(0)
    tempo_noturno_especial = pd.to_timedelta(0)
    tempo_diurno_especial = pd.to_timedelta(0)

    try:
        # Garantir que as colunas são do tipo datetime
        row['Start'] = pd.to_datetime(row['Start'], errors='coerce')
        row['End'] = pd.to_datetime(row['End'], errors='coerce')

        # Verificar se há valores inválidos
        if pd.isna(row['Start']) or pd.isna(row['End']):
            raise ValueError("Valores inválidos em 'Start' ou 'End'.")

        # Definir limites de horários
        seis_horas = row['End'].replace(hour=6, minute=0, second=0)
        dezoito_horas = row['End'].replace(hour=18, minute=0, second=0)
        vinte_uma_horas = row['End'].replace(hour=21, minute=0, second=0)

        if row['Id_Leg'] in ['-I', '-M']:

            # Verificar períodos (Feriado)
            if row['Feriado']:
                if row['End'] >= dezoito_horas or row['End'] < seis_horas:  # Noturno especial
                    tempo_noturno_especial = row['Tempo Solo']
                elif row['End'] < seis_horas and row['Start'] > seis_horas:  # Dividido
                    tempo_noturno_especial = seis_horas - row['End']
                    tempo_diurno_especial = row['Start'] - seis_horas
                elif row['End'] >= seis_horas and row['End'] <= dezoito_horas:  # Diurno especial
                    tempo_diurno_especial = row['Tempo Solo']

            # Verificar se é domingo e o ID é aplicável
            # Caso 1: Domingos
            if row['Checkout'].weekday() == 6:
                if row['Checkout'] >= dezoito_horas or row['Checkout'] < seis_horas:
                    tempo_noturno_especial = row['Checkout'] - row['End']
                elif row['End'] < seis_horas and row['Checkout'] > seis_horas:
                    tempo_noturno_especial = seis_horas - row['End']
                    tempo_diurno_especial = row['Checkout'] - seis_horas
                elif row['End'] >= seis_horas and row['Checkout'] <= dezoito_horas:
                    tempo_diurno_especial = row['Checkout'] - row['End']

            # Caso 2: Sábados após 21:00
            if row['End'].weekday() == 5 and row['End'] >= vinte_uma_horas:
                tempo_noturno_especial = row['Checkout'] - row['End']

            # Períodos padrão (Noturno e Diurno)
            # se as datas de Start e End forem iguais
            if row['Start'].date() == row['End'].date():
                if row['End'] >= dezoito_horas: 
                    tempo_noturno = row['Tempo Solo']
                elif row['End'] < seis_horas:
                    tempo_noturno = row['Tempo Solo']
                elif row['Start'] >= seis_horas and row['End'] < dezoito_horas:
                    tempo_diurno = row['Tempo Solo']
                elif row['End'] >= seis_horas and row['End'] <= dezoito_horas:
                    tempo_diurno = row['Tempo Solo']
            # se as datas de Start e End forem diferentes
            elif row['Start'].date() != row['End'].date():
                if row['Start'] >= dezoito_horas:
                    tempo_noturno = row['Tempo Solo']
                elif row['End'] < seis_horas:
                    tempo_noturno = row['Tempo Solo']
                elif row['Start'] >= seis_horas and row['End'] < dezoito_horas:
                    tempo_diurno = row['Tempo Solo']

    except Exception as e:
        print(f"Erro ao calcular os tempos SOLO :{row['Activity']} {e}")

    # Retornar os tempos calculados
    return pd.Series({
        'Tempo Solo Diurno': tempo_diurno,
        'Tempo Solo Noturno': tempo_noturno,
        'Tempo Solo Especial Diurno': tempo_diurno_especial,
        'Tempo Solo Especial Noturno': tempo_noturno_especial,
    })

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO TEMPO DE JORNADA DE TRABALHO
def calcular_tempos_jornada_especial_diurno_e_noturno(x):
    
    # Inicializar os tempos como zero
    tempo_noturno = pd.to_timedelta(0)
    tempo_diurno = pd.to_timedelta(0)
    tempo_noturno_especial = pd.to_timedelta(0)
    tempo_diurno_especial = pd.to_timedelta(0)

    try:
        # Garantir que as colunas são do tipo datetime
        x['Checkin'] = pd.to_datetime(x['Checkin'], errors='coerce')
        x['Checkout'] = pd.to_datetime(x['Checkout'], errors='coerce')

        # Verificar se há valores inválidos
        if pd.isna(x['Checkin']) or pd.isna(x['Checkout']):
            raise ValueError("Valores inválidos em 'Checkout' ou 'Checkin'.")

        # Definir limites de horários
        seis_horas_checkin = x['Checkin'].replace(hour=6, minute=0, second=0)
        dezoito_horas_checkin = x['Checkin'].replace(hour=18, minute=0, second=0)
        vinte_uma_horas_checkin = x['Checkin'].replace(hour=21, minute=0, second=0)

        seis_horas_checkout = x['Checkout'].replace(hour=6, minute=0, second=0)
        dezoito_horas_checkout = x['Checkout'].replace(hour=18, minute=0, second=0)
        vinte_uma_horas_checkout = x['Checkout'].replace(hour=21, minute=0, second=0)
        
        # Verificar períodos (Feriado)
        if x['Feriado']:
            if (x['Checkin'] >= dezoito_horas_checkin or x['Checkin'] < seis_horas_checkin) and (x['Checkout'] >= dezoito_horas_checkout or x['Checkout'] < seis_horas_checkout):  # Noturno especial
                tempo_noturno_especial = x['Jornada']
            elif x['Checkin'] < seis_horas_checkin and x['Checkout'] > seis_horas_checkout: 
                tempo_noturno_especial = seis_horas_checkin - x['Checkin']
                tempo_diurno_especial = x['Checkout'] - seis_horas_checkout
            elif x['Checkin'] > seis_horas_checkin and x['Checkout'] > dezoito_horas_checkout:
                tempo_noturno_especial = x['Checkout'] - dezoito_horas_checkout
                tempo_diurno_especial = dezoito_horas_checkout - x['Checkin']
            elif x['Checkin'] >= seis_horas_checkin and x['Checkout'] <= dezoito_horas_checkout:  # Diurno especial
                tempo_diurno_especial = x['Jornada']

        # Verificar se é domingo e o ID é aplicável
        if x['Id_Leg'] in ['-F', '-IF']:
            if x['Checkout'].weekday() == 6:
                if (x['Checkin'] >= dezoito_horas_checkin or x['Checkin'] < seis_horas_checkin) and (x['Checkout'] >= dezoito_horas_checkout or x['Checkout'] < seis_horas_checkout):  # Noturno especial
                    tempo_noturno_especial = x['Jornada']
                elif x['Checkin'] < seis_horas_checkin and x['Checkout'] > seis_horas_checkout: 
                    tempo_noturno_especial = seis_horas_checkin - x['Checkin']
                    tempo_diurno_especial = x['Checkout'] - seis_horas_checkout
                elif x['Checkin'] > seis_horas_checkin and x['Checkout'] > dezoito_horas_checkout:
                    tempo_noturno_especial = x['Checkout'] - dezoito_horas_checkout
                    tempo_diurno_especial = dezoito_horas_checkout - x['Checkin']
                elif x['Checkin'] >= seis_horas_checkin and x['Checkout'] <= dezoito_horas_checkout:  # Diurno especial
                    tempo_diurno_especial = x['Jornada']            
            # Caso 2: Sábados após 21:00
            if x['Checkin'].weekday() == 5 or x['Checkout'].weekday() == 5 and x['Checkout'] >= vinte_uma_horas_checkout:
                tempo_noturno_especial = x['Jornada']

        # Períodos padrão (Noturno e Diurno)
        if (x['Checkin'] >= dezoito_horas_checkin or x['Checkin'] < seis_horas_checkin) and (x['Checkout'] >= dezoito_horas_checkout or x['Checkout'] < seis_horas_checkout):
            tempo_noturno = x['Jornada']
        elif x['Checkin'] >= seis_horas_checkin and x['Checkout'] <= dezoito_horas_checkout:
            tempo_diurno = x['Jornada'] 
        elif x['Checkin'] < seis_horas_checkin and x['Checkout'] > seis_horas_checkout: 
            tempo_noturno = seis_horas_checkin - x['Checkin']
            tempo_diurno = x['Jornada'] - tempo_noturno
        elif x['Checkin'] > seis_horas_checkin and x['Checkout'] > dezoito_horas_checkout:
            tempo_noturno = x['Checkout'] - dezoito_horas_checkout
            tempo_diurno = x['Jornada'] - tempo_noturno
    except Exception as e:
        print(f"Erro ao calcular os tempos JORNADA :{x} {e}")
    
    #####
    # Enviar os valores para no caso de serem dois dias retornar os valores corretos por cada dia
    return pd.Series({
        'Tempo Jornada Diurno': tempo_diurno,
        'Tempo Jornada Noturno': tempo_noturno,
        'Tempo Jornada Especial Diurno': tempo_diurno_especial,
        'Tempo Jornada Especial Noturno': tempo_noturno_especial,
    })

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO TEMPO DE REPONSO
def calcular_horas_diurno_noturno_por_dia_repouso(row):
    # se repouso for menor que 12 horas retornar sem executar os calculos
    if pd.to_timedelta(row['Repouso']) < pd.to_timedelta('12:00:00'):
        return pd.Series({
            'Tempo Repouso Diurno': timedelta(),
            'Tempo Repouso Noturno': timedelta(),
            'Tempo Repouso Especial Diurno': timedelta(),
            'Tempo Repouso Especial Noturno': timedelta()
        })
    
    # Definição dos períodos
    hora_diurna_inicio = 6  # 06:00
    hora_diurna_fim = 18    # 18:00

    # Extrair valores de 'Checkin' e 'Checkout' da linha
    inicio = row['Checkout']
    fim = inicio + timedelta(hours=12) 

    # Tempo total decorrido
    tempo_total = fim - inicio

    # Inicializar variáveis de tempo
    total_diurno = timedelta()
    total_noturno = timedelta()
    total_diurno_especial = timedelta()
    total_noturno_especial = timedelta()

    # Iterar sobre cada minuto no intervalo
    atual = inicio
    while atual < fim:
        proximo = atual + timedelta(minutes=1)  # Avança um minuto
        
        # Verifica se está no período diurno ou noturno
        if hora_diurna_inicio <= atual.hour < hora_diurna_fim:
            total_diurno += (proximo - atual)
        else:
            total_noturno += (proximo - atual)

        atual = proximo

    # Calcular períodos especiais
    if row['Feriado']:
        total_diurno_especial = total_diurno
        total_noturno_especial = total_noturno

    if row['Dia_Semana'] == 5 and inicio.hour > 21:
        total_noturno_especial = total_noturno

    #if row['Checkout'].weekday() == 6:
    if row['Dia_Semana'] == 6:
        total_diurno_especial = total_diurno
        total_noturno_especial = total_noturno

    return pd.Series({
        'Tempo Repouso Diurno': total_diurno,
        'Tempo Repouso Noturno': total_noturno,
        'Tempo Repouso Especial Diurno': total_diurno_especial,
        'Tempo Repouso Especial Noturno': total_noturno_especial
    })

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO TEMPO DE REPONSO EXTRA
def calcular_horas_diurno_noturno_por_dia_repouso_extra(row):
    # se repouso for menor que 12 horas retornar sem executar os calculos
    if pd.to_timedelta(row['Repouso']) < pd.to_timedelta('12:00:00'):
        return pd.Series({
            'Tempo Repouso Extra Diurno': timedelta(),
            'Tempo Repouso Extra Noturno': timedelta(),
            'Tempo Repouso Extra Especial Diurno': timedelta(),
            'Tempo Repouso Extra Especial Noturno': timedelta()
        })
    
    # Definição dos períodos
    hora_diurna_inicio = 6  # 06:00
    hora_diurna_fim = 18    # 18:00

    # Extrair valores de 'Checkin' e 'Checkout' da linha
    inicio = row['Checkout'] + timedelta(hours=12, minutes=1) 
    fim = inicio + pd.to_timedelta(row['Repouso Extra']) 

    # Tempo total decorrido
    tempo_total = fim - inicio

    # Inicializar variáveis de tempo
    total_diurno = timedelta()
    total_noturno = timedelta()
    total_diurno_especial = timedelta()
    total_noturno_especial = timedelta()

    # Iterar sobre cada minuto no intervalo
    atual = inicio
    while atual < fim:
        proximo = atual + timedelta(minutes=1)  # Avança um minuto
        
        # Verifica se está no período diurno ou noturno
        if hora_diurna_inicio <= atual.hour < hora_diurna_fim:
            total_diurno += (proximo - atual)
        else:
            total_noturno += (proximo - atual)

        atual = proximo

    # Calcular períodos especiais
    if row['Feriado']:
        total_diurno_especial = total_diurno
        total_noturno_especial = total_noturno

    if row['Dia_Semana'] == 5 and inicio.hour > 21:
        total_noturno_especial = total_noturno

    #if row['Checkout'].weekday() == 6:
    if row['Dia_Semana'] == 6:
        total_diurno_especial = total_diurno
        total_noturno_especial = total_noturno

    return pd.Series({
        'Tempo Repouso Extra Diurno': total_diurno,
        'Tempo Repouso Extra Noturno': total_noturno,
        'Tempo Repouso Extra Especial Diurno': total_diurno_especial,
        'Tempo Repouso Extra Especial Noturno': total_noturno_especial,
    })    
        
        ################################################### FINAL DAS defs ###################################################

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO DAS RESERVAS
def calcular_horas_diurno_noturno_por_dia_reserva(row): 

    row['Tempo Reserva Diurno'] = pd.to_timedelta(0)
    row['Tempo Reserva Noturno'] = pd.to_timedelta(0)
    row['Tempo Reserva Especial Diurno'] = pd.to_timedelta(0)
    row['Tempo Reserva Especial Noturno'] = pd.to_timedelta(0)
    
    # se activity estiver na l_reservas, prosseguir, caso contrario sair
    if row['Activity'] in l_reservas:

        hora_diurna_inicio = 6  # 06:00
        hora_diurna_fim = 18    # 18:00

        # Extrair valores de 'Checkin' e 'Checkout' da linha
        inicio = row['Checkin']
        fim = row['Checkout'] 

        # Tempo total decorrido
        tempo_total = fim - inicio

        # Inicializar acumuladores
        total_diurno = timedelta()
        total_noturno = timedelta()
        total_diurno_especial = timedelta()
        total_noturno_especial = timedelta()
        
        # Iterar sobre cada minuto no intervalo
        atual = inicio
        while atual < fim:
            proximo = atual + timedelta(minutes=1)  # Avança um minuto
            
            # Verifica se está no período diurno ou noturno
            if hora_diurna_inicio <= atual.hour < hora_diurna_fim:
                total_diurno += (proximo - atual)
            else:
                total_noturno += (proximo - atual)

            atual = proximo

        # Calcular períodos especiais
        if row['Feriado']:
            total_diurno_especial = total_diurno
            total_noturno_especial = total_noturno

        if row['Dia_Semana'] == 5 and inicio.hour > 21:
            total_noturno_especial = total_noturno

        if row['Dia_Semana'] == 6:
            total_diurno_especial = total_diurno
            total_noturno_especial = total_noturno

        return pd.Series({
            'Tempo Reserva' : tempo_total,
            'Tempo Reserva Diurno': total_diurno,
            'Tempo Reserva Noturno': total_noturno,
            'Tempo Reserva Especial Diurno': total_diurno_especial,
            'Tempo Reserva Especial Noturno': total_noturno_especial,
        })    
    else:
        return pd.Series({
            'Tempo Reserva Diurno': timedelta(0),
            'Tempo Reserva Noturno': timedelta(0),
            'Tempo Reserva Especial Diurno': timedelta(0),
            'Tempo Reserva Especial Noturno': timedelta(0),
            })

# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO DOS PLANTÕES
def calcular_horas_diurno_noturno_por_dia_plantao(row):
     
    row['Tempo Plantao Diurno'] = pd.to_timedelta(0)
    row['Tempo Plantao Noturno'] = pd.to_timedelta(0)
    row['Tempo Plantao Especial Diurno'] = pd.to_timedelta(0)
    row['Tempo Plantao Especial Noturno'] = pd.to_timedelta(0)
    
    
    if row['Activity'] in l_plantoes:
   
        # Definição dos períodos
        hora_diurna_inicio = 6  # 06:00
        hora_diurna_fim = 18    # 18:00

        # Extrair valores de 'Checkin' e 'Checkout' da linha
        inicio = row['Checkin']
        fim = row['Checkout'] 

        # Tempo total decorrido
        tempo_total = fim - inicio

        # Inicializar acumuladores
        total_diurno = timedelta()
        total_noturno = timedelta()
        total_diurno_especial = timedelta()
        total_noturno_especial = timedelta()
        
        # Iterar sobre cada minuto no intervalo
        atual = inicio
        while atual < fim:
            proximo = atual + timedelta(minutes=1)  # Avança um minuto
            
            # Verifica se está no período diurno ou noturno
            if hora_diurna_inicio <= atual.hour < hora_diurna_fim:
                total_diurno += (proximo - atual)
            else:
                total_noturno += (proximo - atual)

            atual = proximo

        # Calcular períodos especiais
        if row['Feriado']:
            total_diurno_especial = total_diurno
            total_noturno_especial = total_noturno

        if row['Dia_Semana'] == 5 and inicio.hour > 21:
            total_noturno_especial = total_noturno

        if row['Dia_Semana'] == 6:
            total_diurno_especial = total_diurno
            total_noturno_especial = total_noturno

        return pd.Series({
            'Tempo Plantao' : tempo_total,
            'Tempo Plantao Diurno': total_diurno,
            'Tempo Plantao Noturno': total_noturno,
            'Tempo Plantao Especial Diurno': total_diurno_especial,
            'Tempo Plantao Especial Noturno': total_noturno_especial,
        })
    else:
        
        return pd.Series({
            'Tempo Plantao' : pd.to_timedelta(0),
            'Tempo Plantao Diurno' : pd.to_timedelta(0),
            'Tempo Plantao Noturno' : pd.to_timedelta(0),
            'Tempo Plantao Especial Diurno' : pd.to_timedelta(0),
            'Tempo Plantao Especial Noturno' : pd.to_timedelta(0),
        })
        
        
# FUNÇÃO PARA CALCULAR DIURNO E NOTURNO DOS TREINAMENTOS
def calcular_horas_diurno_noturno_por_dia_treinamento(row):
   
    row['Tempo Treinamento'] = pd.to_timedelta(0)
    row['Tempo Treinamento Diurno'] = pd.to_timedelta(0)
    row['Tempo Treinamento Noturno'] = pd.to_timedelta(0)
    row['Tempo Treinamento Especial Diurno'] = pd.to_timedelta(0)
    row['Tempo Treinamento Especial Noturno'] = pd.to_timedelta(0)
 
    if row['Activity'] in l_treinamentos:
   
        # Definição dos períodos
        hora_diurna_inicio = 6  # 06:00
        hora_diurna_fim = 18    # 18:00

        # Extrair valores de 'Checkin' e 'Checkout' da linha
        inicio = row['Checkin']
        fim = row['Checkout'] 

        # Tempo total decorrido
        tempo_total = fim - inicio

        # Inicializar acumuladores
        total_diurno = timedelta()
        total_noturno = timedelta()
        total_diurno_especial = timedelta()
        total_noturno_especial = timedelta()
        
        # Iterar sobre cada minuto no intervalo
        atual = inicio
        while atual < fim:
            proximo = atual + timedelta(minutes=1)  # Avança um minuto
            
            # Verifica se está no período diurno ou noturno
            if hora_diurna_inicio <= atual.hour < hora_diurna_fim:
                total_diurno += (proximo - atual)
            else:
                total_noturno += (proximo - atual)

            atual = proximo

        # Calcular períodos especiais
        if row['Feriado']:
            total_diurno_especial = total_diurno
            total_noturno_especial = total_noturno

        if row['Dia_Semana'] == 5 and inicio.hour > 21:
            total_noturno_especial = total_noturno

        if row['Dia_Semana'] == 6:
            total_diurno_especial = total_diurno
            total_noturno_especial = total_noturno

        return pd.Series({
            'Tempo Treinamento' : tempo_total,
            'Tempo Treinamento Diurno': total_diurno,
            'Tempo Treinamento Noturno': total_noturno,
            'Tempo Treinamento Especial Diurno': total_diurno_especial,
            'Tempo Treinamento Especial Noturno': total_noturno_especial,
        })
    else:
        return pd.Series({
            'Tempo Treinamento': pd.NA,
            'Tempo Treinamento Diurno': pd.NA,
            'Tempo Treinamento Noturno': pd.NA,
            'Tempo Treinamento Especial Diurno': pd.NA,
            'Tempo Treinamento Especial Noturno': pd.NA,
        })

######################################## FINAL DA DEFINIÇÃO DAS DEFs ##################################################

# Verificar se há valores com '-I' ou '-IF' na coluna 'Id_Leg' para os cálculos do Tempo de Apresentação
if df_dados_escala['Id_Leg'].str.contains(r'(-I|-IF)$', na=False).any():
    #print("A coluna 'Id_Leg' contém valores com '-I' ou '-IF'.")
    
    # Filtrar apenas as linhas que possuem '-I' ou '-IF'
    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-I|-IF)$', na=False)
    
    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Apresentacao Noturna', 
                                 'Tempo Apresentacao Diurna', 
                                 'Tempo Apresentacao Especial Noturna', 
                                 'Tempo Apresentacao Especial Diurna']] = \
        df_dados_escala.loc[filtro].apply(calcular_tempos_apresentacao_especial_diurno_e_noturno, axis=1)
#else:
#    print("A coluna 'Id_Leg' não contém valores com '-I' ou '-IF'.")

#####
# Verificar se há valores com '-I' ou '-IF' na coluna 'Id_Leg' para os cálculos do Tempo Corte dos Motores
if df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False).any():
    #print("A coluna 'Id_Leg' contém valores com '-IF' ou '-F'.")
    
    # Filtrar apenas as linhas que possuem '-I' ou '-IF'
    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False)

    print(df_dados_escala.loc[filtro]['Tempo Apos Corte'])
    
    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Apos Corte',
                                 'Tempo Apos Corte Noturno', 
                                 'Tempo Apos Corte Diurno', 
                                 'Tempo Apos Corte Especial Noturno', 
                                 'Tempo Apos Corte Especial Diurno']] = \
        df_dados_escala.loc[filtro].apply(calcular_tempos_corte_especial_diurno_e_noturno, axis=1)
#else:
#    print("A coluna 'Id_Leg' não contém valores com '-IF' ou '-F'.")

#####
# Verificar se há valores com '-I' ou '-IF' na coluna 'Id_Leg' para os cálculos do Tempo EM SOLO
if df_dados_escala['Id_Leg'].str.contains(r'(-I|-M)$', na=False).any():
    print("A coluna 'Id_Leg' contém valores com '-I' ou '-M'.")
    
    # Filtrar apenas as linhas que possuem '-I' ou '-IF'
    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-I|-M)$', na=False)

    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Solo Diurno', 
                                 'Tempo Solo Noturno', 
                                 'Tempo Solo Especial Diurno', 
                                 'Tempo Solo Especial Noturno']] = \
        df_dados_escala.loc[filtro].apply(calcular_tempos_solo_especial_diurno_e_noturno, axis=1)
#else:
#    print("A coluna 'Id_Leg' não contém valores com '-IF' ou '-F'.")

# Aplicar a função ao DataFrame
resultados = df_dados_escala.apply(calcular_tempos_solo_especial_diurno_e_noturno, axis=1)
# Converter as colunas de resultados para timedelta64[ns]
resultados = resultados.astype('timedelta64[ns]')
# Adicionar os resultados ao DataFrame original
df_dados_escala = pd.concat([df_dados_escala, resultados], axis=1)

#####
# Verificar se há valores com '-I' ou '-IF' na coluna 'Id_Leg' para os cálculos do Tempo das Jornadas 
if df_dados_escala['Id_Leg'].str.contains(r'(-F|-IF)$', na=False).any():
    #print("A coluna 'Id_Leg' contém valores com '-F' ou 'IF'.")
    
    # Filtrar apenas as linhas que possuem '-I' ou '-IF'
    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-F|-IF)$', na=False)

    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Jornada Diurno',
                                 'Tempo Jornada Noturno', 
                                 'Tempo Jornada Especial Diurno', 
                                 'Tempo Jornada Especial Noturno', 
                                 ]]= \
        df_dados_escala.loc[filtro].apply(calcular_tempos_jornada_especial_diurno_e_noturno, axis=1)
#else:
#    print("A coluna 'Id_Leg' não contém valores com '-IF' ou '-F'.")

# Aplicar a função ao DataFrame
resultados = df_dados_escala.apply(calcular_tempos_jornada_especial_diurno_e_noturno, axis=1)
# Converter as colunas de resultados para timedelta64[ns]
resultados = resultados.astype('timedelta64[ns]')
# Adicionar os resultados ao DataFrame original
df_dados_escala = pd.concat([df_dados_escala, resultados], axis=1)

#####
# Verificar se há valores com '-IF' ou '-F' na coluna 'Id_Leg' e o valor da coluna Reposuo seja maior que 12 horas para os cálculos do Tempo Corte dos Motores
if df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False).any():
    #print("A coluna 'Id_Leg' contém valores com '-IF' ou '-F'.")

    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False) #& (df_dados_escala['Repouso'] > pd.to_timedelta(12, unit='h'))

    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Repouso Diurno',
                                 'Tempo Repouso Noturno', 
                                 'Tempo Repouso Especial Diurno', 
                                 'Tempo Repouso Especial Noturno', 
                                 ]]= \
        df_dados_escala.loc[filtro].apply(calcular_horas_diurno_noturno_por_dia_repouso, axis=1)    

#else:   
#    print("A coluna 'Id_Leg' não contém valores com '-IF' ou '-F'.")

#####
# Verificar se há valores com '-IF' ou '-F' na coluna 'Id_Leg' e o valor da coluna Reposuo Extra seja maior que 12 horas para os cálculos 
if df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False).any():
    #print("A coluna 'Id_Leg' contém valores com '-IF' ou '-F'.")

    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False) #& (df_dados_escala['Repouso'] > pd.to_timedelta(12, unit='h'))

    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Repouso Extra Diurno',
                                 'Tempo Repouso Extra Noturno', 
                                 'Tempo Repouso Extra Especial Diurno', 
                                 'Tempo Repouso Extra Especial Noturno', 
                                 ]]= \
        df_dados_escala.loc[filtro].apply(calcular_horas_diurno_noturno_por_dia_repouso_extra, axis=1)    

#else:
#    print("A coluna 'Id_Leg' não contém valores com '-IF' ou '-F'.")

#####
# Verificar se há valores com '-IF' ou '-F' na coluna 'Id_Leg' e o valor da coluna Reserva 
if df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False).any():
    #print("A coluna 'Id_Leg' contém valores com '-IF' ou '-F'.")

    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False) #& (df_dados_escala['Repouso'] > pd.to_timedelta(12, unit='h'))

    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Reserva Diurno',
                                 'Tempo Reserva Noturno', 
                                 'Tempo Reserva Especial Diurno', 
                                 'Tempo Reserva Especial Noturno', 
                                 ]]= \
        df_dados_escala.loc[filtro].apply(calcular_horas_diurno_noturno_por_dia_reserva, axis=1)    

#else:
#    print("A coluna 'Id_Leg' não contém valores com '-IF' ou '-F'.")

#####
# Verificar se há valores com '-IF' ou '-F' na coluna 'Id_Leg' e o valor da coluna Plantao 
if df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False).any():
    #print("A coluna 'Id_Leg' contém valores com '-IF' ou '-F'.")

    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-IF|-F)$', na=False) 

    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Plantao',
                                 'Tempo Plantao Diurno',
                                 'Tempo Plantao Noturno', 
                                 'Tempo Plantao Especial Diurno', 
                                 'Tempo Plantao Especial Noturno', 
                                 ]]= \
        df_dados_escala.loc[filtro].apply(calcular_horas_diurno_noturno_por_dia_plantao, axis=1)    

#else:
#    print("A coluna 'Id_Leg' não contém valores com '-IF' ou '-F'.")

#####
# Verificar se há valores com '-IF' ou '-F' na coluna 'Id_Leg' e o valor da coluna Plantao 
if df_dados_escala['Id_Leg'].str.contains(r'(-IF|-M|-F)$', na=False).any():
    #print("A coluna 'Id_Leg' contém valores com '-IF', 'M'  ou '-F'.")

    filtro = df_dados_escala['Id_Leg'].str.contains(r'(-IF|-M|-F)$', na=False) 

    # Aplicar a função apenas às linhas filtradas
    df_dados_escala.loc[filtro, ['Tempo Treinamento',
                                 'Tempo Treinamento Diurno',
                                 'Tempo Treinamento Noturno', 
                                 'Tempo Treinamento Especial Diurno', 
                                 'Tempo Treinamento Especial Noturno', 
                                 ]]= \
        df_dados_escala.loc[filtro].apply(calcular_horas_diurno_noturno_por_dia_treinamento, axis=1)    

#else:
#    print("A coluna 'Id_Leg' não contém valores com '-IF' ou 'M' ou '-F'.")

######
# Passar os valores retornados para a função gravar_arquivo
gravar_arquivo(nome_arquivo, diretorio)    

# fechar o arquivo
        
"""
# Ler o arquivo CSV _com_tempos.csv
df_dados_escala_filtradas = pd.read_csv(path, sep=',', encoding='utf-8')

# Gravar dataframe df_dados_escala_filtrada como arquivo .CSV
df_dados_escala_filtradas.to_csv(path.replace('.csv', '_filtrado.csv'), sep=',', encoding='utf-8', index=False)
"""

# Ajuste o caminho do arquivo aqui
#caminho = ("C:/Users/Ricardo/OneDrive/Área de Trabalho/Fontes funcionando 26082024/Arquivos/Gabriel Lazzarini Portela/23638 - GABRIEL DAGLI LAZZARINI PORTELLA  ( 05-08-2019 - 01-04-2024 ) -_CALCULOS_EM_TIMEDELTA_com_tempos_filtrado.csv")
