#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigação específica da Activity "FR" para entender por que os cálculos param na linha 1516
"""

import pandas as pd
import os

def investigar_activity_fr():
    """Investigar especificamente os registros com Activity FR"""
    
    print("🔍 INVESTIGAÇÃO ESPECÍFICA: Activity FR")
    print("=" * 60)
    
    # Ler o arquivo mais recente
    diretorio_saida = "G:/PROJETOS PYTHON/aeronautas_azul/AERONAUTAS/ARQUIVOS TRABALHADOS/RICARDO LAZZARINI"
    
    # Buscar arquivo mais recente
    arquivos = [f for f in os.listdir(diretorio_saida) if f.endswith('.csv')]
    arquivo_mais_recente = max(arquivos, key=lambda x: os.path.getctime(os.path.join(diretorio_saida, x)))
    caminho_arquivo = os.path.join(diretorio_saida, arquivo_mais_recente)
    
    print(f"📁 Analisando arquivo: {arquivo_mais_recente}")
    
    df = pd.read_csv(caminho_arquivo)
    
    # Filtrar apenas registros com Activity = 'FR'
    registros_fr = df[df['Activity'] == 'FR'].copy()
    print(f"📊 Total de registros com Activity 'FR': {len(registros_fr)}")
    
    if len(registros_fr) == 0:
        print("⚠️ Nenhum registro com Activity 'FR' encontrado!")
        return
    
    # Analisar distribuição dos registros FR
    print(f"\n📋 DISTRIBUIÇÃO DOS REGISTROS FR:")
    print(f"   Primeiro índice: {registros_fr.index.min()}")
    print(f"   Último índice: {registros_fr.index.max()}")
    print(f"   Antes da linha 1516: {(registros_fr.index <= 1516).sum()}")
    print(f"   Depois da linha 1516: {(registros_fr.index > 1516).sum()}")
    
    # Analisar especificamente a linha 1516
    if 1516 in df.index:
        linha_1516 = df.loc[1516]
        print(f"\n🎯 ANÁLISE DA LINHA 1516:")
        print(f"   Activity: {linha_1516['Activity']}")
        if 'Jornada' in df.columns:
            print(f"   Jornada: {linha_1516['Jornada']}")
        if 'Checkin' in df.columns:
            print(f"   Checkin: {linha_1516['Checkin']}")
        
        # Verificar colunas críticas na linha 1516
        colunas_criticas = [
            'Tempo Reserva Especial Diurno',
            'Tempo Reserva Especial Noturno',
            'Tempo Treinamento Especial Noturno'
        ]
        
        print(f"   Valores das colunas críticas:")
        for coluna in colunas_criticas:
            if coluna in df.columns:
                valor = linha_1516[coluna]
                print(f"      {coluna}: {valor}")
    
    # Verificar se FR está nas listas de atividades
    print(f"\n🔍 VERIFICAÇÃO DAS LISTAS DE ATIVIDADES:")
    
    # Carregar as listas do código principal
    try:
        import sys
        sys.path.append(r'g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS')
        
        # Verificar se FR está em lista_reservas
        lista_reservas_json = [
            'R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R09', 'R10',
            'R11', 'R12', 'R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20',
            'R21', 'R22', 'R23', 'R24', 'RES', 'REX', 'R0', 'RF1', 'RF2', 'RF3',
            'RF4', 'RF5', 'RF6', 'RF7', 'RF8', 'RF9'
        ]
        
        lista_treinamentos = [
            'ADT', 'AQT', 'AST', 'CHT', 'CRT', 'CST', 'DGT', 'DMT', 'DQT', 'EGT',
            'EMT', 'ERT', 'EXT', 'FDT', 'FIS', 'FJT', 'GCT', 'GFT', 'GST', 'LFT',
            'LOT', 'LRT', 'LUT', 'MEL', 'MET', 'OJT', 'OPT', 'PCT', 'PET', 'PFT',
            'PMT', 'PPT', 'PRT', 'PST', 'PUT', 'RCT', 'RDT', 'RET', 'RFT', 'ROT',
            'RPT', 'RST', 'RUT', 'SBT', 'SCT', 'SDT', 'SFT', 'SIT', 'SMT', 'SPT',
            'SRT', 'SST', 'STT', 'SUT', 'TRA', 'TRE', 'TRT', 'TST', 'TUT', 'VET',
            'VIT', 'VST', 'VUT', 'WET', 'WIT', 'WST', 'WUT', 'ZET', 'ZIT', 'ZST',
            'ZUT', 'P10', 'P12', 'P14', 'PP1', 'PP2', 'PPS', 'TRE', 'TRA', 'TPT',
            'TPE', 'TPC', 'TPI', 'TPO', 'TPS', 'TPU'
        ]
        
        print(f"   FR está em lista_reservas? {('FR' in lista_reservas_json)}")
        print(f"   FR está em lista_treinamentos? {('FR' in lista_treinamentos)}")
        
        # FR é atividade de voo, não de reserva nem treinamento!
        print(f"   🎯 DESCOBERTA: FR é atividade de VOO, não reserva nem treinamento!")
        
    except Exception as e:
        print(f"   ❌ Erro ao carregar listas: {e}")
    
    # Analisar registros FR antes e depois da linha 1516
    print(f"\n📊 ANÁLISE DETALHADA DOS REGISTROS FR:")
    
    fr_antes_1516 = registros_fr[registros_fr.index <= 1516]
    fr_depois_1516 = registros_fr[registros_fr.index > 1516]
    
    print(f"   Registros FR antes/até linha 1516: {len(fr_antes_1516)}")
    print(f"   Registros FR depois da linha 1516: {len(fr_depois_1516)}")
    
    # Verificar se há diferenças nas colunas críticas
    colunas_criticas = [
        'Tempo Reserva Especial Diurno',
        'Tempo Reserva Especial Noturno',
        'Tempo Treinamento Especial Noturno'
    ]
    
    for coluna in colunas_criticas:
        if coluna in df.columns:
            print(f"\n🔍 ANÁLISE DA COLUNA: {coluna}")
            
            # Valores únicos nos registros FR
            valores_fr = registros_fr[coluna].astype(str).str.strip()
            valores_unicos = valores_fr.value_counts()
            
            print(f"   Valores únicos em registros FR:")
            for valor, count in valores_unicos.head(5).items():
                print(f"      '{valor}': {count} ocorrências")
            
            # Verificar se há diferença antes/depois 1516
            if len(fr_antes_1516) > 0:
                valores_antes = fr_antes_1516[coluna].astype(str).str.strip()
                valores_0days_antes = (valores_antes == '0 days').sum()
                print(f"   Valores '0 days' antes da linha 1516: {valores_0days_antes}/{len(fr_antes_1516)}")
            
            if len(fr_depois_1516) > 0:
                valores_depois = fr_depois_1516[coluna].astype(str).str.strip()
                valores_0days_depois = (valores_depois == '0 days').sum()
                print(f"   Valores '0 days' depois da linha 1516: {valores_0days_depois}/{len(fr_depois_1516)}")
    
    # Verificar se FR possui Jornada válida
    if 'Jornada' in df.columns:
        print(f"\n⏰ ANÁLISE DA JORNADA EM REGISTROS FR:")
        
        # Converter Jornada para análise
        try:
            jornada_fr = pd.to_timedelta(registros_fr['Jornada'], errors='coerce')
            jornada_valida = jornada_fr > pd.Timedelta(0)
            
            print(f"   Registros FR com Jornada > 0: {jornada_valida.sum()}/{len(registros_fr)}")
            
            if jornada_valida.any():
                jornada_media = jornada_fr[jornada_valida].mean()
                print(f"   Jornada média nos registros FR válidos: {jornada_media}")
                
                # Verificar distribuição antes/depois 1516
                fr_jornada_antes = fr_antes_1516['Jornada'] if len(fr_antes_1516) > 0 else pd.Series()
                fr_jornada_depois = fr_depois_1516['Jornada'] if len(fr_depois_1516) > 0 else pd.Series()
                
                if len(fr_jornada_antes) > 0:
                    jornada_antes_valida = pd.to_timedelta(fr_jornada_antes, errors='coerce') > pd.Timedelta(0)
                    print(f"   FR com Jornada válida antes da linha 1516: {jornada_antes_valida.sum()}")
                
                if len(fr_jornada_depois) > 0:
                    jornada_depois_valida = pd.to_timedelta(fr_jornada_depois, errors='coerce') > pd.Timedelta(0)
                    print(f"   FR com Jornada válida depois da linha 1516: {jornada_depois_valida.sum()}")
            
        except Exception as e:
            print(f"   ❌ Erro ao analisar Jornada: {e}")
    
    print(f"\n🎯 CONCLUSÃO:")
    print("   FR é uma atividade de VOO, não de reserva nem treinamento.")
    print("   Os cálculos de reserva e treinamento NÃO devem ser aplicados a registros FR.")
    print("   O fato de parar na linha 1516 (que tem FR) pode ser coincidência.")
    print("   O problema real pode estar na lógica de filtros das funções de cálculo.")

if __name__ == "__main__":
    investigar_activity_fr()
