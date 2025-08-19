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
    
    meses_pt = {
        "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
        "july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
        "jan":1,"feb":2,"mar":3,"apr":4,"jun":6,"jul":7,"aug":8,"sep":9,"sept":9,"oct":10,"nov":11,"dec":12,
        "janeiro":1,"fevereiro":2,"março":3,"marco":3,"abril":4,"maio":5,"junho":6,
        "julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12,
        "jan.":1,"fev.":2,"mar.":3,"abr.":4,"mai.":5,"jun.":6,"jul.":7,"ago.":8,"set.":9,"out.":10,"nov.":11,"dez.":12,
    }
    
    try:
        return pd.to_datetime(data_str, dayfirst=True, errors='coerce')
    except Exception:
        try:
            if any(mes in str(data_str).lower() for mes in meses_pt.keys()):
                data_str = str(data_str).upper()
                for mes_pt, mes_num in meses_pt.items():
                    if mes_pt.upper() in data_str:
                        partes = data_str.split()
                        data_parte = partes[0]
                        hora_parte = partes[1] if len(partes) > 1 else "00:00"
                        dia = data_parte[:2]
                        mes = mes_num
                        ano = "20" + data_parte[-2:]
                        data_formatada = f"{ano}-{mes}-{dia} {hora_parte}"
                        return pd.to_datetime(data_formatada, errors='coerce')
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
                    return pd.to_datetime(data_str, format=formato, dayfirst=True, errors='coerce')
                except Exception:
                    continue
        except Exception:
            pass
    print(f"Não foi possível converter a data: {data_str}")
    return pd.NaT

warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

def selecionar_diretorio():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Seleção de Diretório", "Selecione o diretório onde estão os arquivos necessários.")
    path = filedialog.askdirectory()
    return path

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo ricardo_lazzarini_vcp_3394_112017_022023__TERCEIRA_VERSAO.csv")
    root.update()
    path = filedialog.askopenfilename()
    return path

diretorio_path = selecionar_diretorio()
print(f"Diretório selecionado com sucesso! {diretorio_path}")

arquivo_path = selecionar_arquivo()
print(f"Arquivo selecionado com sucesso! {arquivo_path}")

nome_arquivo = os.path.basename(arquivo_path)
print(f"Nome do arquivo selecionado: {nome_arquivo}")

partes_nome = nome_arquivo.split('_')
if len(partes_nome) > 4:
    nome_arquivo = '_'.join(partes_nome[0:])
else:
    nome_arquivo = partes_nome[0]

nome_arquivo = nome_arquivo.replace('_TERCEIRA_VERSAO', '_QUARTA_VERSAO')
print(f"Nome do arquivo modificado: {nome_arquivo}")

def gravar_arquivo(diretorio_path, nome_arquivo, conteudo):
    if not os.path.exists(diretorio_path):
        os.makedirs(diretorio_path)
    caminho_completo = os.path.join(diretorio_path, nome_arquivo)
    tabela.to_csv(caminho_completo, index=False)
    print(f"Arquivo gravado com sucesso em: {caminho_completo}")
    return caminho_completo

tabela = pd.read_csv(arquivo_path, sep=",", encoding='ISO-8859-1')

path_aeroportos = (r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\todos_aeroportos.json")
print('O CAMINHO ATUAL É:', path_aeroportos)

if not os.path.exists(path_aeroportos):
    print(f"Arquivo não encontrado: {path_aeroportos}")
    path_aeroportos = r"G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS\airports2.csv"
    if not os.path.exists(path_aeroportos):
        print("Arquivo aeroportos não encontrado em nenhum caminho!")
        exit()

try:
    print("Carregando arquivo de aeroportos (JSON)...")
    with open(path_aeroportos, 'r', encoding='utf-8') as f:
        dados_aeroportos = json.load(f)
    df_aeroportos_IATA = pd.DataFrame(dados_aeroportos)
    print(f"Arquivo JSON de aeroportos carregado com sucesso.")
    print(f"Número de aeroportos carregados: {len(df_aeroportos_IATA)}")
    print(f"Colunas disponíveis: {list(df_aeroportos_IATA.columns)}")
    if 'IATA' not in df_aeroportos_IATA.columns:
        print("Coluna 'IATA' não encontrada. Verificando estrutura do JSON...")
        print(f"Primeiras 3 linhas do DataFrame:")
        print(df_aeroportos_IATA.head(3))
        if 'iata' in df_aeroportos_IATA.columns:
            df_aeroportos_IATA = df_aeroportos_IATA.rename(columns={'iata': 'IATA'})
        elif 'code' in df_aeroportos_IATA.columns:
            df_aeroportos_IATA = df_aeroportos_IATA.rename(columns={'code': 'IATA'})
    df_aeroportos_IATA = df_aeroportos_IATA.reset_index(drop=True)
    print(f"Dados de aeroportos finais: {len(df_aeroportos_IATA)} registros")
except FileNotFoundError:
    print(f"Arquivo não encontrado: {path_aeroportos}")
    exit()
except json.JSONDecodeError as e:
    print(f"Erro ao decodificar JSON: {e}")
    exit()
except PermissionError as e:
    print(f"Erro de permissão: {e}")
    exit()
except Exception as e:
    print(f"Ocorreu um erro ao carregar aeroportos: {e}")
    exit()

os.system('cls' if os.name == 'nt' else 'clear')

tqdm.pandas()

print('INICIANDO A TAREFA DE CÁLCULOS BÁSICOS DA ESCALA')
print('AGUARDE ...')

print("Convertendo datas com formato flexível...")
for col in ['Checkin', 'Start', 'End', 'Checkout']:
    if col in tabela.columns:
        tabela[col] = tabela[col].apply(converter_data_flexivel)

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

print("Carregando arquivo de feriados do IBGE...")

path_feriados = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\feriados.json"
print(f"Caminho do arquivo feriados: {path_feriados}")

try:
    with open(path_feriados, 'r', encoding='utf-8') as f:
        feriados_originais = json.load(f)
    print(f"Arquivo feriados.json carregado com sucesso!")
    print(f"Total de feriados carregados: {len(feriados_originais)}")
    feriados = []
    for feriado in feriados_originais:
        try:
            data_original = feriado.get('date', '')
            if '/' in data_original:
                feriados.append(feriado)
            elif '-' in data_original and len(data_original) == 10:
                data_convertida = datetime.strptime(data_original, '%Y-%m-%d')
                feriado_convertido = {
                    'date': data_convertida.strftime('%d/%m/%Y'),
                    'name': feriado.get('name', ''),
                    'type': feriado.get('type', '')
                }
                feriados.append(feriado_convertido)
            else:
                print(f"Formato de data não reconhecido: {data_original}")
        except Exception as e:
            print(f"Erro ao converter feriado: {feriado} - {e}")
    print(f"Conversão concluída! {len(feriados)} feriados convertidos para DD/MM/YYYY")
    encontrou_2018 = False
    for feriado in feriados:
        if feriado['date'] == '01/05/2018':
            print(f"Confirmado: {feriado['name']} em {feriado['date']}")
            encontrou_2018 = True
            break
    if not encontrou_2018:
        print("Feriado 01/05/2018 NÃO encontrado na lista!")
except FileNotFoundError:
    print(f"Arquivo não encontrado: {path_feriados}")
    print("Verifique se o arquivo existe no diretório especificado.")
    exit()
except Exception as e:
    print(f"Erro ao carregar arquivo de feriados: {e}")
    exit()

print("\nPrimeiros 10 feriados carregados:")
for i, feriado in enumerate(feriados[:10]):
    print(f"   {i+1}. {feriado['date']} - {feriado['name']}")

def diurno(start, end):
    if pd.isna(start) or pd.isna(end):
        return timedelta(0)
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

tabela['Operacao'] = tabela['End'] - tabela['Start']

tabela.loc[tabela['Id_Leg'] == '-I', 'Tempo Apresentacao'] = tabela['Start'] - tabela['Checkin']
tabela.loc[tabela['Id_Leg'] == '-IF', 'Tempo Apresentacao'] = tabela['Start'] - tabela['Checkin']

mask1 = (tabela['Id_Leg'] == '-I') & (tabela['Id_Leg'].shift(-1) == '-M')
tabela.loc[mask1, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

mask2 = (tabela['Id_Leg'] == '-M') & (tabela['Id_Leg'].shift(-1) == '-M')
tabela.loc[mask2, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

mask3 = (tabela['Id_Leg'] == '-I') & (tabela['Id_Leg'].shift(-1) == '-F')
tabela.loc[mask3, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

mask4 = (tabela['Id_Leg'] == '-M') & (tabela['Id_Leg'].shift(-1) == '-F')
tabela.loc[mask4, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

tabela.loc[tabela['Id_Leg'] == '-F', 'Jornada'] = (tabela['Checkout'] - tabela['Checkin']) + timedelta(minutes=30)
tabela.loc[tabela['Id_Leg'] == '-IF', 'Jornada'] = (tabela['Checkout'] - tabela['Checkin']) + timedelta(minutes=30)

tabela.loc[tabela['Id_Leg'] == '-F', 'Repouso'] = tabela['Checkin'].shift(-1) - tabela['Checkout']
tabela.loc[tabela['Id_Leg'] == '-IF', 'Repouso'] = tabela['Checkin'].shift(-1) - tabela['Checkout']

tabela.loc[(tabela['Id_Leg'] == '-F') & (tabela['Repouso'] > timedelta(hours=12)), 'Repouso Extra'] = tabela['Repouso'] - timedelta(hours=12)
tabela.loc[(tabela['Id_Leg'] == '-IF') & (tabela['Repouso'] > timedelta(hours=12)), 'Repouso Extra'] = tabela['Repouso'] - timedelta(hours=12)

tabela['Diurno'] = tabela.apply(lambda row: diurno(row['Start'], row['End']), axis=1)
tabela['Noturno'] = tabela.apply(lambda row: noturno(row['Operacao'], row['Diurno']), axis=1)

tabela['Especial Noturno'] = tabela.apply(lambda row: row['Noturno'] if not pd.isna(row['Start']) and row['Start'].weekday() == 5 and row['Start'].time() >= time(21, 0) else timedelta(0), axis=1)
tabela['Especial Noturno'] = tabela.apply(lambda row: row['Noturno'] if not pd.isna(row['Start']) and row['Start'].weekday() == 6 and row['Start'].time() <= time(21, 0) else timedelta(0), axis=1)
tabela['Especial'] = tabela.apply(lambda row: row['Diurno'] if not pd.isna(row['Start']) and row['Start'].weekday() == 6 and row['Start'].time() <= time(18, 0) else timedelta(0), axis=1)

print("Processando feriados para cálculos especiais...")
try:
    tabela['Start_date'] = tabela['Start'].dt.date
    tabela['End_date'] = tabela['End'].dt.date

    feriados_dates = []
    for feriado in feriados:
        try:
            data_feriado = datetime.strptime(feriado['date'], '%d/%m/%Y').date()
            feriados_dates.append(data_feriado)
        except Exception as e:
            print(f"Erro ao converter data do feriado: {feriado['date']} - {e}")

    print(f"{len(feriados_dates)} datas de feriados convertidas para comparação")

    tabela['Especial'] = tabela.apply(lambda row: row['Diurno'] if not pd.isna(row['Start_date']) and row['Start_date'] in feriados_dates else row['Especial'], axis=1)
    tabela['Especial Noturno'] = tabela.apply(lambda row: row['Noturno'] if not pd.isna(row['Start_date']) and row['Start_date'] in feriados_dates else row['Especial Noturno'], axis=1)
    
    print("Cálculo de feriados concluído com sucesso!")
    
except Exception as e:
    print(f"Erro no processamento de feriados: {e}")
    print("Continuando sem cálculo de feriados...")

tabela['Internacional'] = tabela.apply(lambda row: verificar_internacional(row, df_aeroportos_IATA), axis=1)

colunas = ["Activity","Tempo Apresentacao", "Operacao", "Tempo Solo", "Jornada", "Repouso", "Repouso Extra", "Diurno", "Noturno", "Especial", "Especial Noturno", "Internacional"]

pd.set_option('display.max_rows', None)

diretorio_path = diretorio_path.replace('Escalas_Executadas', 'Auditoria_Calculos')

# 🔧 Padronizar todas as datas para o formato %d/%m/%Y %H:%M
for col in ['Checkin', 'Start', 'End', 'Checkout']:
    if col in tabela.columns:
        tabela[col] = pd.to_datetime(tabela[col], errors='coerce', dayfirst=True)
        tabela[col] = tabela[col].dt.strftime('%d/%m/%Y %H:%M')

conteudo_exemplo = "Este é um exemplo de conteúdo para o arquivo."
caminho_arquivo_gravado = gravar_arquivo(diretorio_path, nome_arquivo, conteudo_exemplo)

data_completa = datetime.now().strftime("%d/%m/%Y %H:%M")
print(f"TAREFA CONCLUIDA COM SUCESSO: {data_completa}")