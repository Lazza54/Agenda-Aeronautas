#!/usr/bin/env python3
"""
Analisador Simples de PDF - Escala Azul
Versão simplificada para análise manual de PDFs
"""

import PyPDF2
import pandas as pd
from tkinter import filedialog
import os
import re

def analisar_pdf_escala():
    """Análise básica de PDF de escala"""
    
    print("=== ANALISADOR DE PDF - ESCALA AZUL ===")
    print("Selecione o arquivo PDF da escala...")
    
    # Selecionar arquivo
    path = filedialog.askopenfilename(
        title="Selecione o PDF da Escala",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    
    if not path:
        print("Nenhum arquivo selecionado.")
        return
    
    print(f"Arquivo selecionado: {os.path.basename(path)}")
    
    # Abrir PDF
    try:
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_paginas = len(pdf_reader.pages)
            
            print(f"Número de páginas: {num_paginas}")
            
            # Tentar extrair texto
            texto_total = ""
            for i, pagina in enumerate(pdf_reader.pages):
                texto_pagina = pagina.extract_text()
                texto_total += texto_pagina
                print(f"Página {i+1}: {len(texto_pagina)} caracteres")
            
            if texto_total.strip():
                print("\n✅ TEXTO EXTRAÍDO COM SUCESSO!")
                
                # Salvar texto completo
                nome_txt = f"escala_texto_extraido.txt"
                with open(nome_txt, 'w', encoding='utf-8') as f:
                    f.write(texto_total)
                print(f"Texto salvo em: {nome_txt}")
                
                # Análise básica
                analisar_texto_escala(texto_total)
                
            else:
                print("\n❌ Não foi possível extrair texto do PDF")
                print("💡 POSSÍVEIS SOLUÇÕES:")
                print("1. O PDF pode ser baseado em imagens")
                print("2. Tente copiar e colar manualmente o conteúdo")
                print("3. Use um conversor online PDF para texto")
                print("4. Verifique se o PDF não está protegido")
                
                # Criar template para entrada manual
                criar_template_manual()
    
    except Exception as e:
        print(f"Erro ao processar PDF: {e}")

def analisar_texto_escala(texto):
    """Analisa o texto extraído procurando padrões de escala"""
    
    print("\n=== ANÁLISE DO TEXTO ===")
    
    # Procurar padrões
    padroes = {
        'datas': re.findall(r'\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b', texto),
        'horarios': re.findall(r'\b\d{1,2}:\d{2}\b', texto),
        'aeroportos': re.findall(r'\b[A-Z]{3}\b', texto),
        'voos': re.findall(r'\b[A-Z]{1,2}\d{3,4}\b', texto),
        'equipamentos': re.findall(r'\b(A\d{3}|B\d{3}|E\d{3})\b', texto)
    }
    
    for categoria, encontrados in padroes.items():
        unicos = list(set(encontrados))
        print(f"{categoria.capitalize()}: {len(encontrados)} total, {len(unicos)} únicos")
        if unicos:
            print(f"  Exemplos: {unicos[:5]}")
    
    # Criar CSV com dados estruturados
    dados_estruturados = []
    linhas = texto.split('\n')
    
    for i, linha in enumerate(linhas):
        linha = linha.strip()
        if linha:
            # Tentar identificar linhas que parecem ser de voos
            if any(padrao in linha for padrao in [':']) and len(linha) > 10:
                dados_estruturados.append({
                    'linha': i + 1,
                    'conteudo': linha,
                    'tem_horario': bool(re.search(r'\d{1,2}:\d{2}', linha)),
                    'tem_aeroporto': bool(re.search(r'\b[A-Z]{3}\b', linha)),
                    'tem_voo': bool(re.search(r'\b[A-Z]{1,2}\d{3,4}\b', linha))
                })
    
    if dados_estruturados:
        df = pd.DataFrame(dados_estruturados)
        df.to_csv('escala_dados_estruturados.csv', index=False, encoding='utf-8')
        print(f"\n✅ Dados estruturados salvos: escala_dados_estruturados.csv")
        print(f"Linhas processadas: {len(dados_estruturados)}")
        
        # Estatísticas
        linhas_com_horario = df[df['tem_horario']].shape[0]
        linhas_com_aeroporto = df[df['tem_aeroporto']].shape[0]
        linhas_com_voo = df[df['tem_voo']].shape[0]
        
        print(f"Linhas com horário: {linhas_com_horario}")
        print(f"Linhas com aeroporto: {linhas_com_aeroporto}")
        print(f"Linhas com voo: {linhas_com_voo}")

def criar_template_manual():
    """Cria um template para entrada manual dos dados"""
    
    template = """# TEMPLATE PARA ENTRADA MANUAL DE ESCALA

## Instruções:
1. Copie os dados do PDF e cole abaixo
2. Mantenha a estrutura de linhas
3. Salve este arquivo como .txt
4. Execute novamente o analisador

## DADOS DA ESCALA:
[Cole aqui o conteúdo do PDF]

## FORMATO ESPERADO:
Data: DD/MM/YYYY
Horário: HH:MM
Voo: ADXXXX
Aeroportos: GRU-SDU
Equipamento: A320

## EXEMPLO:
01/07/2024
AD4567 GRU-SDU 08:30-10:15 A320
AD4568 SDU-GRU 11:00-12:45 A320
"""
    
    with open('template_entrada_manual.txt', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"\n📝 Template criado: template_entrada_manual.txt")
    print("Use este arquivo para entrada manual dos dados")

def processar_entrada_manual():
    """Processa dados inseridos manualmente"""
    
    print("=== PROCESSAMENTO MANUAL ===")
    
    # Verificar se existe arquivo manual
    arquivo_manual = "dados_escala_manual.txt"
    if os.path.exists(arquivo_manual):
        with open(arquivo_manual, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        print(f"Processando arquivo manual: {arquivo_manual}")
        analisar_texto_escala(conteudo)
    else:
        print(f"Arquivo {arquivo_manual} não encontrado.")
        print("Crie este arquivo com os dados da escala e execute novamente.")

if __name__ == "__main__":
    print("ESCOLHA UMA OPÇÃO:")
    print("1. Analisar PDF automaticamente")
    print("2. Processar dados inseridos manualmente")
    
    while True:
        escolha = input("\nDigite 1 ou 2: ").strip()
        
        if escolha == "1":
            analisar_pdf_escala()
            break
        elif escolha == "2":
            processar_entrada_manual()
            break
        else:
            print("Por favor, digite 1 ou 2")
    
    print("\n✅ Processamento concluído!")
    input("Pressione Enter para sair...")
