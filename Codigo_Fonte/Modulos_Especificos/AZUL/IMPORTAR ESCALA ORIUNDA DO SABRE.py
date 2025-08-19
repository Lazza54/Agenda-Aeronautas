##### IMPORTAR BIBLIOTECAS NECESSÁRIAS
import csv
from typing import Union, Any
import tabula
import pandas as pd
import numpy as np
import re
import PyPDF2
from datetime import timedelta, time, datetime

import pendulum
from pendulum import now, yesterday, tomorrow, timezone, date
import dateutil
import os
import warnings
import requests
import pprint
import json
from tkinter import filedialog
from pandas import DataFrame
from pandas.io.parsers import TextFileReader

# Bibliotecas para OCR
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_DISPONIVEL = True
except ImportError:
    OCR_DISPONIVEL = False
    print("⚠️ OCR não disponível. Para PDFs baseados em imagem, instale: pip install pytesseract pdf2image")

warnings.filterwarnings("ignore")

### LEITURA DO ARQUIVO DE SIGLAS SABRE
path = filedialog.askopenfilename()

print(path)

#imported_data = tabula.read_pdf(path, pages="all")

imported_data = open(path, 'rb')
pdf_reader = PyPDF2.PdfReader(imported_data)

num_paginas = len(pdf_reader.pages)
num_paginas

pagina = pdf_reader.pages[0]

print(f"Arquivo PDF aberto: {imported_data}")
print(f"Número total de páginas: {num_paginas}")

# Extrair texto da primeira página
try:
    texto_primeira_pagina = pagina.extract_text()
    print("\n=== CONTEÚDO DA PRIMEIRA PÁGINA ===")
    print(texto_primeira_pagina[:500])  # Primeiros 500 caracteres
    print("..." if len(texto_primeira_pagina) > 500 else "")
except Exception as e:
    print(f"Erro ao extrair texto: {e}")

# Função para extrair dados de todas as páginas
def extrair_dados_completos(pdf_reader):
    """Extrai texto de todas as páginas do PDF"""
    dados_completos = []
    
    for i, pagina in enumerate(pdf_reader.pages):
        try:
            texto = pagina.extract_text()
            dados_completos.append({
                'pagina': i + 1,
                'texto': texto,
                'linhas': texto.split('\n') if texto else []
            })
            print(f"Página {i + 1} processada - {len(texto)} caracteres")
        except Exception as e:
            print(f"Erro na página {i + 1}: {e}")
            dados_completos.append({
                'pagina': i + 1,
                'texto': '',
                'linhas': [],
                'erro': str(e)
            })
    
    return dados_completos

# Extrair dados de todas as páginas
print(f"\n=== PROCESSANDO {num_paginas} PÁGINAS ===")
dados_pdf = extrair_dados_completos(pdf_reader)

# Fechar arquivo
imported_data.close()

print("\nProcessamento concluído!")

print(dados_pdf)  # Exibir as primeiras 3 páginas para verificação

# Análise básica do conteúdo
def analisar_conteudo_escala(dados_pdf):
    """Analisa o conteúdo para identificar padrões da escala"""
    
    print("\n=== ANÁLISE DO CONTEÚDO ===")
    
    # Procurar por padrões comuns em escalas
    padroes_encontrados = {
        'datas': [],
        'horarios': [],
        'aeroportos': [],
        'voos': []
    }
    
    for pagina_data in dados_pdf:
        texto = pagina_data['texto']
        
        # Procurar datas (formato DD/MM ou DD-MM)
        datas = re.findall(r'\b\d{1,2}[/-]\d{1,2}\b', texto)
        padroes_encontrados['datas'].extend(datas)
        
        # Procurar horários (formato HH:MM)
        horarios = re.findall(r'\b\d{1,2}:\d{2}\b', texto)
        padroes_encontrados['horarios'].extend(horarios)
        
        # Procurar códigos de aeroportos (3 letras maiúsculas)
        aeroportos = re.findall(r'\b[A-Z]{3}\b', texto)
        padroes_encontrados['aeroportos'].extend(aeroportos)
        
        # Procurar códigos de voo (letra seguida de números)
        voos = re.findall(r'\b[A-Z]\d{3,4}\b', texto)
        padroes_encontrados['voos'].extend(voos)
    
    # Mostrar estatísticas
    for categoria, itens in padroes_encontrados.items():
        itens_unicos = list(set(itens))
        print(f"{categoria.capitalize()}: {len(itens)} encontrados, {len(itens_unicos)} únicos")
        if itens_unicos:
            print(f"  Exemplos: {itens_unicos[:5]}")
    
    return padroes_encontrados

# Executar análise
padroes = analisar_conteudo_escala(dados_pdf)

# Se PyPDF2 não extraiu texto, tentar com tabula-py
print("\n=== TENTATIVA COM TABULA-PY ===")
if all(len(p['texto']) == 0 for p in dados_pdf):
    print("PyPDF2 não conseguiu extrair texto. Tentando com tabula-py...")
    
    try:
        # Tentar extrair tabelas com tabula
        tabelas = tabula.read_pdf(path, pages="all", multiple_tables=True)
        
        print(f"Tabula encontrou {len(tabelas)} tabelas")
        
        for i, tabela in enumerate(tabelas):
            print(f"\n--- TABELA {i+1} ---")
            print(f"Dimensões: {tabela.shape}")
            print(f"Colunas: {list(tabela.columns)}")
            print("\nPrimeiras 3 linhas:")
            print(tabela.head(3))
            
            # Salvar cada tabela como CSV
            nome_arquivo = f"escala_tabela_{i+1}.csv"
            tabela.to_csv(nome_arquivo, index=False)
            print(f"✅ Tabela salva como: {nome_arquivo}")
        
        # Tentar extrair todo o conteúdo como uma única tabela
        print("\n=== EXTRAÇÃO COMPLETA ===")
        try:
            df_completo = tabula.read_pdf(path, pages="all", lattice=True, pandas_options={'header': None})
            if isinstance(df_completo, list) and len(df_completo) > 0:
                df_principal = df_completo[0]
                print(f"Dados principais extraídos: {df_principal.shape}")
                print("\nPrimeiras linhas dos dados:")
                print(df_principal.head())
                
                # Salvar dados principais
                df_principal.to_csv("escala_dados_principais.csv", index=False)
                print("✅ Dados principais salvos como: escala_dados_principais.csv")
                
        except Exception as e:
            print(f"Erro na extração completa: {e}")
    
    except Exception as e:
        print(f"Erro com tabula-py: {e}")
        print("\n💡 SUGESTÕES:")
        print("1. O PDF pode conter apenas imagens")
        print("2. Considere usar OCR (pytesseract)")
        print("3. Verifique se o PDF não está protegido")
        print("4. Tente converter o PDF para outro formato primeiro")

# Tentar OCR se disponível
if OCR_DISPONIVEL and all(len(p['texto']) == 0 for p in dados_pdf):
    print("\n=== TENTATIVA COM OCR ===")
    print("Convertendo PDF para imagens e aplicando OCR...")
    
    try:
        # Converter PDF para imagens
        imagens = convert_from_path(path, dpi=300)
        print(f"PDF convertido em {len(imagens)} imagens")
        
        texto_ocr_completo = []
        
        for i, imagem in enumerate(imagens):
            print(f"Processando página {i+1} com OCR...")
            
            # Aplicar OCR na imagem
            texto_pagina = pytesseract.image_to_string(imagem, lang='por')
            texto_ocr_completo.append({
                'pagina': i + 1,
                'texto': texto_pagina,
                'linhas': texto_pagina.split('\n')
            })
            
            # Salvar imagem para debug
            nome_imagem = f"pagina_{i+1}.png"
            imagem.save(nome_imagem)
            print(f"Imagem salva: {nome_imagem}")
        
        # Mostrar resultado do OCR
        print(f"\n=== RESULTADO OCR ===")
        for pagina_ocr in texto_ocr_completo:
            texto = pagina_ocr['texto']
            print(f"Página {pagina_ocr['pagina']}: {len(texto)} caracteres extraídos")
            
            if texto.strip():
                print(f"Primeiros 200 caracteres:")
                print(texto[:200])
                print("...\n")
                
                # Salvar texto extraído
                nome_arquivo_txt = f"ocr_pagina_{pagina_ocr['pagina']}.txt"
                with open(nome_arquivo_txt, 'w', encoding='utf-8') as f:
                    f.write(texto)
                print(f"✅ Texto OCR salvo: {nome_arquivo_txt}")
        
        # Analisar conteúdo OCR
        if texto_ocr_completo:
            print("\n=== ANÁLISE OCR ===")
            padroes_ocr = analisar_conteudo_escala(texto_ocr_completo)
            
            # Criar DataFrame com dados OCR
            dados_estruturados = []
            for pagina_ocr in texto_ocr_completo:
                linhas = pagina_ocr['linhas']
                for i, linha in enumerate(linhas):
                    if linha.strip():
                        dados_estruturados.append({
                            'pagina': pagina_ocr['pagina'],
                            'linha': i + 1,
                            'conteudo': linha.strip()
                        })
            
            if dados_estruturados:
                df_ocr = pd.DataFrame(dados_estruturados)
                df_ocr.to_csv("dados_ocr_completos.csv", index=False)
                print(f"✅ Dados OCR salvos: dados_ocr_completos.csv")
                print(f"Total de linhas extraídas: {len(dados_estruturados)}")
    
    except Exception as e:
        print(f"Erro no OCR: {e}")
        print("💡 Verifique se o Tesseract está instalado:")
        print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Configure o caminho se necessário:")
        print("   pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")

elif not OCR_DISPONIVEL:
    print("\n⚠️ OCR não está disponível.")
    print("Para PDFs baseados em imagem, instale:")
    print("pip install pytesseract pdf2image")
    print("E instale o Tesseract OCR no sistema")

# Análise final
print(f"\n=== RESUMO FINAL ===")
print(f"Arquivo processado: {os.path.basename(path)}")
print(f"Páginas: {num_paginas}")
print(f"Método PyPDF2: {'[OK] Sucesso' if any(len(p['texto']) > 0 for p in dados_pdf) else '[ERRO] Sem texto'}")

# Função para processar dados de escala (se houver)
def processar_escala_azul(dados):
    """Processa dados específicos de escala da Azul"""
    
    escalas_processadas = []
    
    # Se tivermos dados do tabula
    if 'tabelas' in locals() and len(tabelas) > 0:
        for tabela in tabelas:
            # Procurar por colunas típicas de escala
            colunas_escala = ['data', 'horario', 'voo', 'origem', 'destino', 'aeronave', 'posicao']
            
            for col in tabela.columns:
                col_lower = str(col).lower()
                for escala_col in colunas_escala:
                    if escala_col in col_lower:
                        print(f"Coluna identificada: {col} -> {escala_col}")
    
    return escalas_processadas

# Verificar se encontrou dados estruturados
if 'tabelas' in locals():
    escalas = processar_escala_azul(tabelas)
    print(f"Escalas processadas: {len(escalas)}")

print("\nPRÓXIMOS PASSOS:")
print("1. Analise os arquivos CSV gerados")
print("2. Identifique padrões nos dados")
print("3. Ajuste o processamento conforme necessário")

escalas_processadas = processar_escala_azul(dados_pdf)

print(escalas_processadas)