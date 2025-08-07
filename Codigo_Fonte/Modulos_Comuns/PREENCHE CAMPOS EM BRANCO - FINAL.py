#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PREENCHE CAMPOS EM BRANCO - Script Auxiliar

Autor: Ricardo Lazzarini
Data de criação: 27 de junho de 2025
Data de verificação: 27 de junho de 2025

Descrição:
Este código preenche os campos de checkin em branco com o valor do checkin anterior, 
para atividades de não voo e reservas.
Lê o CSV gerado _PRIMEIRA_VERSAO e gera um novo _SEM_COLUNAS_EM_BRANCO.csv

Dependências:
- pandas
- numpy
- dateutil
- tkinter
- tqdm
"""

import pandas as pd
from datetime import timedelta, time, datetime, date, tzinfo, timezone
import warnings
warnings.filterwarnings("ignore")

import tkinter as tk
from tkinter import filedialog, messagebox, Tk
from tqdm import tqdm
import time
import threading
import sys
import os

# Inicializa a janela Tkinter (necessária para dialogs)
root = Tk()
root.withdraw()

def spinner():
    """Função para exibir ampulheta/spinner durante processamento"""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    while getattr(spinner, 'running', True):
        for char in chars:
            sys.stdout.write(f'\r{char} Processando...')
            sys.stdout.flush()
            time.sleep(0.1)
            if not getattr(spinner, 'running', True):
                break
    sys.stdout.write('\r' + ' ' * 20 + '\r')  # Limpa a linha
    sys.stdout.flush()


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

    messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo ricardo_lazzarini_vcp_3394_112017_022023_PRIMEIRA_VERSAO.csv")
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
nome_arquivo = nome_arquivo.replace('_PRIMEIRA_VERSAO', '_SEGUNDA_VERSAO')

print(f"Nome do arquivo modificado: {nome_arquivo}")

def gravar_arquivo(diretorio_path, nome_arquivo, conteudo):
    if not os.path.exists(diretorio_path):
        os.makedirs(diretorio_path)
    
    caminho_completo = os.path.join(diretorio_path, nome_arquivo)

    df_merged.to_csv(caminho_completo, index=False)

    print(f"Arquivo gravado com sucesso em: {caminho_completo}")
    return caminho_completo

# Inicia spinner de processamento
spinner.running = True
spinner_thread = threading.Thread(target=spinner)
spinner_thread.start()

df_merged = pd.read_csv(arquivo_path, sep=',')

# Para o spinner
spinner.running = False
spinner_thread.join()

print("✅ Arquivo carregado com sucesso!")
print(f"📈 Total de registros: {len(df_merged)}")

var_temp_checkin = ''
reservas=[]
reservas=[
'RE', 
'RES',
'R0',
'R04',
'R05',
'R06',
'R07',
'R08',
'R09',
'R10',
'R11',
'R12',
'R13',
'R15',
'R16',
'R17',
'R18',
'R19',
'R21',
'R22',
]
##### TODOS OS CHECKIN EM BRANCO TERÃO '-'
print("🔄 Preenchendo campos em branco...")
df_merged['Checkin'].fillna("-", inplace=True)

print("🚌 Processando atividades BUS...")
start_row = 0 
for i in tqdm(range(start_row, len(df_merged)), desc="⏳ Processando BUS"):
    
    ##### AS ATIVIDADES DE NÃO VOO DEVEM TER O MESMO HORÁRIO DE CHECKIN E START
    if df_merged['Activity'].iloc[i][0:3] == 'BUS':
      var_temp_checkin = df_merged['Checkin'].iloc[i]
      #print(var_temp_checkin)
    
      #### SE 'Activity' = 'AD' E 'Checkout' = '-' igualar checkout a end
    
      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

      i = i + 1
      if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
          df_merged['Checkin'].iloc[i] = var_temp_checkin

print("🎫 Processando reservas...")
for i in tqdm(range(len(df_merged)), desc="⏳ Processando reservas"):
    
    if df_merged['Activity'].iloc[i] in reservas:
        var_temp_checkin = df_merged['Checkin'].iloc[i]
        #print(' ENTREI EM RESERVA')    
        
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin
        else:
            continue    
        i = i + 1
        if df_merged['Activity'].iloc[i][0:2] == 'AD' and df_merged['Checkin'].iloc[i] == '-':
            df_merged['Checkin'].iloc[i] = var_temp_checkin

# TODAS AS COLUNAS QUE TIVEREM VALOR 00:00 OU 00:00:00 SERÃO SUBSTITUIDAS POR '-'
print("🕐 Limpando horários zerados...")
df_merged.replace('00:00', '-', inplace=True)
df_merged.replace('00:00:00', '-', inplace=True)

print("🔄 Reorganizando dados...")
df_merged.reset_index(drop=True, inplace=True)

print("💾 Salvando arquivo final...")
path = arquivo_path.replace('_PRIMEIRA_VERSAO.csv', '_SEGUNDA_VERSAO.csv')

# Inicia spinner para salvamento
spinner.running = True
spinner_thread = threading.Thread(target=spinner)
spinner_thread.start()

#df_merged.to_csv(path, index=False)

# Funçã o gravar_arquivo
diretorio_path = diretorio_path.replace('Escalas_Executadas', 'Auditoria_Calculos')

# chamar a função gravar_arquivo
conteudo_exemplo = "Este é um exemplo de conteúdo para o arquivo."
caminho_arquivo_gravado = gravar_arquivo(diretorio_path, nome_arquivo, conteudo_exemplo)

##################################################################

data_completa = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# imprimir TAREFA CONCLUÍDA e data completa do sistema
print(f"TAREFA CONCLUIDA COM SUCESSO: {data_completa}")

# Para o spinner
spinner.running = False
spinner_thread.join()

print(f"📂 Arquivo salvo em: {path}")
print(f"📊 Total de registros processados: {len(df_merged)}")