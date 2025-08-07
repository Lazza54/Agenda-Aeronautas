# =============================================================================
# CÁLCULO DE VALORES BÁSICOS - PROCESSAMENTO DE ESCALAS AERONÁUTICAS
# =============================================================================
# 
# Objetivo: Realizar os cálculos básicos da escala
# Entrada: Arquivo CSV '-UTC_COM_SUFIXO.csv' 
# Saída: Arquivo CSV '-CALCULOS_EM_TIMEDELTA.csv'
# 
# Autor: Ricardo Lazzarini
# Data de criação: 2024
# Última verificação: junho 2025
# =============================================================================

# importando as bibliotecas necessárias

from datetime import timedelta, time, datetime
from tkinter import filedialog, messagebox
from tqdm import tqdm
import pandas as pd
import os
import warnings
import requests
import pprint
import json
import tkinter as tk

def converter_data_flexivel(data_str):
    """
    Converte datas em múltiplos formatos para datetime
    Suporta formatos como: "01DEZ17 02:00", "2017-12-01 02:00", etc.
    """
    if pd.isna(data_str) or data_str == '' or data_str == '-':
        return pd.NaT
    
    # Dicionário de meses em português para inglês
    meses_pt = {
        'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
        'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
        'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
    }
    
    try:
        # Primeiro, tentar o formato padrão
        return pd.to_datetime(data_str)
    except Exception:
        try:
            # Converter formato "01DEZ17 02:00" para "2017-12-01 02:00"
            if any(mes in str(data_str) for mes in meses_pt.keys()):
                data_str = str(data_str).upper()
                for mes_pt, mes_num in meses_pt.items():
                    if mes_pt in data_str:
                        # Extrair partes da data
                        partes = data_str.split()
                        data_parte = partes[0]
                        hora_parte = partes[1] if len(partes) > 1 else "00:00"
                        
                        # Extrair dia, mês e ano
                        dia = data_parte[:2]
                        mes = mes_num
                        ano = "20" + data_parte[-2:]  # Assumir 20XX para anos de 2 dígitos
                        
                        # Reformatar
                        data_formatada = f"{ano}-{mes}-{dia} {hora_parte}"
                        return pd.to_datetime(data_formatada)
            
            # Tentar outros formatos comuns
            formatos = [
                '%d/%m/%Y %H:%M',
                '%d-%m-%Y %H:%M',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y-%m-%d'
            ]
            
            for formato in formatos:
                try:
                    return pd.to_datetime(data_str, format=formato)
                except Exception:
                    continue
                    
        except Exception:
            pass
    
    # Se nenhum formato funcionou, retornar NaT
    print(f"⚠️ Não foi possível converter a data: {data_str}")
    return pd.NaT

warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# FUNÇÃO PARA DETERMINAR DIRETORIO DE ARQUIVO E NOME DO ARQUIVO A SER UTILIZADO

def selecionar_diretorio():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    
    messagebox.showinfo("Seleção de Diretório", "Selecione o diretório onde estão os arquivos necessários.")

    path = filedialog.askdirectory()
    return path

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal

    messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo ricardo_lazzarini_vcp_3394_112017_022023__TERCEIRA_VERSAO.csv")
    root.update()

    path = filedialog.askopenfilename()
    return path

diretorio_path = selecionar_diretorio()
print(f"📂 Diretório selecionado com sucesso! {diretorio_path}")

arquivo_path = selecionar_arquivo()
print(f"📄 Arquivo selecionado com sucesso! {arquivo_path}")

# extrair o nome do arquivo 
nome_arquivo = os.path.basename(arquivo_path)
print(f"Nome do arquivo selecionado: {nome_arquivo}")

# extrair do nome_arquivo o que estiver até o segundo '_' descartando esse valor
# Exemplo: '2023_10_01_Escala_Simplificada.pdf' -> '2023_10'
# Se não houver segundo '_', manter o nome original
partes_nome = nome_arquivo.split('_')
if len(partes_nome) > 4:
    nome_arquivo = '_'.join(partes_nome[0:])
else:
    nome_arquivo = partes_nome[0]

# nome_arquivo = nome_arquivo.replace('.pdf', '.txt')  # substitui a extensão .pdf por .txt
nome_arquivo = nome_arquivo.replace('_TERCEIRA_VERSAO', '_QUARTA_VERSAO')

print(f"Nome do arquivo modificado: {nome_arquivo}")

def gravar_arquivo(diretorio_path, nome_arquivo, conteudo):
    if not os.path.exists(diretorio_path):
        os.makedirs(diretorio_path)
    
    caminho_completo = os.path.join(diretorio_path, nome_arquivo)

    tabela.to_csv(caminho_completo, index=False)

    print(f"Arquivo gravado com sucesso em: {caminho_completo}")
    return caminho_completo

#path = filedialog.askopenfilename()
tabela = pd.read_csv(arquivo_path, sep=",", encoding='ISO-8859-1')

# SELECIONAR O ARQUIVO AEROPORTOS COMPLETO 
#path_aeroportos = os.path.join(os.path.dirname(__file__), "..", "ARQUIVOS COMUNS", "airports2.csv")
path_aeroportos = (r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\todos_aeroportos.json")  # Garantir que o caminho seja compatível com sistemas Unix

print(' O CAMINHO ATUAL É :', path_aeroportos)

# Verificar se o arquivo foi selecionado e existe
if not os.path.exists(path_aeroportos):
    print(f"❌ Arquivo não encontrado: {path_aeroportos}")
    # Tentar caminho alternativo
    path_aeroportos = r"G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS\airports2.csv"
    if not os.path.exists(path_aeroportos):
        print("❌ Arquivo aeroportos não encontrado em nenhum caminho!")
        exit()

try:
    # Carregar o arquivo JSON em vez de CSV
    print("🔄 Carregando arquivo de aeroportos (JSON)...")
    
    with open(path_aeroportos, 'r', encoding='utf-8') as f:
        dados_aeroportos = json.load(f)
    
    # Converter JSON para DataFrame
    df_aeroportos_IATA = pd.DataFrame(dados_aeroportos)
    
    print(f"✅ Arquivo JSON de aeroportos carregado com sucesso.")
    print(f"📊 Número de aeroportos carregados: {len(df_aeroportos_IATA)}")
    
    # Verificar as colunas disponíveis no DataFrame
    print(f"📋 Colunas disponíveis: {list(df_aeroportos_IATA.columns)}")
    
    # Verificar se as colunas necessárias existem
    if 'IATA' not in df_aeroportos_IATA.columns:
        # Se não existe coluna IATA, tentar identificar qual coluna contém os códigos IATA
        print("⚠️ Coluna 'IATA' não encontrada. Verificando estrutura do JSON...")
        print(f"📋 Primeiras 3 linhas do DataFrame:")
        print(df_aeroportos_IATA.head(3))
        
        # Tentar renomear colunas com base na estrutura comum
        if 'iata' in df_aeroportos_IATA.columns:
            df_aeroportos_IATA = df_aeroportos_IATA.rename(columns={'iata': 'IATA'})
        elif 'code' in df_aeroportos_IATA.columns:
            df_aeroportos_IATA = df_aeroportos_IATA.rename(columns={'code': 'IATA'})
            
    # Reindexar o DataFrame
    df_aeroportos_IATA = df_aeroportos_IATA.reset_index(drop=True)
    
    print(f"📊 Dados de aeroportos finais: {len(df_aeroportos_IATA)} registros")
    
except FileNotFoundError:
    print(f"❌ Arquivo não encontrado: {path_aeroportos}")
    exit()
except json.JSONDecodeError as e:
    print(f"❌ Erro ao decodificar JSON: {e}")
    exit()
except PermissionError as e:
    print(f"❌ Erro de permissão: {e}")
    exit()
except Exception as e:
    print(f"❌ Ocorreu um erro ao carregar aeroportos: {e}")
    exit()
# LIMPAR O TERMINAL
os.system('cls' if os.name == 'nt' else 'clear')

# CRIAR BARRA DE PROGRESSO
tqdm.pandas()

# MOSTRAR A EVOLUÇÃO DO PROCESSO
print(' INICIANDO A TAREFA DE CÁLCULOS BÁSICOS DA ESCALA')
print(' AGUARDE ...')

# CONVERTER AS COLUNAS Checkin, Start, End e Checkout PARA DATETIME
print("🔄 Convertendo datas com formato flexível...")
tabela['Checkin'] = tabela['Checkin'].apply(converter_data_flexivel)
tabela['Start'] = tabela['Start'].apply(converter_data_flexivel)
tabela['End'] = tabela['End'].apply(converter_data_flexivel)
tabela['Checkout'] = tabela['Checkout'].apply(converter_data_flexivel)

tabela['Tempo Apresentacao'] = 0
tabela['Operacao'] = 0
tabela['Tempo Solo'] = 0
tabela['Jornada'] = 0
tabela['Repouso'] = 0
tabela['Repouso Extra'] = 0
tabela['Diurno'] = 0
tabela['Noturno'] = 0
tabela['Especial'] = 0
tabela['Especial Noturno'] = 0

# CONVERTER AS COLUNAS ACIMMA PARA TIMEDELTA
tabela['Tempo Apresentacao'] = pd.to_timedelta(tabela['Tempo Apresentacao'])
tabela['Operacao'] = pd.to_timedelta(tabela['Operacao'])
tabela['Tempo Solo'] = pd.to_timedelta(tabela['Tempo Solo'])
tabela['Jornada'] = pd.to_timedelta(tabela['Jornada'])
tabela['Repouso'] = pd.to_timedelta(tabela['Repouso'])
tabela['Repouso Extra'] = pd.to_timedelta(tabela['Repouso Extra'])
tabela['Diurno'] = pd.to_timedelta(tabela['Diurno'])
tabela['Noturno'] = pd.to_timedelta(tabela['Noturno'])
tabela['Especial'] = pd.to_timedelta(tabela['Especial'])
tabela['Especial Noturno'] = pd.to_timedelta(tabela['Especial Noturno'])

voo = [
'SFX',
'CPT',
'APT',
'FPT',
'FSX',
'FSY',
'FS',
'BUS'
]

tabela = tabela.reset_index(drop=True)

######### CARREGAMENTO DO ARQUIVO FERIADOS.JSON DO IBGE #########
print("📅 Carregando arquivo de feriados do IBGE...")

# Caminho fixo para o arquivo feriados.json baixado do IBGE
path_feriados = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\feriados.json"

print(f"📂 Caminho do arquivo feriados: {path_feriados}")

try:
    # Carregar o arquivo JSON
    with open(path_feriados, 'r', encoding='utf-8') as f:
        feriados_originais = json.load(f)
    
    print(f"✅ Arquivo feriados.json carregado com sucesso!")
    print(f"📊 Total de feriados carregados: {len(feriados_originais)}")
    
    # Converter as datas do formato original para DD/MM/YYYY
    feriados = []
    for feriado in feriados_originais:
        try:
            # Detectar formato da data original
            data_original = feriado.get('date', '')
            
            # Se já está no formato DD/MM/YYYY, manter
            if '/' in data_original:
                feriados.append(feriado)
            # Se está no formato YYYY-MM-DD, converter
            elif '-' in data_original and len(data_original) == 10:
                data_convertida = datetime.strptime(data_original, '%Y-%m-%d')
                feriado_convertido = {
                    'date': data_convertida.strftime('%d/%m/%Y'),
                    'name': feriado.get('name', ''),
                    'type': feriado.get('type', '')
                }
                feriados.append(feriado_convertido)
            else:
                print(f"⚠️ Formato de data não reconhecido: {data_original}")
                
        except Exception as e:
            print(f"⚠️ Erro ao converter feriado: {feriado} - {e}")
    
    print(f"✅ Conversão concluída! {len(feriados)} feriados convertidos para DD/MM/YYYY")
    
    # Verificar se 01/05/2018 está na lista
    encontrou_2018 = False
    for feriado in feriados:
        if feriado['date'] == '01/05/2018':
            print(f"✅ Confirmado: {feriado['name']} em {feriado['date']}")
            encontrou_2018 = True
            break
    
    if not encontrou_2018:
        print("❌ Feriado 01/05/2018 NÃO encontrado na lista!")
    
except FileNotFoundError:
    print(f"❌ Arquivo não encontrado: {path_feriados}")
    print("💡 Verifique se o arquivo existe no diretório especificado.")
    exit()
except Exception as e:
    print(f"❌ Erro ao carregar arquivo de feriados: {e}")
    exit()

# Exibir alguns feriados para verificação
print("\n🔍 Primeiros 10 feriados carregados:")
for i, feriado in enumerate(feriados[:10]):
    print(f"   {i+1}. {feriado['date']} - {feriado['name']}")

####### FINAL DO CARREGAMENTO DOS FERIADOS #########

######### CRIAÇÃO DAS DEFS PARA CALCULAR OS VALORES DE DIURNO, NOTURNO, ESPECIAL E ESPECIAL NOTURNO #####
def diurno(start, end):
    if start.time() >= time(6, 0) and start.time() < time(18, 0):
        if end.time() >= time(6, 0) and end.time() < time(18, 0):
            return end - start
        elif end.time() >= time(18, 0):
            return datetime.combine(start.date(), time(18, 0)) - start
    elif start.time() < time(6, 0):
        if end.time() >= time(6, 0):
            return datetime.combine(start.date(), time(6, 0)) - start
    return timedelta(0)      

def noturno(operacao, diurno):
    return operacao - diurno

def verificar_internacional(row, aeroportos_IATA):
    dep_presente = row['Dep'] in aeroportos_IATA['IATA'].values
    arr_presente = row['Arr'] in aeroportos_IATA['IATA'].values
    return 'N' if dep_presente and arr_presente else 'S'

########## FINAL DAS DEFS ##########

# SE COLUNA Id_Leg = '-I' ou = '-IF' o Tempo Apresentacao será o resultado de Start - Checkin
tabela['Operacao'] = tabela['End'] - tabela['Start']

# SE A COLUNA Id_Leg == '-I' ou == '-IF' o Tempo Apresentacao será o resultado de Start - Checkin
tabela.loc[tabela['Id_Leg'] == '-I', 'Tempo Apresentacao'] = tabela['Start'] - tabela['Checkin']
tabela.loc[tabela['Id_Leg'] == '-IF', 'Tempo Apresentacao'] = tabela['Start'] - tabela['Checkin']

# SE A COLUNA Id_Leg == '-I' ou == '-M' o Tempo Solo será o resultado de End - Start DA LINHA SEGUINTE
# Caso 1: Id_Leg = '-I' e a próxima linha Id_Leg = '-M'
mask1 = (tabela['Id_Leg'] == '-I') & (tabela['Id_Leg'].shift(-1) == '-M')
tabela.loc[mask1, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

# Caso 2: Id_Leg = '-M' e a próxima linha Id_Leg = '-M'
mask2 = (tabela['Id_Leg'] == '-M') & (tabela['Id_Leg'].shift(-1) == '-M')
tabela.loc[mask2, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

# Caso 3: Id_Leg = '-I' e a próxima linha Id_Leg = '-F'
mask3 = (tabela['Id_Leg'] == '-I') & (tabela['Id_Leg'].shift(-1) == '-F')
tabela.loc[mask3, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

# Caso 4: Id_Leg = '-M' e a próxima linha Id_Leg = '-F'
mask4 = (tabela['Id_Leg'] == '-M') & (tabela['Id_Leg'].shift(-1) == '-F')
tabela.loc[mask4, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

# Para os demais casos, 'Tempo Solo' permanece não calculado (NaN)

# SE A COLUNA Id_Leg == '-I' ou == '-IF' a Jornada será o resultado de Checkout - Checkin + 30 minutos
tabela.loc[tabela['Id_Leg'] == '-F', 'Jornada'] = (tabela['Checkout'] - tabela['Checkin']) + timedelta(minutes=30)
tabela.loc[tabela['Id_Leg'] == '-IF', 'Jornada'] = (tabela['Checkout'] - tabela['Checkin']) + timedelta(minutes=30)

# SE A COLUNA Id_Leg == '-F' ou == '-IF' o Repouso será o resultado de  'Checkin' da proxima linha - 'Checkout' da linha atual
tabela.loc[tabela['Id_Leg'] == '-F', 'Repouso'] = tabela['Checkin'].shift(-1) - tabela['Checkout']
tabela.loc[tabela['Id_Leg'] == '-IF', 'Repouso'] = tabela['Checkin'].shift(-1) - tabela['Checkout']

# SE A COLUNA Id_Leg == '-F' ou == '-IF' e Repouso > que 12 horas o Repouso Extra será o resultado de  'Checkin' da proxima linha - 'Checkout' da linha atual
tabela.loc[(tabela['Id_Leg'] == '-F') & (tabela['Repouso'] > timedelta(hours=12)), 'Repouso Extra'] = tabela['Repouso'] - timedelta(hours=12)
tabela.loc[(tabela['Id_Leg'] == '-IF') & (tabela['Repouso'] > timedelta(hours=12)), 'Repouso Extra'] = tabela['Repouso'] - timedelta(hours=12)

# Aplicar a função diurno linha por linha
tabela['Diurno'] = tabela.apply(lambda row: diurno(row['Start'], row['End']), axis=1)

# Aplicar a função noturno linha por linha
tabela['Noturno'] = tabela.apply(lambda row: noturno(row['Operacao'], row['Diurno']), axis=1)

# PREPARAR PARA OS CÁLCULOS DE ESPECIAL E ESPECIAL NOTURNO
# neste caso do sábado apenas haverá noturno e especial noturno

tabela['Especial Noturno'] = tabela.apply(lambda row: row['Noturno'] if row['Start'].weekday() == 5 and row['Start'].time() >= time(21, 0) else timedelta(0), axis=1)

tabela['Especial Noturno'] = tabela.apply(lambda row: row['Noturno'] if row['Start'].weekday() == 6 and row['Start'].time() <= time(21, 0) else timedelta(0), axis=1)

tabela['Especial'] = tabela.apply(lambda row: row['Diurno'] if row['Start'].weekday() == 6 and row['Start'].time() <= time(18, 0) else timedelta(0), axis=1)

# CÁLCULO DE ESPECIAL E ESPECIAL NOTURNO BASEADO NOS FERIADOS
print("📅 Processando feriados para cálculos especiais...")
try:
    # CORREÇÃO: Converter as datas do START e END para comparação
    tabela['Start_date'] = tabela['Start'].dt.date
    tabela['End_date'] = tabela['End'].dt.date

    # Converter as datas dos feriados para datetime.date (FORMATO DD/MM/YYYY)
    feriados_dates = []
    for feriado in feriados:
        try:
            data_feriado = datetime.strptime(feriado['date'], '%d/%m/%Y').date()
            feriados_dates.append(data_feriado)
        except Exception as e:
            print(f"⚠️ Erro ao converter data do feriado: {feriado['date']} - {e}")

    print(f"✅ {len(feriados_dates)} datas de feriados convertidas para comparação")

    # CORREÇÃO: Aplicar cálculo baseado na data do START (início da operação)
    # Se o START foi em feriado, aplicar valores especiais
    tabela['Especial'] = tabela.apply(lambda row: row['Diurno'] if row['Start_date'] in feriados_dates else row['Especial'], axis=1)
    tabela['Especial Noturno'] = tabela.apply(lambda row: row['Noturno'] if row['Start_date'] in feriados_dates else row['Especial Noturno'], axis=1)
    
    print("✅ Cálculo de feriados concluído com sucesso!")
    
except Exception as e:
    print(f"⚠️ Erro no processamento de feriados: {e}")
    print("💡 Continuando sem cálculo de feriados...")

# Verificar se os valores das colunas 'Dep' e 'Arr' do dataframe tabela estão presentes no DataFrame df_aeroportos_IATA
# Se estiverem presentes a coluna 'Internacional' será 'N', caso contrário será 'S'

tabela['Internacional'] = tabela.apply(lambda row: verificar_internacional(row, df_aeroportos_IATA), axis=1)

##### MOSTRAR E GRAVAR ARQUIVO FINAL COM TODOS OS CÁLCULOS
colunas = ["Activity","Tempo Apresentacao", "Operacao", "Tempo Solo", "Jornada", "Repouso", "Repouso Extra", "Diurno", "Noturno", "Especial", "Especial Noturno", "Internacional"]

# CONFIGURAR A IMPRIMESSÃO DE TODAS AS LINHAS DO DATAFRAME
pd.set_option('display.max_rows', None)

### incluir no final 

#path = arquivo_path.replace('_SEGUNDA_VERSAO.csv', '_TERCEIRA_VERSAO.csv')
#escala.to_csv(path, index=False)
#print(' TAREFA REALIZADA COM SUCESSO :')
# Funçã o gravar_arquivo
diretorio_path = diretorio_path.replace('Escalas_Executadas', 'Auditoria_Calculos')

# chamar a função gravar_arquivo
conteudo_exemplo = "Este é um exemplo de conteúdo para o arquivo."
caminho_arquivo_gravado = gravar_arquivo(diretorio_path, nome_arquivo, conteudo_exemplo)

data_completa = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# imprimir TAREFA CONCLUÍDA e data completa do sistema
print(f"TAREFA CONCLUIDA COM SUCESSO: {data_completa}")



