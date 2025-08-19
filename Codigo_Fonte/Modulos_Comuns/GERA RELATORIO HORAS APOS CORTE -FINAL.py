# Autor: Ricardo Lazzarini
# Data: 2025-06-27
# Descrição: Programa para calcular o total de horas trabalhadas por semana e por mês
#            a partir de um arquivo CSV com as colunas Checkin, Tempo Apresentacao, TJS, TJSD, TJSN, TJSE e TJSEN
#            e gerar um relatório em um arquivo texto chamado 'rel_horas_tempo_Tempo Apresentacaosdetrabalho.txt'
# UTILIZA O ARQUIVO Tempo ApresentacaoS
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
  
import pandas as pd
import re 
import tkinter as tk
import datetime as dt
import warnings
import logging
import os
import sys
import time

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
    arquivo_path = filedialog.askopenfilename(initialdir=diretorio, title="Selecione o arquivo - _APOS_CORTE.csv")
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

##############################################################################################################################
# BARRA DE PROGRESSO MELHORADA

def exibir_barra_progresso(atual, total, etapa="Processando", largura=50):
    """
    Função para exibir barra de progresso no terminal
    """
    percentual = atual / total if total > 0 else 0
    preenchido = int(largura * percentual)
    barra = '█' * preenchido + '-' * (largura - preenchido)
    
    # Calcular porcentagem
    porcentagem = int(percentual * 100)
    
    # Exibir a barra de progresso
    print(f'\r{etapa}: |{barra}| {porcentagem}% ({atual}/{total})', end='', flush=True)
    
    # Quebrar linha quando completar
    if atual == total:
        print()

def processar_com_progresso(dados, funcao_processamento, etapa_nome):
    """
    Função genérica para processar dados com barra de progresso
    """
    total = len(dados)
    print(f"\n🔄 Iniciando {etapa_nome}...")
    
    resultado = []
    for i, item in enumerate(dados):
        # Processar item
        item_processado = funcao_processamento(item)
        resultado.append(item_processado)
        
        # Atualizar barra de progresso
        exibir_barra_progresso(i + 1, total, etapa_nome)
        
        # Pequena pausa para visualizar melhor (opcional, pode remover em produção)
        if total > 1000:  # Só adiciona pausa para arquivos grandes
            time.sleep(0.001)
    
    print(f"✅ {etapa_nome} concluído!")
    return resultado

##############################################################################################################################

#######################################

print("🚀 Iniciando processamento do relatório...")
print("📁 Selecionando arquivo...")

# Chamar a função selecionar_arquivo e armazenar os retornos
diretorio, nome_arquivo = selecionar_arquivo()

nome_arquivo = diretorio + '/' + nome_arquivo 

print(f"📄 Arquivo selecionado: {os.path.basename(nome_arquivo)}")
print("📊 Carregando dados...")

# Ler o arquivo CSV
dados_iniciais = pd.read_csv(nome_arquivo, sep=',', encoding='utf-8', parse_dates=['Checkin', 'Checkout'], dayfirst=True)

print(f"✅ Dados carregados: {len(dados_iniciais)} registros encontrados")
print("🔍 Filtrando dados...")

# FILTRAR O DATAFRAME dados_iniciais PARA MANTER LINHAS ONDE A COLUNA 'Activity' inicie com 'AD' ou 'S' ou 'R' ou 'GS' ou 'BUS'
dados = dados_iniciais[dados_iniciais['Activity'].str.startswith(('AD', 'S', 'BUS'))]

# reindexar o dataframe
dados = dados.reset_index(drop=True)
# filtrar o dataframe para excluir as linhas onde a coluna Tempo Apresentacao é nula ou igual a '-' 
dados = dados[dados['Tempo Apos Corte'].notnull() & dados['Tempo Apos Corte'] != '']

print(f"✅ Dados filtrados: {len(dados)} registros válidos")
print("⏱️ Convertendo colunas de tempo...")

# CONVERTER AS COLUNAS Tempo Apresentacao, Tempo Apos Corte Diurno, Tempo Apos Corte Noturno, Tempo Apos Corte Especial Diurno, Tempo Apos Corte Especial Noturna,  PARA timedelta
colunas_tempo = ['Tempo Apos Corte', 'Tempo Apos Corte Diurno', 'Tempo Apos Corte Noturno', 'Tempo Apos Corte Especial Diurno', 'Tempo Apos Corte Especial Noturno']

for i, coluna in enumerate(colunas_tempo):
    dados[coluna] = pd.to_timedelta(dados[coluna])
    exibir_barra_progresso(i + 1, len(colunas_tempo), "Convertendo tempos")

print("✅ Conversão de colunas concluída!")

# Função para limpar e corrigir valores da coluna 'Tempo Apos Corte'
def corrigir_Tempo_Apresentacao(valor):
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
    colunas_tempo = ['Tempo Apos Corte', 'Tempo Apos Corte Diurno', 'Tempo Apos Corte Noturno', 'Tempo Apos Corte Especial Diurno', 'Tempo Apos Corte Especial Noturno']
    
    # Verificar e converter colunas de tempo para timedelta
    for coluna in colunas_tempo:
        df[coluna] = pd.to_timedelta(df[coluna], errors='coerce')
    
    # Adicionar coluna de semana
    df['Semana'] = df['Checkin'].dt.to_period('W-SUN')
    
    # Agrupar por semana e somar as colunas de tempo
    total_semana = df.groupby('Semana')[colunas_tempo].sum()

    return total_semana

# Função para totalizar horas por mês
def totalizar_por_mes(dados):
    df = pd.DataFrame(dados)
    df['Checkin'] = pd.to_datetime(df['Checkin'])
    
    # Lista das colunas de tempo
    colunas_tempo = ['Tempo Apos Corte', 'Tempo Apos Corte Diurno', 'Tempo Apos Corte Noturno', 'Tempo Apos Corte Especial Diurno', 'Tempo Apos Corte Especial Noturno']
    
    # Verificar e converter colunas de tempo para timedelta
    for coluna in colunas_tempo:
        df[coluna] = pd.to_timedelta(df[coluna], errors='coerce')
    
    # Adicionar coluna de semana
    df['Mes'] = df['Checkin'].dt.to_period('M')
    
    # Agrupar por semana e somar as colunas de tempo
    total_mes = df.groupby('Mes')[colunas_tempo].sum()
    
    return total_mes

print("📈 Calculando totais por semana...")
# Calcular total de horas por semana
total_semana = totalizar_por_semana(dados)
print(f"✅ Totais semanais calculados: {len(total_semana)} semanas")

print("📅 Calculando totais por mês...")
# Calcular total de horas por mês
total_mes = totalizar_por_mes(dados)
print(f"✅ Totais mensais calculados: {len(total_mes)} meses")

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

linha_simples = '-'*120    
linha_dupla = '=' *120

novo_nome = nome_arquivo.split(")")[0] + ") - REL_HORAS_APOS_CORTE_MOTORES.txt"

print(f"📝 Gerando relatório: {os.path.basename(novo_nome)}")
print("✍️ Escrevendo dados no arquivo...")

with open(novo_nome, 'w', encoding='utf-8') as arquivo:
    # centralizar o título
    titulo = 'EXTRATO TOTAL DE HORAS APOS CORTE DOS MOTORES' 
    largura_total = 120
    titulo_centralizado = titulo.center(largura_total)
    arquivo.write(titulo_centralizado + '\n')
    
    # alinhar a linha abaixo como cabeçalho
    arquivo.write('Activity'.ljust(15) + 'Checkin'.ljust(21) + 'Start'.ljust(14) + 'Dep'.ljust(5) + 'Arr'.ljust(12) + 'End'.ljust(20) + 'Checkout'.ljust(15) + 'Tempo Apos Corte'.ljust(15) + '\n')

    arquivo.write(linha_simples + '\n')

    print("\n🔄 Processando dados por semana...")
    total_linhas = len(dados)

    for linha in range(len(dados)):
        # Atualizar barra de progresso
        if linha % 10 == 0 or linha == total_linhas - 1:  # Atualizar a cada 10 linhas
            exibir_barra_progresso(linha + 1, total_linhas, "Escrevendo dados semanais")

        # Converter 'Tempo Apos Corte' para o formato HH:MM
        Tempo_Apresentacao_timedelta = dados['Tempo Apos Corte'][linha]
        horas, resto = divmod(Tempo_Apresentacao_timedelta.total_seconds(), 3600)
        minutos, _ = divmod(resto, 60)
        Tempo_Apos_Corte_formatada = f"{int(horas):02}:{int(minutos):02}"

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
                      Tempo_Apos_Corte_formatada.ljust(15) + '\n')
             
        # imprimir os totais por semana
        if linha < len(dados) - 1:

            if pd.to_datetime(dados['Checkin'][linha]).week != pd.to_datetime(dados['Checkin'][linha + 1]).week:

                arquivo.write(linha_simples + '\n')

                total_semana['Tempo Apos Corte                          = '] = total_semana['Tempo Apos Corte'].dt.components.hours + total_semana['Tempo Apos Corte'].dt.components.days * 24
                total_semana['Tempo Apos Corte Diurno           = '] = total_semana['Tempo Apos Corte Diurno'].dt.components.hours + total_semana['Tempo Apos Corte Diurno'].dt.components.days * 24
                total_semana['Tempo Apos Corte Noturno          = '] = total_semana['Tempo Apos Corte Noturno'].dt.components.hours + total_semana['Tempo Apos Corte Noturno'].dt.components.days * 24
                total_semana['Tempo Apos Corte Especial Diurno  = '] = total_semana['Tempo Apos Corte Especial Diurno'].dt.components.hours + total_semana['Tempo Apos Corte Especial Diurno'].dt.components.days * 24
                total_semana['Tempo Apos Corte Especial Noturno = '] = total_semana['Tempo Apos Corte Especial Noturno'].dt.components.hours + total_semana['Tempo Apos Corte Especial Noturno'].dt.components.days * 24
                
                total_semana['Tempo Apos Corte                          = '] = total_semana['Tempo Apos Corte                          = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apos Corte'].dt.components.minutes.astype(str).str.zfill(2)
                total_semana['Tempo Apos Corte Diurno           = '] = total_semana['Tempo Apos Corte Diurno           = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apos Corte Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                total_semana['Tempo Apos Corte Noturno          = '] = total_semana['Tempo Apos Corte Noturno          = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apos Corte Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                total_semana['Tempo Apos Corte Especial Diurno  = '] = total_semana['Tempo Apos Corte Especial Diurno  = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apos Corte Especial Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                total_semana['Tempo Apos Corte Especial Noturno = '] = total_semana['Tempo Apos Corte Especial Noturno = '].astype(str).str.zfill(2) + ':' + total_semana['Tempo Apos Corte Especial Noturno'].dt.components.minutes.astype(str).str.zfill(2)

                arquivo.write('Total por semana:'.ljust(15) + '\n')
                
                # Converter 'Checkin' para período semanal
                periodo_semanal = pd.to_datetime(dados['Checkin'][linha]).to_period('W-SUN')

                # Verificar se o período semanal está no índice de 'total_semana'
                if periodo_semanal in total_semana.index:
                    # Acessar os valores específicos das colunas desejadas
                    valores = total_semana.loc[periodo_semanal, ['Tempo Apos Corte                          = ', 'Tempo Apos Corte Diurno           = ', 'Tempo Apos Corte Noturno          = ', 'Tempo Apos Corte Especial Diurno  = ', 'Tempo Apos Corte Especial Noturno = ']]
                    
                    for coluna in valores.index:
                        valor_str = f"{coluna.ljust(50)}: {valores[coluna]}"
                        arquivo.write(valor_str + '\n')
                else:
                    print(f"Período semanal {periodo_semanal} não encontrado no índice de 'total_semana'.")
                
                arquivo.write(linha_dupla + '\f')

                # centralizar o título
                titulo = 'EXTRATO TOTAL DE HORAS APOS CORTE DOS MOTORES '
                largura_total = 120
                titulo_centralizado = titulo.center(largura_total)
                arquivo.write(titulo_centralizado + '\n')
                arquivo.write('Activity'.ljust(15) + 'Checkin'.ljust(21) + 'Start'.ljust(14) + 'Dep'.ljust(5) + 'Arr'.ljust(12) + 'End'.ljust(20) + 'Checkout'.ljust(15) + 'Tempo Apos Corte'.ljust(21) + '\n')
                
                arquivo.write(linha_simples + '\n')
        else:
            # imprimir o último total por semana
            semana_atual = pd.to_datetime(dados['Checkin'][linha]).to_period('W-SUN')
            if semana_atual in total_semana.index:
                arquivo.write(linha_simples + '\n')
                        
                arquivo.write('Total por semana:' .ljust(25) + '\n')
                
                # Acessar os valores específicos das colunas desejadas para a semana atual
                valores = total_semana.loc[semana_atual, ['Tempo Apos Corte', 'Tempo Apos Corte Diurno', 'Tempo Apos Corte Noturno', 'Tempo Apos Corte Especial Diurno', 'Tempo Apos Corte Especial Noturno']]
                
                for coluna in valores.index:
                    # Converter Timedelta para string no formato HH:MM
                    horas, resto = divmod(valores[coluna].total_seconds(), 3600)
                    minutos, _ = divmod(resto, 60)
                    valor_str = f"{int(horas):02}:{int(minutos):02}"
                    linha_formatada = f"{coluna.ljust(50)} = : {valor_str.rjust(7)}"
                    arquivo.write(linha_formatada + '\n')
            else:
                print(f"Período semanal {semana_atual} não encontrado no índice de 'total_semana'.")
    
    arquivo.write(linha_dupla + '\f')

    print("\n🔄 Processando dados por mês...")

    # iniciar novo for loop para imprimir os totais por mês
    titulo = 'EXTRATO TOTAL DE HORAS APOS CORTE DOS MOTORES'
    largura_total = 120
    titulo_centralizado = titulo.center(largura_total)
    arquivo.write(titulo_centralizado + '\n')
    arquivo.write('Activity'.ljust(15) + 'Checkin'.ljust(21) + 'Start'.ljust(14) + 'Dep'.ljust(5) + 'Arr'.ljust(12) + 'End'.ljust(20) + 'Checkout'.ljust(15) + 'Tempo Apos Corte'.ljust(15) + '\n')
                
    arquivo.write(linha_simples + '\n')

    for linha in range(len(dados)):
        # Atualizar barra de progresso
        if linha % 10 == 0 or linha == total_linhas - 1:  # Atualizar a cada 10 linhas
            exibir_barra_progresso(linha + 1, total_linhas, "Escrevendo dados mensais")

        # Converter 'Tempo Apos Corte' para o formato HH:MM
        Tempo_Apresentacao_timedelta = dados['Tempo Apos Corte'][linha]
        horas, resto = divmod(Tempo_Apresentacao_timedelta.total_seconds(), 3600)
        minutos, _ = divmod(resto, 60)
        Tempo_Apos_Corte_formatada = f"{int(horas):02}:{int(minutos):02}"

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
                      Tempo_Apos_Corte_formatada.ljust(15) + '\n')

        if linha < len(dados) - 1:
            if pd.to_datetime(dados['Checkin'][linha]).month != pd.to_datetime(dados['Checkin'][linha + 1]).month:

                arquivo.write(linha_simples + '\n')
          
                total_mes['Tempo Apos Corte                          = '] = total_mes['Tempo Apos Corte'].dt.components.hours + total_mes['Tempo Apos Corte'].dt.components.days * 24
                total_mes['Tempo Apos Corte Diurno           = '] = total_mes['Tempo Apos Corte Diurno'].dt.components.hours + total_mes['Tempo Apos Corte Diurno'].dt.components.days * 24
                total_mes['Tempo Apos Corte Noturno          = '] = total_mes['Tempo Apos Corte Noturno'].dt.components.hours + total_mes['Tempo Apos Corte Noturno'].dt.components.days * 24
                total_mes['Tempo Apos Corte Especial Diurno  = '] = total_mes['Tempo Apos Corte Especial Diurno'].dt.components.hours + total_mes['Tempo Apos Corte Especial Diurno'].dt.components.days * 24
                total_mes['Tempo Apos Corte Especial Noturno = '] = total_mes['Tempo Apos Corte Especial Noturno'].dt.components.hours + total_mes['Tempo Apos Corte Especial Noturno'].dt.components.days * 24
                
                total_mes['Tempo Apos Corte                          = '] = total_mes['Tempo Apos Corte                          = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apos Corte'].dt.components.minutes.astype(str).str.zfill(2)
                total_mes['Tempo Apos Corte Diurno           = '] = total_mes['Tempo Apos Corte Diurno           = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apos Corte Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                total_mes['Tempo Apos Corte Noturno          = '] = total_mes['Tempo Apos Corte Noturno          = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apos Corte Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                total_mes['Tempo Apos Corte Especial Diurno  = '] = total_mes['Tempo Apos Corte Especial Diurno  = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apos Corte Especial Diurno'].dt.components.minutes.astype(str).str.zfill(2)
                total_mes['Tempo Apos Corte Especial Noturno = '] = total_mes['Tempo Apos Corte Especial Noturno = '].astype(str).str.zfill(2) + ':' + total_mes['Tempo Apos Corte Especial Noturno'].dt.components.minutes.astype(str).str.zfill(2)
                 
                arquivo.write('Total por mes:'.ljust(15) + '\n')
                
                # Converter 'Checkin' para período mensal
                periodo_mensal = pd.to_datetime(dados['Checkin'][linha]).to_period('M')
                
                # Verificar se o período mensal está no índice de 'total_mes'
                if periodo_mensal in total_mes.index: 
                    # Acessar os valores específicos das colunas desejadas
                    valores = total_mes.loc[periodo_mensal, ['Tempo Apos Corte                          = ', 'Tempo Apos Corte Diurno           = ', 'Tempo Apos Corte Noturno          = ', 'Tempo Apos Corte Especial Diurno  = ', 'Tempo Apos Corte Especial Noturno = ']]

                    for coluna in valores.index:
                        valor_str = f"{coluna.ljust(50)}: {valores[coluna]}"
                        arquivo.write(valor_str + '\n')
                else:
                    print(f"Período mensal {periodo_mensal} não encontrado no índice de 'total_mes'.")

                arquivo.write(linha_dupla + '\f')

                titulo = 'EXTRATO TOTAL DE HORAS APOS CORTE DOS MOTORES'
                largura_total = 120
                titulo_centralizado = titulo.center(largura_total)
                arquivo.write(titulo_centralizado + '\n')
                arquivo.write('Activity'.ljust(15) + 'Checkin'.ljust(21) + 'Start'.ljust(14) + 'Dep'.ljust(5) + 'Arr'.ljust(12) + 'End'.ljust(20) + 'Checkout'.ljust(15) + 'Tempo Apos Corte'.ljust(15) + '\n')
                arquivo.write(linha_simples + '\n')
        
    arquivo.write(linha_simples + '\n')
    
    arquivo.write('Total por mes:'.ljust(15) + '\n')
    
    # Converter 'Checkin' para período mensal
    periodo_mensal = pd.to_datetime(dados['Checkin'][linha]).to_period('M')
    
    # Verificar se o período mensal está no índice de 'total_mes'
    if periodo_mensal in total_mes.index:
        # Acessar os valores específicos das colunas desejadas
        valores = total_mes.loc[periodo_mensal, ['Tempo Apos Corte                          = ', 'Tempo Apos Corte Diurno           = ', 'Tempo Apos Corte Noturno          = ', 'Tempo Apos Corte Especial Diurno  = ', 'Tempo Apos Corte Especial Noturno = ']]
        
        # Iterar sobre as colunas e escrever cada valor no arquivo
        for coluna in valores.index:
            valor_str = f"{coluna.ljust(50)}: {valores[coluna]}"
            arquivo.write(valor_str + '\n')
    else:
        print(f"Período mensal {periodo_mensal} não encontrado no índice de 'total_mes'.")

print("\n🎉 Relatório gerado com sucesso!")
print(f"📁 Arquivo salvo em: {novo_nome}")
print("✅ Processamento concluído!")