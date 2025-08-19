# -*- coding: utf-8 -*-
# Autor: Ricardo Lazzarini
# Data: 2025-02-10
# Descrição: Programa para calcular o total de horas trabalhadas por semana e por mês
#            a partir de um arquivo CSV com as colunas Checkin, Tempo Apresentacao, TJS, TJSD, TJSN, TJSE e TJSEN
#            e gerar um EXTRATO em um arquivo texto chamado 'rel_horas_tempo_Tempo Apresentacão de trabalho.txt'
# UTILIZA O ARQUIVO Tempo Apresentacão

#import subprocess
#subprocess.check_call(["pip", "install", "fpdf"])


from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
# from fpdf import FPDF  # Comentado - descomente se precisar gerar PDF
import pandas as pd
import re 
import tkinter as tk
import datetime as dt
import warnings
import logging
import os
import json  # Adicionar esta importação no topo do arquivo

warnings.filterwarnings("ignore")

# ocultar os warnings
pd.options.mode.chained_assignment = None

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
    arquivo_path = filedialog.askopenfilename(
        initialdir=diretorio, 
        title="Selecione o arquivo - _QUARTA_VERSAO.csv"
    )
    if not arquivo_path:
        print("Nenhum arquivo selecionado.")
        exit()

    # Extrair nome do arquivo
    nome_arquivo = os.path.basename(arquivo_path)

    print(f"Diretório selecionado: {diretorio}")
    print(f"Arquivo original: {nome_arquivo}")

    # Carregar arquivo JSON - CORRIGIDO
    arquivo_JSON_path = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\feriados.json"
    
    if os.path.exists(arquivo_JSON_path):
        try:
            with open(arquivo_JSON_path, 'r', encoding='utf-8') as json_file:
                dados_json = json.load(json_file)  # CORREÇÃO: usar json.load() ao invés de json_path.load()
                print(f"✅ Arquivo JSON carregado com sucesso: {arquivo_JSON_path}")
                print(f"📊 Total de feriados carregados: {len(dados_json) if isinstance(dados_json, list) else 'N/A'}")
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao ler arquivo JSON: {e}")
            dados_json = []
        except Exception as e:
            print(f"❌ Erro inesperado ao carregar JSON: {e}")
            dados_json = []
    else:
        print(f"⚠️ Arquivo JSON não encontrado: {arquivo_JSON_path}")
        dados_json = []

    return diretorio, nome_arquivo, arquivo_path

######################################

def gravar_arquivo(nome_arquivo, diretorio):
    # 3. Substituir tudo após ')' no nome do arquivo por "novo nome"
    novo_nome = nome_arquivo.split(")")[0] + ") - RELATORIO_HORAS_APRESENTACAO.txt"

# Chamar a função selecionar_arquivo e armazenar os retornos
diretorio, nome_arquivo, arquivo_path = selecionar_arquivo()

nome_arquivo = diretorio + '/' + nome_arquivo 

# Ler o arquivo  CSV, o arquivo é o 
dados_iniciais = pd.read_csv(nome_arquivo, sep=',', encoding='utf-8', parse_dates=['Checkin', 'Checkout'], dayfirst=True)

# FILTRAR O DATAFRAME dados_iniciais PARA MANTER LINHAS ONDE A COLUNA 'Activity' inicie com 'AD' ou 'S' ou 'R' ou 'GS' ou 'BUS'
dados = dados_iniciais[dados_iniciais['Activity'].str.startswith(('AD', 'APT','SFX', 'S02', 'S06', 'S10', 'S14', 'S18', 'S22', 'CPT'))] 

# reindexar o dataframe
dados = dados.reset_index(drop=True)

# filtrar o dataframe para excluir as linhas onde a coluna Tempo Apresentacao é nula ou igual a '-' 
#dados = dados[dados['Tempo Apresentacao'].notnull() & dados['Tempo Apresentacao'] != '' ]

##### TÉRMINO DA ABERTURA DOS ARQUIVOS

# CONVERTER AS COLUNAS Tempo Apresentacao, Tempo Apresentacao Diurno, Tempo Apresentacao Noturno, Tempo Apresentacao Especial Diurno, Tempo Apresentacao Especial Noturno,  PARA timedelta
dados['Tempo Apresentacao'] = pd.to_timedelta(dados['Tempo Apresentacao'])
dados['Tempo Apresentacao Diurno'] = pd.to_timedelta(dados['Tempo Apresentacao Diurno'])
dados['Tempo Apresentacao Noturno'] = pd.to_timedelta(dados['Tempo Apresentacao Noturno'])
dados['Tempo Apresentacao Especial Diurno'] = pd.to_timedelta(dados['Tempo Apresentacao Especial Diurno'])
dados['Tempo Apresentacao Especial Noturn'] = pd.to_timedelta(dados['Tempo Apresentacao Especial Noturno'])

# Extrair o nome do aeronauta - CORRIGIDO CONFORME ESPECIFICAÇÃO
file_path = arquivo_path
print(f"Caminho do arquivo: {file_path}")

# Extrair nome conforme padrão especificado
base_name = os.path.basename(file_path)
print(f"Nome do arquivo: {base_name}")

# Dividir por underscores para extrair partes específicas
partes = base_name.split('_')
print(f"Partes divididas: {partes}")

# Verificar se temos partes suficientes para extrair o padrão desejado
if len(partes) >= 6:
    nome_extraido = '_'.join(partes[2:6])  # Índices 2, 3, 4, 5
    extracted_text = nome_extraido
    print(f"✅ Nome extraído com sucesso: {extracted_text}")
else:
    # Fallback - tentar extrair pelo menos o nome
    if len(partes) >= 3:
        extracted_text = '_'.join(partes[2:4])  # Pelo menos nome_sobrenome
    else:
        extracted_text = "aeronauta"
    print(f"⚠️ Padrão não encontrado, usando fallback: {extracted_text}")

print(f"Nome final do aeronauta: {extracted_text}")

# Função para limpar e corrigir valores da coluna 'Tempo Apresentacao'
def corrigir_Tempo_Apresentação(valor):
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
    colunas_tempo = ['Tempo Apresentacao', 'Tempo Apresentacao Diurno', 'Tempo Apresentacao Noturno', 'Tempo Apresentacao Especial Diurno', 'Tempo Apresentacao Especial Noturno']
    
    # Verificar e converter colunas de tempo para timedelta
    for coluna in colunas_tempo:
        df[coluna] = pd.to_timedelta(df[coluna], errors='coerce')
    
    # Adicionar coluna de semana
    df['Semana'] = df['Checkin'].dt.to_period('W-SUN')
    
    # Agrupar por semana e somar as colunas de tempo
    total_semana = df.groupby('Semana')[colunas_tempo].sum()
    
    return total_semana

# Função para totalizar horas por semana
def totalizar_por_mes(dados):
    df = pd.DataFrame(dados)
    df['Checkin'] = pd.to_datetime(df['Checkin'])
    
    # Lista das colunas de tempo
    colunas_tempo = ['Tempo Apresentacao', 'Tempo Apresentacao Diurno', 'Tempo Apresentacao Noturno', 'Tempo Apresentacao Especial Diurno', 'Tempo Apresentacao Especial Noturno']
    
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

# CRIAR NOME DO ARQUIVO CONFORME ESPECIFICAÇÃO
nome_arquivo_saida = f"{extracted_text}_relatorio_apresentacao.txt"

# Garantir que o caminho não seja muito longo
novo_nome = os.path.join(diretorio, nome_arquivo_saida)

# Se o caminho ainda for muito longo, usar nome mais curto
if len(novo_nome) > 250:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo_saida = f"relatorio_apresentacao_{timestamp}.txt"
    novo_nome = os.path.join(diretorio, nome_arquivo_saida)

print(f"Gerando EXTRATO em: {novo_nome}")

# Verificar permissões do diretório
try:
    # Testar se consegue escrever no diretório
    test_file = os.path.join(diretorio, "test_write.tmp")
    with open(test_file, 'w') as f:
        f.write("test")
    os.remove(test_file)
    print("✅ Permissões de escrita verificadas")
except Exception as e:
    print(f"❌ Erro de permissão: {e}")
    # Usar diretório alternativo
    import tempfile
    diretorio = tempfile.gettempdir()
    novo_nome = os.path.join(diretorio, nome_arquivo_saida)
    print(f"📁 Usando diretório alternativo: {novo_nome}")

# iniciar a barra de progresso
total_linhas = len(dados)
print("Processando dados...")
for i in range(total_linhas):
    print(gerar_barra_progresso(i + 1, total_linhas), end='\r')

print("\n✅ Dados processados com sucesso!")

try:
    with open(novo_nome, 'w', encoding='utf-8') as arquivo:
        # centralizar o título
        titulo = 'EXTRATO DE HORAS ENTRE APRESENTAÇÃO E INÍCIO DA OPERAÇÃO'
        largura_total = 120
        titulo_centralizado = titulo.center(largura_total)
        arquivo.write(titulo_centralizado + '\n')
        
        # alinhar a linha abaixo como cabeçalho - AJUSTADO
        arquivo.write('Activity'.ljust(10) + 'Checkin'.ljust(18) + 'Start'.ljust(18) + 'Dep'.ljust(5) + 'Arr'.ljust(5) + 'End'.ljust(18) + 'Checkout'.ljust(18) + 'Tempo Apres'.ljust(12) + '\n')

        arquivo.write(linha_simples + '\n')

        for linha in range(len(dados)):
            # Converter 'Tempo Apresentacao' para o formato HH:MM
            Tempo_Apresentação_timedelta = dados['Tempo Apresentacao'][linha]
            horas, resto = divmod(Tempo_Apresentação_timedelta.total_seconds(), 3600)
            minutos, _ = divmod(resto, 60)
            Tempo_Apresentação_formatada = f"{int(horas):02}:{int(minutos):02}"

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

            # Imprimir os dados com ESPAÇAMENTO AJUSTADO
            arquivo.write(dados['Activity'][linha].ljust(10) + 
                         checkin_formatado.ljust(18) + 
                         start_formatado.ljust(18) + 
                         str(dados['Dep'][linha]).ljust(5) + 
                         str(dados['Arr'][linha]).ljust(5) + 
                         end_formatado.ljust(18) + 
                         checkout_formatado.ljust(18) + 
                         Tempo_Apresentação_formatada.ljust(12) + '\n')

            # imprimir os totais por semana
            if linha < len(dados) - 1:
                if pd.to_datetime(dados['Checkin'][linha]).week != pd.to_datetime(dados['Checkin'][linha + 1]).week:
                    arquivo.write(linha_simples + '\n')

                    # Cálculos dos totais semanais
                    total_semana['Tempo Apresentacao                        = '] = total_semana['Tempo Apresentacao'].dt.components.hours + total_semana['Tempo Apresentacao'].dt.components.days * 24
                    total_semana['Tempo Apresentacao Diurno           = '] = total_semana['Tempo Apresentacao Diurno'].dt.components.hours + total_semana['Tempo Apresentacao Diurno'].dt.components.days * 24
                    total_semana['Tempo Apresentacao Noturno          = '] = total_semana['Tempo Apresentacao Noturno'].dt.components.hours + total_semana['Tempo Apresentacao Noturno'].dt.components.days * 24
                    total_semana['Tempo Apresentacao Especial Diurno  = '] = total_semana['Tempo Apresentacao Especial Diurno'].dt.components.hours + total_semana['Tempo Apresentacao Especial Diurno'].dt.components.days * 24
                    total_semana['Tempo Apresentacao Especial Noturno = '] = total_semana['Tempo Apresentacao Especial Noturno'].dt.components.hours + total_semana['Tempo Apresentacao Especial Noturno'].dt.components.days * 24
                    
                    total_semana['Tempo Apresentacao                        = '] = total_semana['Tempo Apresentacao                        = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apresentacao'].dt.components.minutes.astype(str).str.zfill(2)
                    total_semana['Tempo Apresentacao Diurno           = '] = total_semana['Tempo Apresentacao Diurno           = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apresentacao Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                    total_semana['Tempo Apresentacao Noturno          = '] = total_semana['Tempo Apresentacao Noturno          = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apresentacao Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                    total_semana['Tempo Apresentacao Especial Diurno  = '] = total_semana['Tempo Apresentacao Especial Diurno  = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apresentacao Especial Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                    total_semana['Tempo Apresentacao Especial Noturno = '] = total_semana['Tempo Apresentacao Especial Noturno = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apresentacao Especial Noturno'].dt.components.minutes.astype(str).str.zfill(2)

                    arquivo.write('Total por semana:'.ljust(15) + '\n')
                    
                    periodo_semanal = pd.to_datetime(dados['Checkin'][linha]).to_period('W-SUN')

                    if periodo_semanal in total_semana.index:
                        valores = total_semana.loc[periodo_semanal, ['Tempo Apresentacao                        = ', 'Tempo Apresentacao Diurno           = ', 'Tempo Apresentacao Noturno          = ', 'Tempo Apresentacao Especial Diurno  = ', 'Tempo Apresentacao Especial Noturno = ']]
                        
                        for coluna in valores.index:
                            valor_str = f"{coluna.ljust(45)}: {valores[coluna]}"
                            arquivo.write(valor_str.ljust(105) + '\n')
                    else:
                        print(f"Período semanal {periodo_semanal} não encontrado no índice de 'total_semana'.")
                    
                    arquivo.write(linha_dupla + '\f')

                    # Novo cabeçalho com espaçamento ajustado
                    titulo = 'EXTRATO DE HORAS ENTRE APRESENTAÇÃO E INÍCIO DA OPERAÇÃO'
                    titulo_centralizado = titulo.center(120)
                    arquivo.write(titulo_centralizado + '\n')
                    arquivo.write('Activity'.ljust(10) + 'Checkin'.ljust(18) + 'Start'.ljust(18) + 'Dep'.ljust(5) + 'Arr'.ljust(5) + 'End'.ljust(18) + 'Checkout'.ljust(18) + 'Tempo Apres'.ljust(12) + '\n')
                    arquivo.write(linha_simples + '\n')
            else:
                # Último total semanal
                semana_atual = pd.to_datetime(dados['Checkin'][linha]).to_period('W-SUN')
                if semana_atual in total_semana.index:
                    arquivo.write(linha_simples + '\n')
                    arquivo.write('Total por semana:'.ljust(25) + '\n')
                    
                    valores = total_semana.loc[semana_atual, ['Tempo Apresentacao', 'Tempo Apresentacao Diurno', 'Tempo Apresentacao Noturno', 'Tempo Apresentacao Especial Diurno', 'Tempo Apresentacao Especial Noturno']]
                    
                    for coluna in valores.index:
                        horas, resto = divmod(valores[coluna].total_seconds(), 3600)
                        minutos, _ = divmod(resto, 60)
                        valor_str = f"{int(horas):02}:{int(minutos):02}"
                        linha_formatada = f"{coluna.ljust(50)} = : {valor_str.rjust(7)}"
                        arquivo.write(linha_formatada + '\n')
                else:
                    print(f"Período semanal {semana_atual} não encontrado no índice de 'total_semana'.")
        
        arquivo.write(linha_dupla + '\f')

        # Seção mensal com espaçamento ajustado
        titulo = 'EXTRATO TOTAL DE HORAS TEMPO DE TRABALHO'
        titulo_centralizado = titulo.center(120)
        arquivo.write(titulo_centralizado + '\n')
        arquivo.write('Activity'.ljust(10) + 'Checkin'.ljust(18) + 'Start'.ljust(18) + 'Dep'.ljust(5) + 'Arr'.ljust(5) + 'End'.ljust(18) + 'Checkout'.ljust(18) + 'Tempo Apres'.ljust(12) + '\n')
        arquivo.write(linha_simples + '\n')

        for linha in range(len(dados)):
            # Repetir formatação para seção mensal
            Tempo_Apresentação_timedelta = dados['Tempo Apresentacao'][linha]
            horas, resto = divmod(Tempo_Apresentação_timedelta.total_seconds(), 3600)
            minutos, _ = divmod(resto, 60)
            Tempo_Apresentação_formatada = f"{int(horas):02}:{int(minutos):02}"

            # Formatar datas com hora
            checkin_formatado = pd.to_datetime(dados['Checkin'][linha]).strftime('%d/%m/%Y %H:%M')
            start_formatado = pd.to_datetime(dados['Start'][linha]).strftime('%d/%m/%Y %H:%M') if pd.notna(dados['Start'][linha]) else ''
            end_formatado = pd.to_datetime(dados['End'][linha]).strftime('%d/%m/%Y %H:%M') if pd.notna(dados['End'][linha]) else ''
            checkout_formatado = pd.to_datetime(dados['Checkout'][linha]).strftime('%d/%m/%Y %H:%M')

            # ESPAÇAMENTO AJUSTADO para seção mensal
            arquivo.write(dados['Activity'][linha].ljust(10) + 
                         checkin_formatado.ljust(18) + 
                         start_formatado.ljust(18) + 
                         str(dados['Dep'][linha]).ljust(5) + 
                         str(dados['Arr'][linha]).ljust(5) + 
                         end_formatado.ljust(18) + 
                         checkout_formatado.ljust(18) + 
                         Tempo_Apresentação_formatada.ljust(12) + '\n')

            if linha < len(dados) - 1:
                if pd.to_datetime(dados['Checkin'][linha]).month != pd.to_datetime(dados['Checkin'][linha + 1]).month:
                    arquivo.write(linha_simples + '\n')
              
                    # Cálculos mensais
                    total_mes['Tempo Apresentacao                  = '] = total_mes['Tempo Apresentacao'].dt.components.hours + total_mes['Tempo Apresentacao'].dt.components.days * 24
                    total_mes['Tempo Apresentacao Diurno           = '] = total_mes['Tempo Apresentacao Diurno'].dt.components.hours + total_mes['Tempo Apresentacao Diurno'].dt.components.days * 24
                    total_mes['Tempo Apresentacao Noturno          = '] = total_mes['Tempo Apresentacao Noturno'].dt.components.hours + total_mes['Tempo Apresentacao Noturno'].dt.components.days * 24
                    total_mes['Tempo Apresentacao Especial Diurno  = '] = total_mes['Tempo Apresentacao Especial Diurno'].dt.components.hours + total_mes['Tempo Apresentacao Especial Diurno'].dt.components.days * 24
                    total_mes['Tempo Apresentacao Especial Noturno = '] = total_mes['Tempo Apresentacao Especial Noturno'].dt.components.hours + total_mes['Tempo Apresentacao Especial Noturno'].dt.components.days * 24
                    
                    total_mes['Tempo Apresentacao                  = '] = total_mes['Tempo Apresentacao                  = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apresentacao'].dt.components.minutes.astype(str).str.zfill(2)
                    total_mes['Tempo Apresentacao Diurno           = '] = total_mes['Tempo Apresentacao Diurno           = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apresentacao Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                    total_mes['Tempo Apresentacao Noturno          = '] = total_mes['Tempo Apresentacao Noturno          = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apresentacao Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                    total_mes['Tempo Apresentacao Especial Diurno  = '] = total_mes['Tempo Apresentacao Especial Diurno  = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apresentacao Especial Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                    total_mes['Tempo Apresentacao Especial Noturno = '] = total_mes['Tempo Apresentacao Especial Noturno = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apresentacao Especial Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                     
                    arquivo.write('Total por mes:'.ljust(15) + '\n')
                    
                    periodo_mensal = pd.to_datetime(dados['Checkin'][linha]).to_period('M')
                    
                    if periodo_mensal in total_mes.index: 
                        valores = total_mes.loc[periodo_mensal, ['Tempo Apresentacao                  = ', 'Tempo Apresentacao Diurno           = ', 'Tempo Apresentacao Noturno          = ', 'Tempo Apresentacao Especial Diurno  = ', 'Tempo Apresentacao Especial Noturno = ']]

                        for coluna in valores.index:
                            valor_str = f"{coluna.ljust(45)}: {valores[coluna]}"
                            arquivo.write(valor_str.ljust(105) + '\n')
                    else:
                        print(f"Período mensal {periodo_mensal} não encontrado no índice de 'total_mes'.")

                    arquivo.write(linha_dupla + '\f')

                    titulo = 'EXTRATO DE HORAS ENTRE APRESENTAÇÃO E INÍCIO DA OPERAÇÃO'
                    titulo_centralizado = titulo.center(120)
                    arquivo.write(titulo_centralizado + '\n')
                    arquivo.write('Activity'.ljust(10) + 'Checkin'.ljust(18) + 'Start'.ljust(18) + 'Dep'.ljust(5) + 'Arr'.ljust(5) + 'End'.ljust(18) + 'Checkout'.ljust(18) + 'Tempo Apres'.ljust(12) + '\n')
                    arquivo.write(linha_simples + '\n')
        arquivo.write(linha_simples + '\n')
        arquivo.write('Total por mes:'.ljust(15) + '\n')
        
        periodo_mensal = pd.to_datetime(dados['Checkin'][linha]).to_period('M')
        
        if periodo_mensal in total_mes.index:
            valores = total_mes.loc[periodo_mensal, ['Tempo Apresentacao                  = ', 'Tempo Apresentacao Diurno           = ', 'Tempo Apresentacao Noturno          = ', 'Tempo Apresentacao Especial Diurno  = ', 'Tempo Apresentacao Especial Noturno = ']]
            
            for coluna in valores.index:
                valor_str = f"{coluna.ljust(45)}: {valores[coluna]}"
                arquivo.write(valor_str.ljust(105) + '\n')
        else:
            print(f"Período mensal {periodo_mensal} não encontrado no índice de 'total_mes'.")

    print(f"🎉 EXTRATO de texto salvo como: {novo_nome}")
    print("✅ Processamento concluído!")

except PermissionError as e:
    print(f"❌ Erro de permissão: {e}")
    print("💡 Soluções possíveis:")
    print("1. Execute como administrador")
    print("2. Verifique se o arquivo não está aberto")
    print("3. Escolha um diretório diferente")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    print(f"Tipo do erro: {type(e).__name__}")
finally:
    print("🔄 Processo finalizado.")
