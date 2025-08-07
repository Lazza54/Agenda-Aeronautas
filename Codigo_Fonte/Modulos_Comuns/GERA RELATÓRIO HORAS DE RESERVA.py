# Autor: Ricardo Lazzarini
# Data: 2025-06-27
# Descrição: Programa para calcular o total de horas trabalhadas por semana e por mês
#            a partir de um arquivo CSV com as colunas Checkin, 
# #            e gerar um relatório em um arquivo texto chamado 'rel_horas_tempo_de_repouso_extra.txt'
# UTILIZA O ARQUIVO 

from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
                          
import pandas as pd
import datetime as dt
import tkinter as tk

import os
import re
import warnings
import logging

warnings.filterwarnings("ignore")

# ocultar os warnings
pd.options.mode.chained_assignment = None

# produzir um popup informando o nome do arquivo a se selecionar
root = tk.Tk()
root.withdraw()

# Trazer a janela para o topo e focar
root.lift()
root.focus_force()

######################################

def selecionar_arquivo():
    # 1. Selecionar diretório e armazenar na variável
    diretorio = filedialog.askdirectory(title="Selecione o diretório")
    if not diretorio:
        print("Nenhum diretório selecionado.")
        exit()

    # 2. Selecionar arquivo no diretório escolhido
    arquivo_path = filedialog.askopenfilename(initialdir=diretorio, title="Selecione o arquivo - _CALCULOS_EM_TIMEDELTA_com_tempos.csv")
    if not arquivo_path:
        print("Nenhum arquivo selecionado.")
        exit()

    # Extrair nome do arquivo
    nome_arquivo = os.path.basename(arquivo_path)
    
    return diretorio, nome_arquivo

######################################

def gravar_arquivo(nome_arquivo, diretorio):
    # 3. Substituir tudo após ')' no nome do arquivo por "novo nome"
    novo_nome = nome_arquivo.split(")")[0] + ") - CALCULOS_EM_TIMEDELTA_COM_TEMPOS_CALCULADOS" #+ os.path.splitext(nome_arquivo)[1]

    # Exibir resultados
    #print(f"Diretório selecionado: {diretorio}")
    #print(f"Arquivo original: {nome_arquivo}")
    #print(f"Novo nome do arquivo: {novo_nome}")

#######################################

# Chamar a função selecionar_arquivo e armazenar os retornos
diretorio, nome_arquivo = selecionar_arquivo()

nome_arquivo = diretorio + '/' + nome_arquivo 
# Ler o arquivo  CSV, o arquivo que é o COM TODOS OS CÁLCULOS 
dados_iniciais = pd.read_csv(nome_arquivo, sep=',', encoding='utf-8', parse_dates=['Checkin', 'Checkout'], dayfirst=True)

##### CRIAR LISTA DE ATIVIDADES VOOS
lista_voos=['AD']

##### GERAR ARQUIVO COM ATIVIDADES PAGAS
# Carregar o arquivo Excel
atividades_pagas = r'G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS\Siglas Sabre 1.xlsx'

df_atividades_pagas = pd.read_excel(atividades_pagas)

# EXCLUIR COLUNAS QUE CONTENHAM APENAS VALORES NULOS
df_atividades_pagas = df_atividades_pagas.dropna(axis=1, how='all')

# REINDEXAR O ARQUIVO df
df_atividades_pagas = df_atividades_pagas.reset_index(drop=True)

# Filtrar onde a coluna 'PGTO' contém o valor 'S'
DF_ATIVIDADESPAGAS = df_atividades_pagas[df_atividades_pagas['PGTO'] == 'S']

# Exibir o dataframe resultante todas as linhas
# HABILITAR A IMPRESSÃO DE TODAS AS LINHAS
pd.set_option('display.max_rows', None)

# Filtrar onde 'Activity' está em ATIVIDADESPAGAS ou começa com 'AD'
dados_filtrados = dados_iniciais[
    (dados_iniciais['Activity'].isin(DF_ATIVIDADESPAGAS['SIGLA'])) |
    (dados_iniciais['Activity'].str.startswith('AD'))
]

# Filtrar onde 'Activity' inicia com 'R'
dados_filtrados = dados_filtrados[dados_filtrados['Activity'].str.startswith('R')]

# CRIAR O DATAFRAME dados A PARTIR DO DATAFRAME dados_iniciais
dados = dados_filtrados.copy()

# reindexar o dataframe
dados = dados.reset_index(drop=True)

# Filtrar o DataFrame para excluir as linhas onde a coluna 'Tempos Reservas' é nula, vazia ou igual a '-'
dados = dados[(dados['Tempo Reserva Diurno'].notnull()) & (dados['Tempo Reserva Diurno'] != '') & (dados['Tempo Reserva Diurno'] != '-')]
dados = dados[(dados['Tempo Reserva Noturno'].notnull()) & (dados['Tempo Reserva Noturno'] != '') & (dados['Tempo Reserva Noturno'] != '-')]
dados = dados[(dados['Tempo Reserva Especial Diurno'].notnull()) & (dados['Tempo Reserva Especial Diurno'] != '') & (dados['Tempo Reserva Especial Diurno'] != '-')]
dados = dados[(dados['Tempo Reserva Especial Noturno'].notnull()) & (dados['Tempo Reserva Especial Noturno'] != '') & (dados['Tempo Reserva Especial Noturno'] != '-')]

# CONVERTER AS COLUNAS Repouso, TJS, TJSD, TJSN, TJSE e TJSEN PARA timedelta
#dados['Tempo Reserva '] = pd.to_timedelta(dados['Tempo Reserva '])
dados['Tempo Reserva Diurno'] = pd.to_timedelta(dados['Tempo Reserva Diurno'])
dados['Tempo Reserva Noturno'] = pd.to_timedelta(dados['Tempo Reserva Noturno'])
dados['Tempo Reserva Especial Diurno'] = pd.to_timedelta(dados['Tempo Reserva Especial Diurno'])
dados['Tempo Reserva Especial Noturno'] = pd.to_timedelta(dados['Tempo Reserva Especial Noturno'])

# Extrair o nome do aeronauta
file_path = diretorio
match = re.search(r'-\s*(.*?)\s*\(', file_path)
extracted_text = match.group(1) if match else "Texto não encontrado"

# Função para limpar e corrigir valores da coluna 'Tempo Reserva '
def corrigir_repouso(valor):
    try:
        # Remover espaços em branco extras
        valor = valor.strip()
        # Verificar se o valor é um número negativo com sinal no início
        if re.match(r'^-?\d+:\d+:\d+$', valor):
            return valor
        else:
            # Tentar converter para timedelta
            return str(pd.to_timedelta(valor))
    except Exception as e:
        print(f"Erro ao corrigir valor: {valor} - {e}")
        return pd.NaT

#####
# Função para totalizar horas por semana
def totalizar_por_semana(dados):
    df = pd.DataFrame(dados)
    df['Checkin'] = pd.to_datetime(df['Checkin'])
    
    # Lista das colunas de tempo
    colunas_tempo = ['Tempo Reserva Diurno', 'Tempo Reserva Noturno', 'Tempo Reserva Especial Diurno', 'Tempo Reserva Especial Noturno']
    
    # Verificar e converter colunas de tempo para timedelta
    for coluna in colunas_tempo:
        df[coluna] = pd.to_timedelta(df[coluna], errors='coerce')
    
    # Adicionar coluna de semana
    df['Semana'] = df['Checkin'].dt.to_period('W-SUN')
    
    # Agrupar por semana e somar as colunas de tempo
    total_semana = df.groupby('Semana')[colunas_tempo].sum()

    #print(total_semana)
    
    return total_semana

# Função para totalizar horas por semana
def totalizar_por_mes(dados):
    df = pd.DataFrame(dados)
    df['Checkin'] = pd.to_datetime(df['Checkin'])
    
    # Lista das colunas de tempo
    #colunas_tempo = ['Tempo Reserva ', 'Tempo Reserva Diurno', 'Tempo Reserva Noturno', 'Tempo Reserva Especial Diurno', 'Tempo Reserva Especial Noturno']

    colunas_tempo = ['Tempo Reserva Diurno', 'Tempo Reserva Noturno', 'Tempo Reserva Especial Diurno', 'Tempo Reserva Especial Noturno']    
    
    # Verificar e converter colunas de tempo para timedelta
    for coluna in colunas_tempo:
        df[coluna] = pd.to_timedelta(df[coluna], errors='coerce')
    
    # Adicionar coluna de semana
    df['Mes'] = df['Checkin'].dt.to_period('M')
    
    # Agrupar por semana e somar as colunas de tempo
    total_mes = df.groupby('Mes')[colunas_tempo].sum()
    
    return total_mes

# Calcular total de horas por semana 
total_semana = totalizar_por_semana(dados)

# Calcular total de horas por mês
total_mes = totalizar_por_mes(dados)

# Função para converter tempo para minutos
def converter_tempo_para_minutos(tempo):
    if not tempo or pd.isna(tempo) or tempo.lower() == 'nan':
        return 0
    try:
        partes = list(map(float, tempo.split(':')))
        if len(partes) == 3:
            horas, minutos, segundos = partes
            minutos += segundos / 60
        elif len(partes) == 2:
            horas, minutos = partes
        else:
            return 0
        return int(horas * 60 + minutos)
    except ValueError:
        return 0
    
##############################################################################################################################
# GERAR BARRA DE PROGRESSO PARA INDICAR O ANDAMENTO DO PROCESSAMENTO DO CÓDIGO

# Função para gerar barra de progresso
def gerar_barra_progresso(atual, total, tamanho=50):
    percentual = atual / total
    n_barra = int(tamanho * percentual)
    barra = '=' * n_barra + ' ' * (tamanho - n_barra)
    return f"[{barra}] {int(percentual * 100)}%"

##############################################################################################################################

linha_simples = '-'*120    
linha_dupla = '=' *120
    
novo_nome = nome_arquivo.split(")")[0] + ") - REL_HORAS_DE_RESERVA.txt"

with open(novo_nome, 'w') as arquivo:

    # centralizar o título
    titulo = 'RELATORIO TOTAL DE HORAS DE RESERVA' 
    largura_total = 120
    titulo_centralizado = titulo.center(largura_total)
    arquivo.write(titulo_centralizado + '\n')
    
    # alinhar a linha abaixo como cabeçalho
    arquivo.write('Activity'.ljust(15) + 'Checkin'.ljust(21) + 'Start'.ljust(14) + 'Dep'.ljust(5) + 'Arr'.ljust(12) + 'End'.ljust(20) + 'Checkout'.ljust(15) +  '\n') #'Tempo Reserva '.ljust(15) + '\n')

    arquivo.write(linha_simples + '\n')

    for linha in range(len(dados)):

        #  imprimir os dados da linha atual com as seguintes colunas 'activity' 'checkin' 'start' 'dep' 'arr' 'end' 'checkout' 'repouso, antes de pular para a próxima semana ou mês imprimir os totais

        # Converter 'Tempo Reserva ' para o formato HH:MM
        reserva_timedelta = dados['Tempo Reserva Diurno'][linha]
        horas, resto = divmod(reserva_timedelta.total_seconds(), 3600)
        minutos, _ = divmod(resto, 60)
        reserva_formatada = f"{int(horas):02}:{int(minutos):02}"

        # Formatar todas as datas no formato dd/mm/yyyy HH:MM
        try:
            checkin_formatado = pd.to_datetime(dados['Checkin'][linha]).strftime('%d/%m/%Y %H:%M')
            start_formatado = pd.to_datetime(dados['Start'][linha]).strftime('%d/%m/%Y %H:%M') if pd.notna(dados['Start'][linha]) else ''
            end_formatado = pd.to_datetime(dados['End'][linha]).strftime('%d/%m/%Y %H:%M') if pd.notna(dados['End'][linha]) else ''
            checkout_formatado = pd.to_datetime(dados['Checkout'][linha]).strftime('%d/%m/%Y %H:%M')
        except Exception as e:
            print(f"Erro ao formatar data na linha {linha}: {e}")
            checkin_formatado = str(dados['Checkin'][linha])[:16]
            start_formatado = str(dados['Start'][linha])[:16] if pd.notna(dados['Start'][linha]) else ''
            end_formatado = str(dados['End'][linha])[:16] if pd.notna(dados['End'][linha]) else ''
            checkout_formatado = str(dados['Checkout'][linha])[:16]

        # Imprimir os dados da linha atual com as colunas 'Activity', 'Checkin', 'Start', 'Dep', 'Arr', 'End', 'Checkout' e 'Tempo Apos Corte' formatada
        arquivo.write(dados['Activity'][linha].ljust(8) + 
                      checkin_formatado.ljust(21) + 
                      start_formatado.ljust(21) + 
                      str(dados['Dep'][linha]).ljust(5) + 
                      str(dados['Arr'][linha]).ljust(5) + 
                      end_formatado.ljust(21) +
                      checkout_formatado.ljust(21) + 
                      reserva_formatada.ljust(15) + '\n')
             
        # imprimir os totais por semana
        if linha < len(dados) - 1:

            if pd.to_datetime(dados['Checkin'][linha]).week != pd.to_datetime(dados['Checkin'][linha + 1]).week:

                # modelo de codigo para impressão de 80 pontinhos 

                arquivo.write(linha_simples + '\n')

                ########################################################################################################################
                #converter todas as de total_semana para timedelta
                # Extrair apenas as horas e minutos para todas as colunas de total_semana

                ### TENTATIVA DE ALTERAR repouso_hhmm PARA Repouso = 
                #total_semana['Repouso                        = '] = total_semana['Tempo Reserva '].dt.components.hours + total_semana['Tempo Reserva '].dt.components.days * 24
                
                total_semana['Tempo Reserva Diurno           = '] = total_semana['Tempo Reserva Diurno'].dt.components.hours + total_semana['Tempo Reserva Diurno'].dt.components.days * 24
                total_semana['Tempo Reserva Noturno          = '] = total_semana['Tempo Reserva Noturno'].dt.components.hours + total_semana['Tempo Reserva Noturno'].dt.components.days * 24
                total_semana['Tempo Reserva Especial Diurno  = '] = total_semana['Tempo Reserva Especial Diurno'].dt.components.hours + total_semana['Tempo Reserva Especial Diurno'].dt.components.days * 24
                total_semana['Tempo Reserva Especial Noturno = '] = total_semana['Tempo Reserva Especial Noturno'].dt.components.hours + total_semana['Tempo Reserva Especial Noturno'].dt.components.days * 24
                
                ###

                #total_semana['Repouso                        = '] = total_semana['Repouso                        = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Reserva '].dt.components.minutes.astype(str).str.zfill(2)
                
                total_semana['Tempo Reserva Diurno           = '] = total_semana['Tempo Reserva Diurno           = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Reserva Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                total_semana['Tempo Reserva Noturno          = '] = total_semana['Tempo Reserva Noturno          = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Reserva Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                total_semana['Tempo Reserva Especial Diurno  = '] = total_semana['Tempo Reserva Especial Diurno  = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Reserva Especial Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                total_semana['Tempo Reserva Especial Noturno = '] = total_semana['Tempo Reserva Especial Noturno = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Reserva Especial Noturno'].dt.components.minutes.astype(str).str.zfill(2)

                ##### IMPRIMI O TOTAL DE HORAS POR SEMANA
                ###

                arquivo.write('Total por semana:'.ljust(15) + '\n')
                
                # Converter 'Checkin' para período semanal
                periodo_semanal = pd.to_datetime(dados['Checkin'][linha]).to_period('W-SUN')

                # Verificar se o período semanal está no índice de 'total_semana'
                if periodo_semanal in total_semana.index:
                    # Acessar os valores específicos das colunas desejadas
                    #valores = total_semana.loc[periodo_semanal, ['Repouso                        = ', 'Tempo Reserva Diurno           = ', 'Tempo Reserva Noturno          = ', 'Tempo Reserva Especial Diurno  = ', 'Tempo Reserva Especial Noturno = ']]
                    
                    valores = total_semana.loc[periodo_semanal, ['Tempo Reserva Diurno           = ', 'Tempo Reserva Noturno          = ', 'Tempo Reserva Especial Diurno  = ', 'Tempo Reserva Especial Noturno = ']]                    
                    # Iterar sobre as colunas e escrever cada valor no arquivo
                    for coluna in valores.index:
                        valor_str = f"{coluna.ljust(45)}: {valores[coluna]}"  # Ajuste para garantir espaçamento adequado
                        arquivo.write(valor_str.ljust(105) + '\n')
                else:
                    print(f"Período semanal {periodo_semanal} não encontrado no índice de 'total_semana'.")
                
                arquivo.write(linha_dupla + '\f')

                # centralizar o título
                titulo = 'RELATORIO TOTAL DE HORAS DE RESERVA'
                largura_total = 120
                titulo_centralizado = titulo.center(largura_total)
                arquivo.write(titulo_centralizado + '\n')
                # alinhar a linha abaixo como cabeçalho
                arquivo.write('Activity'.ljust(15) + 'Checkin'.ljust(21) + 'Start'.ljust(14) + 'Dep'.ljust(5) + 'Arr'.ljust(12) + 'End'.ljust(20) + 'Checkout'.ljust(15) + '\n') #'Tempo Reserva '.ljust(21) + '\n')
                
                arquivo.write(linha_simples + '\n')
        else:
            # imprimir o último total por semana

            semana_atual = pd.to_datetime(dados['Checkin'][linha]).to_period('W-SUN') # coloquei agora
            if semana_atual in total_semana.index: # coloquei agora
                arquivo.write(linha_simples + '\n')
                        
                # Iterar sobre as colunas e escrever cada valor no arquivo
                arquivo.write('Total por semana:' .ljust(25) + '\n')
                
                # Acessar os valores específicos das colunas desejadas para a semana atual
                #valores = total_semana.loc[semana_atual, ['Tempo Reserva ', 'Tempo Reserva Diurno', 'Tempo Reserva Noturno', 'Tempo Reserva Especial Diurno', 'Tempo Reserva Especial Noturno']]
                
                valores = total_semana.loc[semana_atual, ['Tempo Reserva Diurno', 'Tempo Reserva Noturno', 'Tempo Reserva Especial Diurno', 'Tempo Reserva Especial Noturno']]
                
                for coluna in valores.index:
                    # Converter Timedelta para string no formato HH:MM
                    horas, resto = divmod(valores[coluna].total_seconds(), 3600)
                    minutos, _ = divmod(resto, 60)
                    valor_str = f"{int(horas):02}:{int(minutos):02}"
                    # Justificar a parte fixa à esquerda e os últimos 7 caracteres à direita
                    linha_formatada = f"{coluna.ljust(50)} = : {valor_str.rjust(7)}"
                    arquivo.write(linha_formatada + '\n')
            else:
                print(f"Período semanal {semana_atual} não encontrado no índice de 'total_semana'.")
    arquivo.write(linha_dupla + '\f')

    # iniciar novo for loop para imprimir os totais por mês
    # centralizar o título
    titulo = 'RELATORIO TOTAL DE HORAS DE RESERVA'
    largura_total = 120
    titulo_centralizado = titulo.center(largura_total)
    arquivo.write(titulo_centralizado + '\n')
    # alinhar a linha abaixo como cabeçalho
    arquivo.write('Activity'.ljust(15) + 'Checkin'.ljust(21) + 'Start'.ljust(14) + 'Dep'.ljust(5) + 'Arr'.ljust(12) + 'End'.ljust(20) + 'Checkout'.ljust(15) + '\n') #'Tempo Reserva '.ljust(15) + '\n')
                
    arquivo.write(linha_simples + '\n')

    for linha in range(len(dados)):
        ##############################
        # Converter 'Tempo Reserva ' para o formato HH:MM
        reserva_timedelta = dados['Tempo Reserva Diurno'][linha]
        horas, resto = divmod(reserva_timedelta.total_seconds(), 3600)
        minutos, _ = divmod(resto, 60)
        reserva_formatada = f"{int(horas):02}:{int(minutos):02}"

        # Formatar todas as datas no formato dd/mm/yyyy HH:MM
        try:
            checkin_formatado = pd.to_datetime(dados['Checkin'][linha]).strftime('%d/%m/%Y %H:%M')
            start_formatado = pd.to_datetime(dados['Start'][linha]).strftime('%d/%m/%Y %H:%M') if pd.notna(dados['Start'][linha]) else ''
            end_formatado = pd.to_datetime(dados['End'][linha]).strftime('%d/%m/%Y %H:%M') if pd.notna(dados['End'][linha]) else ''
            checkout_formatado = pd.to_datetime(dados['Checkout'][linha]).strftime('%d/%m/%Y %H:%M')
        except Exception as e:
            print(f"Erro ao formatar data na linha {linha}: {e}")
            checkin_formatado = str(dados['Checkin'][linha])[:16]
            start_formatado = str(dados['Start'][linha])[:16] if pd.notna(dados['Start'][linha]) else ''
            end_formatado = str(dados['End'][linha])[:16] if pd.notna(dados['End'][linha]) else ''
            checkout_formatado = str(dados['Checkout'][linha])[:16]

        # Imprimir os dados da linha atual com as colunas 'Activity', 'Checkin', 'Start', 'Dep', 'Arr', 'End', 'Checkout' e 'Tempo Apos Corte' formatada
        arquivo.write(dados['Activity'][linha].ljust(8) + 
                      checkin_formatado.ljust(21) + 
                      start_formatado.ljust(21) + 
                      str(dados['Dep'][linha]).ljust(5) + 
                      str(dados['Arr'][linha]).ljust(5) + 
                      end_formatado.ljust(21) +
                      checkout_formatado.ljust(21) + 
                      reserva_formatada.ljust(15) + '\n')

        if linha < len(dados) - 1:
            if pd.to_datetime(dados['Checkin'][linha]).month != pd.to_datetime(dados['Checkin'][linha + 1]).month:

                arquivo.write(linha_simples + '\n')
          
                #converter todas as de total_mes para timedelta
                total_mes['Tempo Reserva Diurno           = '] = total_mes['Tempo Reserva Diurno'].dt.components.hours + total_mes['Tempo Reserva Diurno'].dt.components.days * 24
                total_mes['Tempo Reserva Noturno          = '] = total_mes['Tempo Reserva Noturno'].dt.components.hours + total_mes['Tempo Reserva Noturno'].dt.components.days * 24
                total_mes['Tempo Reserva Especial Diurno  = '] = total_mes['Tempo Reserva Especial Diurno'].dt.components.hours + total_mes['Tempo Reserva Especial Diurno'].dt.components.days * 24
                total_mes['Tempo Reserva Especial Noturno = '] = total_mes['Tempo Reserva Especial Noturno'].dt.components.hours + total_mes['Tempo Reserva Especial Noturno'].dt.components.days * 24
                
                ###
                
                total_mes['Tempo Reserva Diurno           = '] = total_mes['Tempo Reserva Diurno           = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Reserva Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                total_mes['Tempo Reserva Noturno          = '] = total_mes['Tempo Reserva Noturno          = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Reserva Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                total_mes['Tempo Reserva Especial Diurno  = '] = total_mes['Tempo Reserva Especial Diurno  = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Reserva Especial Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                total_mes['Tempo Reserva Especial Noturno = '] = total_mes['Tempo Reserva Especial Noturno = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Reserva Especial Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                 
                arquivo.write('Total por mes:'.ljust(15) + '\n')
                
                # Converter 'Checkin' para período mensal
                periodo_mensal = pd.to_datetime(dados['Checkin'][linha]).to_period('M')
                
                # Verificar se o período mensal está no índice de 'total_mes'
                if periodo_mensal in total_mes.index:
                    # Acessar os valores específicos das colunas desejadas
                    #valores = total_mes.loc[periodo_mensal, ['Repouso                        = ', 'Tempo Reserva Diurno           = ', 'Tempo Reserva Noturno          = ', 'Tempo Reserva Especial Diurno  = ', 'Tempo Reserva Especial Noturno = ']]
                    valores = total_mes.loc[periodo_mensal, ['Tempo Reserva Diurno           = ', 'Tempo Reserva Noturno          = ', 'Tempo Reserva Especial Diurno  = ', 'Tempo Reserva Especial Noturno = ']]
                    
                    # Iterar sobre as colunas e escrever cada valor no arquivo
                    for coluna in valores.index:
                        valor_str = f"{coluna.ljust(45)}: {valores[coluna]}"
                        arquivo.write(valor_str.ljust(105) + '\n')
                else:
                    print(f"Período mensal {periodo_mensal} não encontrado no índice de 'total_mes'.")

                arquivo.write(linha_dupla + '\f')

                # iniciar novo for loop para imprimir os totais por mês
                # centralizar o título
                titulo = 'RELATORIO TOTAL DE HORAS DE RESERVA'
                largura_total = 120
                titulo_centralizado = titulo.center(largura_total)
                arquivo.write(titulo_centralizado + '\n')
                # alinhar a linha abaixo como cabeçalho
                arquivo.write('Activity'.ljust(15) + 'Checkin'.ljust(21) + 'Start'.ljust(14) + 'Dep'.ljust(5) + 'Arr'.ljust(12) + 'End'.ljust(20) + 'Checkout'.ljust(15) + '\n') #'Tempo Reserva '.ljust(15) + '\n')
                arquivo.write(linha_simples + '\n')

    arquivo.write(linha_simples + '\n')
    
    arquivo.write('Total por mes:'.ljust(15) + '\n')
    
    # Converter 'Checkin' para período mensal
    periodo_mensal = pd.to_datetime(dados['Checkin'][linha]).to_period('M')
    
    # Verificar se o período mensal está no índice de 'total_mes'
    if periodo_mensal in total_mes.index:
        # Acessar os valores específicos das colunas desejadas
        #valores = total_mes.loc[periodo_mensal, ['Repouso                        = ', 'Tempo Reserva Diurno           = ', 'Tempo Reserva Noturno          = ', 'Tempo Reserva Especial Diurno  = ', 'Tempo Reserva Especial Noturno = ']]
        
        valores = total_mes.loc[periodo_mensal, ['Tempo Reserva Diurno           = ', 'Tempo Reserva Noturno          = ', 'Tempo Reserva Especial Diurno  = ', 'Tempo Reserva Especial Noturno = ']]

        # Iterar sobre as colunas e escrever cada valor no arquivo
        for coluna in valores.index:
            valor_str = f"{coluna.ljust(45)}: {valores[coluna]}"
            arquivo.write(valor_str.ljust(105) + '\n')
    else:
        print(f"Período mensal {periodo_mensal} não encontrado no índice de 'total_mes'.")
        
# Fechar o arquivo
arquivo.close()

print("Relatório gerado com sucesso!")