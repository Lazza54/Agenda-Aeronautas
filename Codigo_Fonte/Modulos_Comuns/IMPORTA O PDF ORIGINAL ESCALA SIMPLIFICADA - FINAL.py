#
##### ---------------ESTE CÓDIGO IMPORTA OS DADOS DA ESCALA PDF ORIUNDA DO SISTEMA SIMPLIFICADO.PDF
#                    E GERA O CSV DO MESMO NOME ADICIONADO _PRIMEIRA VERSÃO
#
# AUTOR: RICARDO LAZZARINI
# DATA DE CRIAÇÃO: 2025
# ÚLTIMA VERIFICAÇÃO: 27/06/2025
#
import os

# Configurar Java antes de importar tabula
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'
os.environ['PATH'] = r'C:\Program Files\Java\jdk-21\bin;' + os.environ.get('PATH', '')


# Verificar se Java está acessível
try:
    import subprocess
    result = subprocess.run(['java', '-version'], capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        print("   ✅ Java configurado com sucesso")
    else:
        print("   ⚠️ Aviso: Java pode não estar configurado corretamente")
except Exception as e:
    print(f"   ⚠️ Erro ao verificar Java: {e}")

from tabula.io import read_pdf
import tabula
import numpy as np
import pandas as pd
from dateutil import tz
from datetime import timedelta, time, datetime, date, tzinfo, timezone
import warnings
from tqdm import tqdm
import tkinter as tk
from tkinter import messagebox, filedialog

warnings.filterwarnings("ignore")

# %% [markdown]
# TKINTER É A BIBLIOTECA QUE POSSIBILITA A INTERFACE  

# %%

# FUNÇÃO PARA DETERMINAR DIRETORIO DE ARQUIVO E NOME DO ARQUIVO A SER UTILIZADO

def selecionar_diretorio():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    
    messagebox.showinfo("Seleção de Diretório", "Selecione o diretório onde estão os arquivos necessários - ddd.")

    path = filedialog.askdirectory()
    return path

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal

    messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo que deseja importar - aaa.")
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
    nome_arquivo = '_'.join(partes_nome[2:])
else:
    nome_arquivo = partes_nome[0]

# nome_arquivo = nome_arquivo.replace('.pdf', '.txt')  # substitui a extensão .pdf por .txt
nome_arquivo = nome_arquivo.replace('.pdf', '_PRIMEIRA_VERSAO.csv')

print(f"Nome do arquivo modificado: {nome_arquivo}")

def gravar_arquivo(diretorio_path, nome_arquivo, conteudo):
    if not os.path.exists(diretorio_path):
        os.makedirs(diretorio_path)
    
    caminho_completo = os.path.join(diretorio_path, nome_arquivo)

    df_merged.to_csv(caminho_completo, index=False)

    print(f"Arquivo gravado com sucesso em: {caminho_completo}")
    return caminho_completo


# %%
imported_data = tabula.read_pdf(arquivo_path, lattice=True, encoding='utf-8', pages="all")  # retorna uma lista de DataFrames

# %%
len(imported_data)

# %%
df_merged = imported_data[0]
for df_to_concat in imported_data[1:]:
    df_merged = pd.concat([df_merged, df_to_concat])

# %%
# MOSTRA TODOS OS REGISTROS DA DATAFRAME
pd.set_option('display.max_rows', None) 

# %% [markdown]
# INICIA ACERTOS NO DATAFRAME PARA OBTER APENAS OS DADOS DE INTERESSE

# %%
# RETIRAR ',\r'
df_merged.replace(',\r', ' ', regex=True, inplace=True)

# RETIRAR ',\r'
df_merged.replace('\r', ' ', regex=True, inplace=True)

# SUBSTITUIR ',' POR BRANCO
df_merged.replace(',', ' ', regex=True, inplace=True)

# RETIRAR LINHAS DUPLICADAS
df_merged.duplicated()

# DELETAR LINHAS QUE CONTENHAM NA OU NAM EM TUDO
df_merged.dropna(how='all', inplace=True)

# COLOCAR "OCULTO" ONDE 'Activity' ESTEJA NULO
df_merged['Activity'].fillna('OCULTO', inplace=True)

# DELETAR LINHAS COM MAIS DE 3 NAN
df_merged.dropna(thresh=3, inplace=True)

df_merged.reset_index(drop=True, inplace=True)

# criar variável not_flight_activities 
not_flight_activities = ['LOP', 'CMA', 'BUS', 'FR', 'FC', 'FA', 'FER', 'SNA', 'FP', 'FJC', 'DMI24', 'DMI', 'PLT', 'DMF', 'INF', 'SPS', 'SPS24']
tipos_folga = ['FR', 'FC', 'FP', 'FA', 'FJC']
 
# MOSTRAR TODAS AS LINHAS
pd.set_option('display.max_rows', None)        

# %% [markdown]
# QUANDO MUDA DE PÁGINA NO ARQUIVO ORIGINAL ALGUNS DADOS SÃO SEPARADOS EM LINHAS DIFERENTES, FAZER OS REPAROS NECESSÁRIOS

# %%
# QUANDO 'Activity' FOR IGUAL A OCULTO UNIR OS VALORES DE START, DEP, ARR, END AOS VALORES DA PRÓXIMA LINHA E APAGAR A SEGUNDA LINHA

start_row = 0 
for i in tqdm(range(start_row, len(df_merged)), desc="Processando"):
    
    if df_merged['Activity'].iloc[i] == 'OCULTO': 

        if df_merged['Checkin'].iloc[i] != 'NaN':
            tm = (df_merged['Checkin'].iloc[i])  # apenas o valor de checkin
        if df_merged['Start'].iloc[i] != 'NaN':
            tm1 = (df_merged['Start'].iloc[i])  # apenas o valor de start
        if df_merged['End'].iloc[i] != 'NaN':
            tm2 = (df_merged['End'].iloc[i])  # apenas o valor de end
        if df_merged['Checkout'].iloc[i] != 'NaN':
            tm3 = (df_merged['Checkout'].iloc[i])  # apenas o valor de checkout
        
        i -= 1
        if df_merged['Checkin'].iloc[i] != 'NaN':
            dt = (df_merged['Checkin'].iloc[i]) 
        if df_merged['Start'].iloc[i] != 'NaN':
            dt1 = (df_merged['Start'].iloc[i])
        if df_merged['End'].iloc[i] != 'NaN':
            dt2 = (df_merged['End'].iloc[i])
        if df_merged['Checkout'].iloc[i] != 'NaN':
            dt3 = (df_merged['Checkout'].iloc[i])

        if df_merged['Checkin'].iloc[i] != 'NaN':
            combined = (str(dt) + ' ' + str(tm))
        if df_merged['Start'].iloc[i] != 'NaN':
            combined1 = (str(dt1) + " " + str(tm1))        
        if df_merged['End'].iloc[i] != 'NaN':
            combined2 = (str(dt2) + " " + str(tm2))        
        if df_merged['Checkout'].iloc[i] != 'NaN':
            combined3 = (str(dt3) + " " + str(tm3))        

        df_merged['Checkin'].iloc[i] = combined
        df_merged['Start'].iloc[i] = combined1
        df_merged['End'].iloc[i] = combined2
        df_merged['Checkout'].iloc[i] = combined3

df_merged.reset_index(drop=True, inplace=True)

# %%
# ELIMINAR LINHAS ONDE CONSTE 'OCULTO' NA COLUNA 'Activity'
df_merged.drop(df_merged.loc[df_merged['Activity'] == 'OCULTO'].index, inplace=True)

df_merged.drop(df_merged.loc[df_merged['Activity'] == 'TOTAL:'].index, inplace=True)

# SUBSTITUIR '\r' POR BRANCO
df_merged.replace('\r', ' ', regex=True, inplace=True)

# SUBSTITUIR  - nan,' POR '-'
df_merged.replace('- nan', '-', regex=True, inplace=True)

df_merged.reset_index(drop=True, inplace=True)

linhas_vazias = df_merged[df_merged[['Checkin', 'Start', 'End', 'Checkout']].isnull().all(axis=1)]

for i in range(len(df_merged)):
    
    ##### AS ATIVIDADES DE NÃO VOO DEVEM TER O MESMO HORÁRIO DE CHECKIN E START
    if df_merged['Activity'].iloc[i][0:2] != 'AD' and df_merged['Checkin'].iloc[i] == '-':
        df_merged['Checkin'].iloc[i] = df_merged['Start'].iloc[i]
    
    #### PREENCHER Checkout vazio com End para TODAS as atividades (não apenas 'AD')
    if df_merged['Checkout'].iloc[i] == '-' or df_merged['Checkout'].iloc[i] == '':
        df_merged['Checkout'].iloc[i] = df_merged['End'].iloc[i]

df_merged.reset_index(drop=True, inplace=True)

# var_checki_temp = Checkin quando diferente de '-', filtrar as linhas até que o checkin seja diferente de '-' então alocar 
# nos checkin das linhas filtradas o valor que está na variável var_checki_temp
# Supondo que a coluna seja 'Checkin' e o DataFrame seja df_primary
import pandas as pd

# Encontrar os índices onde Checkin é diferente de '-'
indices = df_merged.index[df_merged['Checkin'] != '-'].tolist()

for i in range(len(indices)):
    idx_inicio = indices[i]
    # Define idx_fim: até a próxima linha com Checkin diferente de '-' ou até o final
    if i + 1 < len(indices):
        idx_fim = indices[i + 1]
    else:
        idx_fim = len(df_merged)
    # Filtra o bloco
    bloco = df_merged.iloc[idx_inicio:idx_fim].copy()
    if bloco.empty:
        continue
    # Valor inicial de Checkin e valor final de Checkout
    checkin_inicial = bloco.iloc[0]['Checkin']
    checkout_final = bloco.iloc[-1]['Checkout']
    # Substitui '-' em Checkin pelo valor inicial
    bloco['Checkin'] = bloco['Checkin'].replace('-', checkin_inicial)
    # Todos os Checkout recebem o valor final
    bloco['Checkout'] = checkout_final
    # Atualiza no DataFrame original
    df_merged.iloc[idx_inicio:idx_fim] = bloco.values

# Função para converter datas com múltiplos formatos
def convert_date_column(series, column_name):
    print(f"🔄 Convertendo coluna {column_name}...")
    
    # Mostrar algumas amostras antes da conversão
    samples = series.dropna().head(10).tolist()
    #print(f"   Amostras encontradas: {samples[:5]}")
    
    # Função especial para lidar com anos problemáticos
    def fix_year_format(date_str):
        """Corrige problemas específicos de ano"""
        if pd.isna(date_str) or date_str == '-':
            return date_str
        
        date_str = str(date_str).strip()
        
        # Corrigir DEC18 -> DEC2018 (dezembro 2018)
        if 'DEC18' in date_str.upper():
            date_str = date_str.upper().replace('DEC18', 'DEC2018')
        elif 'DEZ18' in date_str.upper():
            date_str = date_str.upper().replace('DEZ18', 'DEC2018')
        
        # Corrigir outros meses problemáticos de 2018
        month_corrections = {
            'JAN18': 'JAN2018', 'FEB18': 'FEB2018', 'MAR18': 'MAR2018',
            'APR18': 'APR2018', 'MAY18': 'MAY2018', 'JUN18': 'JUN2018',
            'JUL18': 'JUL2018', 'AUG18': 'AUG2018', 'SEP18': 'SEP2018',
            'OCT18': 'OCT2018', 'NOV18': 'NOV2018',
            # Versões em português (diferentes das inglesas)
            'FEV18': 'FEB2018', 'ABR18': 'APR2018', 'MAI18': 'MAY2018',
            'AGO18': 'AUG2018', 'SET18': 'SEP2018', 'OUT18': 'OCT2018', 
            'DEZ18': 'DEC2018'
        }
        
        for old, new in month_corrections.items():
            if old in date_str.upper():
                date_str = date_str.upper().replace(old, new)
                break
        
        return date_str
    
    # Aplicar correções de ano
    #print("   🔧 Corrigindo formatos de ano problemáticos...")
    corrected_series = series.apply(fix_year_format)
    
    # Contar correções feitas
    corrections_made = (series.astype(str) != corrected_series.astype(str)).sum()
    if corrections_made > 0:
        print(f"   ✅ {corrections_made} correções de formato aplicadas")
    
    # Lista de formatos a tentar
    formats_to_try = [
        "%d%b%Y %H:%M",     # 01DEC2018 14:30 (formato corrigido)
        "%d%b%y %H:%M",     # 01DEC18 14:30 (formato original)
        "%d/%m/%Y %H:%M",   # 01/12/2018 14:30
        "%d-%m-%Y %H:%M",   # 01-12-2018 14:30
        "%d/%m/%y %H:%M",   # 01/12/18 14:30
        "%d-%m-%y %H:%M"    # 01-12-18 14:30
    ]
    
    converted_series = pd.Series([None] * len(corrected_series), index=corrected_series.index)
    conversion_stats = {}
    
    for fmt in formats_to_try:
        try:
            # Tentar converter apenas valores ainda não convertidos
            mask_not_converted = converted_series.isna()
            temp_converted = pd.to_datetime(corrected_series[mask_not_converted], format=fmt, errors='coerce')
            valid_conversions = temp_converted.notna()
            
            # Atualizar apenas as conversões bem-sucedidas
            converted_series.loc[mask_not_converted & valid_conversions] = temp_converted[valid_conversions]
            
            count = valid_conversions.sum()
            if count > 0:
                conversion_stats[fmt] = count
                print(f"   ✅ Formato '{fmt}': {count} datas convertidas")
        except Exception as e:
            print(f"   ❌ Formato '{fmt}': erro - {e}")
    
    # Tentar conversão automática para valores ainda não convertidos
    mask_remaining = converted_series.isna()
    if mask_remaining.any():
        try:
            auto_converted = pd.to_datetime(corrected_series[mask_remaining], dayfirst=True, errors='coerce')
            valid_auto = auto_converted.notna()
            converted_series.loc[mask_remaining & valid_auto] = auto_converted[valid_auto]
            auto_count = valid_auto.sum()
            if auto_count > 0:
                conversion_stats['automático'] = auto_count
                print(f"   ✅ Formato automático: {auto_count} datas convertidas")
        except Exception as e:
            print(f"   ❌ Conversão automática falhou: {e}")
    
    # Estatísticas finais
    total_converted = converted_series.notna().sum()
    total_original = corrected_series.notna().sum()
    success_rate = (total_converted / total_original * 100) if total_original > 0 else 0
    
    # Criar série de resultado com o mesmo índice
    result = pd.Series([None] * len(corrected_series), index=corrected_series.index, dtype='object')
    
    # Converter para string apenas os valores datetime válidos
    mask_datetime = converted_series.notna()
    if mask_datetime.any():
        try:
            # Verificar se há valores datetime válidos na série
            datetime_subset = converted_series[mask_datetime]
            if hasattr(datetime_subset, 'dt') and len(datetime_subset) > 0:
                result[mask_datetime] = datetime_subset.dt.strftime("%d/%m/%Y %H:%M")
            else:
                # Se não há valores datetime válidos, converter para string simples
                result[mask_datetime] = datetime_subset.astype(str)
        except Exception as e:
            print(f"   ❌ Erro ao formatar datas: {e}")
            # Em caso de erro, converter para string simples
            result[mask_datetime] = converted_series[mask_datetime].astype(str)
    
    # Manter valores originais onde a conversão falhou (exceto NaN e '-')
    mask_failed = converted_series.isna() & corrected_series.notna() & (corrected_series != '-')
    if mask_failed.any():
        failed_count = mask_failed.sum()
        print(f"   ⚠️ {failed_count} valores não puderam ser convertidos, mantendo formato original")
        result[mask_failed] = corrected_series[mask_failed].astype(str)
        
        # Mostrar alguns exemplos de valores que falharam
        failed_examples = corrected_series[mask_failed].head(5).tolist()
        print(f"      Exemplos de falhas: {failed_examples}")
    
    # Manter valores '-' como estão
    mask_dash = (corrected_series == '-')
    if mask_dash.any():
        result[mask_dash] = '-'
    
    return result

# Aplicar conversão para cada coluna
df_merged['Checkin'] = convert_date_column(df_merged['Checkin'], 'Checkin')
df_merged['Start'] = convert_date_column(df_merged['Start'], 'Start')
df_merged['End'] = convert_date_column(df_merged['End'], 'End')
df_merged['Checkout'] = convert_date_column(df_merged['Checkout'], 'Checkout')

df_merged.reset_index(drop=True, inplace=True)

# Verificação específica para dezembro de 2018
december_2018_patterns = ['DEC18', 'DEZ18', '12/2018', '12/18', '/12/2018', '/12/18']

for pattern in december_2018_patterns:
    for col in ['Checkin', 'Start', 'End', 'Checkout']:
        if col in df_merged.columns:
            matches = df_merged[col].astype(str).str.contains(pattern, case=False, na=False)
            count = matches.sum()
            if count > 0:
                print(f"   📅 Coluna {col}: {count} registros contêm '{pattern}'")
                # Mostrar alguns exemplos
                examples = df_merged.loc[matches, col].head(3).tolist()
                print(f"      Exemplos: {examples}")

# Verificar valores NaN após conversão especificamente para dezembro 2018
for col in ['Checkin', 'Start', 'End', 'Checkout']:
    if col in df_merged.columns:
        nan_count = df_merged[col].isna().sum()
        total_count = len(df_merged[col])
        print(f"   {col}: {nan_count}/{total_count} valores NaN ({nan_count/total_count*100:.1f}%)")

# Mostrar algumas linhas onde todas as datas são NaN
all_dates_nan = df_merged[
    df_merged['Checkin'].isna() & 
    df_merged['Start'].isna() & 
    df_merged['End'].isna() & 
    df_merged['Checkout'].isna()
]

if len(all_dates_nan) > 0:
    print(f"\n⚠️ {len(all_dates_nan)} linhas onde TODAS as datas são NaN:")
    print(all_dates_nan[['Activity', 'Checkin', 'Start', 'End', 'Checkout']].head())

#%% [markdown]
# CRIA CÓPIA NO FORMATO .CSV

# %%

####################################################################

# Funçã o gravar_arquivo

diretorio_path = diretorio_path.replace('Escalas_Executadas', 'Auditoria_Calculos')

# chamar a função gravar_arquivo
conteudo_exemplo = "Este é um exemplo de conteúdo para o arquivo."
caminho_arquivo_gravado = gravar_arquivo(diretorio_path, nome_arquivo, conteudo_exemplo)

##################################################################

data_completa = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# imprimir TAREFA CONCLUÍDA e data completa do sistema
print(f"TAREFA CONCLUIDA COM SUCESSO: {data_completa}")

# DESCREVER O TAMANHO DE CADA COLUNA
#df_merged.describe()
#missingno.bar(df_merged)

# %%
#missingno.matrix(df_merged)
