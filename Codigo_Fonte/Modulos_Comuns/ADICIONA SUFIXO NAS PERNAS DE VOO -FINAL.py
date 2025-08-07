#####
# ESTE CÓDIGO ADICIONA SUFIXO NA COLUNA ATIVIDADE PARA ESTABELECER ONDE INICIA A JORNADA E
# ONDE A MESMA TERMINA
# path = path.replace('SEM_COLUNAS_EM_BRANCO.csv' GERA '\_COM_SUFIXO.csv')
####
# AUTOR: RICARDO LAZZARINI
# DATA FINALIZAÇÃO: 27/06/2025
# VERSÃO: 1.0
# VERSÃO DO PYTHON: 3.11.9
# VERSÃO DO PANDAS: 2.1.3
# # IMPORTANTE: O CÓDIGO DEVE SER EXECUTADO NO MESMO DIRETÓRIO ONDE ESTÁ O ARQUIVO CSV   

import pandas as pd
import numpy as np
from datetime import datetime
from tkinter import filedialog, messagebox, Tk
import warnings
from tqdm import tqdm
import os

warnings.filterwarnings("ignore")

# FUNÇÃO PARA DETERMINAR DIRETORIO DE ARQUIVO E NOME DO ARQUIVO A SER UTILIZADO

def selecionar_diretorio():
    root = Tk()
    root.withdraw()  # Oculta a janela principal
    
    messagebox.showinfo("Seleção de Diretório", "Selecione o diretório onde estão os arquivos necessários.")

    path = filedialog.askdirectory()
    return path

def selecionar_arquivo():
    root = Tk()
    root.withdraw()  # Oculta a janela principal

    messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo ricardo_lazzarini_vcp_3394_112017_022023__SEGUNDA_VERSAO.csv")
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
nome_arquivo = nome_arquivo.replace('_SEGUNDA_VERSAO', '_TERCEIRA_VERSAO')

print(f"Nome do arquivo modificado: {nome_arquivo}")

def gravar_arquivo(diretorio_path, nome_arquivo, conteudo):
    if not os.path.exists(diretorio_path):
        os.makedirs(diretorio_path)
    
    caminho_completo = os.path.join(diretorio_path, nome_arquivo)

    escala.to_csv(caminho_completo, index=False)

    print(f"Arquivo gravado com sucesso em: {caminho_completo}")
    return caminho_completo

escala = pd.read_csv(arquivo_path,sep=',')
escala.insert(1, 'Id_Leg', '')

#### TENTATIVA COMO STRINGS
i = 0
while i < len(escala):
    # se for a última linha do dataframe
    if i == (len(escala)-1):
      # se a linha anterior for igual, incluir F
      if escala['Checkin'].iloc[i] == escala['Checkin'].iloc[i-1]:
        #escala['Activity'].iloc[i] = escala['Activity'].iloc[i] + '-F'
        escala['Id_Leg'].iloc[i] = '-F'
        break
      # se a linha anterior for diferente, colocar IF
      else:
        #escala['Activity'].iloc[i] = escala['Activity'].iloc[i] + '-IF'
        escala['Id_Leg'].iloc[i] = '-IF'
        break
    # se a próxima linha for uma data igual à atual
    elif escala['Checkin'].iloc[i] == escala['Checkin'].iloc[i+1]:
      # se a linha anterior é uma data diferente, a linha recebe I
      if escala['Checkin'].iloc[i] != escala['Checkin'].iloc[i-1]:
        #escala['Activity'].iloc[i] = escala['Activity'].iloc[i] + '-I'
        escala['Id_Leg'].iloc[i] = '-I'
        i += 1
      # se a linha anterior é uma data igual, a linha recebe M
      elif escala['Checkin'].iloc[i] == escala['Checkin'].iloc[i-1]:
        #escala['Activity'].iloc[i] = escala['Activity'].iloc[i] + '-M'
        escala['Id_Leg'].iloc[i] = '-M'
        i += 1
    # se for uma linha única
    elif escala['Checkin'].iloc[i] != escala['Checkin'].iloc[i-1] and escala['Checkin'].iloc[i] != escala['Checkin'].iloc[i+1]:
        #escala['Activity'].iloc[i] = escala['Activity'].iloc[i] + '-IF'
        escala['Id_Leg'].iloc[i] = '-IF'
        i += 1
    # se a próxima linha for uma data diferente da atual e se a linha anterior for igual
    elif escala['Checkin'].iloc[i] != escala['Checkin'].iloc[i+1] and escala['Checkin'].iloc[i] == escala['Checkin'].iloc[i-1]:
        #escala['Activity'].iloc[i] = escala['Activity'].iloc[i] + '-F'
        escala['Id_Leg'].iloc[i] = '-F'
        i += 1

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
