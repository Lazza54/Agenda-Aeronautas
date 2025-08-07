#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigação específica da Activity "FP" na linha 1516
"""

import pandas as pd
import os

def investigar_activity_fp():
    """Investigar especificamente os registros com Activity FP"""
    
    print("🔍 INVESTIGAÇÃO ESPECÍFICA: Activity FP (linha 1516)")
    print("=" * 60)
    
    # Ler o arquivo mais recente
    diretorio_saida = "G:/PROJETOS PYTHON/aeronautas_azul/AERONAUTAS/ARQUIVOS TRABALHADOS/RICARDO LAZZARINI"
    
    # Buscar arquivo mais recente
    arquivos = [f for f in os.listdir(diretorio_saida) if f.endswith('.csv')]
    arquivo_mais_recente = max(arquivos, key=lambda x: os.path.getctime(os.path.join(diretorio_saida, x)))
    caminho_arquivo = os.path.join(diretorio_saida, arquivo_mais_recente)
    
    print(f"📁 Analisando arquivo: {arquivo_mais_recente}")
    
    df = pd.read_csv(caminho_arquivo)
    
    # Verificar se FP está nas listas de atividades
    print("\n🔍 VERIFICAÇÃO DAS LISTAS DE ATIVIDADES:")
    
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
    
    print(f"   FP está em lista_reservas? {'FP' in lista_reservas_json}")
    print(f"   FP está em lista_treinamentos? {'FP' in lista_treinamentos}")
    
    # Filtrar registros com Activity = 'FP'
    registros_fp = df[df['Activity'] == 'FP'].copy()
    print(f"\n📊 Total de registros com Activity 'FP': {len(registros_fp)}")
    
    if len(registros_fp) == 0:
        print("⚠️ Nenhum registro com Activity 'FP' encontrado!")
        return
    
    # Analisar distribuição dos registros FP
    print("\n📋 DISTRIBUIÇÃO DOS REGISTROS FP:")
    print(f"   Primeiro índice: {registros_fp.index.min()}")
    print(f"   Último índice: {registros_fp.index.max()}")
    print(f"   Antes da linha 1516: {(registros_fp.index <= 1516).sum()}")
    print(f"   Depois da linha 1516: {(registros_fp.index > 1516).sum()}")
    
    # Analisar especificamente a linha 1516
    if 1516 in df.index:
        linha_1516 = df.loc[1516]
        print("\n🎯 ANÁLISE DA LINHA 1516:")
        print(f"   Activity: {linha_1516['Activity']}")
        if 'Jornada' in df.columns:
            print(f"   Jornada: {linha_1516['Jornada']}")
        if 'Checkin' in df.columns:
            print(f"   Checkin: {linha_1516['Checkin']}")
    
    # Verificar se FP tem Jornada válida (para reserva) ou se deveria ser treinamento
    if 'Jornada' in df.columns:
        print("\n⏰ ANÁLISE DA JORNADA EM REGISTROS FP:")
        
        try:
            jornada_fp = pd.to_timedelta(registros_fp['Jornada'], errors='coerce')
            jornada_valida = jornada_fp > pd.Timedelta(0)
            
            print(f"   Registros FP com Jornada > 0: {jornada_valida.sum()}/{len(registros_fp)}")
            
            if jornada_valida.any():
                jornada_media = jornada_fp[jornada_valida].mean()
                print(f"   Jornada média nos registros FP válidos: {jornada_media}")
                
                # Verificar se algum FP tem Checkin válido (requisito para reserva)
                if 'Checkin' in df.columns:
                    checkin_valido = pd.notna(registros_fp['Checkin'])
                    registros_fp_criterios_reserva = (
                        (pd.to_timedelta(registros_fp['Jornada'], errors='coerce') > pd.Timedelta(0)) &
                        pd.notna(registros_fp['Checkin'])
                    )
                    
                    print(f"   Registros FP que atendem critérios de reserva: {registros_fp_criterios_reserva.sum()}")
                    
                    if registros_fp_criterios_reserva.any():
                        print("   🚨 PROBLEMA IDENTIFICADO: FP tem critérios de reserva mas não está na lista!")
                        
                        # Mostrar alguns exemplos
                        fp_com_criterios = registros_fp[registros_fp_criterios_reserva].head(3)
                        for i, (idx, row) in enumerate(fp_com_criterios.iterrows()):
                            print(f"      Exemplo {i+1} (linha {idx}):")
                            print(f"         Jornada: {row['Jornada']}")
                            print(f"         Checkin: {row['Checkin']}")
            
        except Exception as e:
            print(f"   ❌ Erro ao analisar Jornada: {e}")
    
    # Verificar se FP poderia ser treinamento
    if 'Tempo Apresentacao' in df.columns:
        print("\n📚 ANÁLISE PARA TREINAMENTO EM REGISTROS FP:")
        
        try:
            tempo_apresentacao_fp = pd.to_timedelta(registros_fp['Tempo Apresentacao'], errors='coerce')
            tempo_apres_valido = tempo_apresentacao_fp > pd.Timedelta(0)
            
            print(f"   Registros FP com Tempo Apresentacao > 0: {tempo_apres_valido.sum()}/{len(registros_fp)}")
            
            if tempo_apres_valido.any():
                print("   🚨 PROBLEMA IDENTIFICADO: FP tem Tempo Apresentacao mas não está na lista de treinamentos!")
        
        except Exception as e:
            print(f"   ❌ Erro ao analisar Tempo Apresentacao: {e}")
    
    print("\n🎯 CONCLUSÃO:")
    print("   FP parece ser uma atividade que DEVERIA estar em uma das listas")
    print("   (reserva ou treinamento) mas NÃO ESTÁ.")
    print("   Isso explicaria por que os cálculos não são aplicados aos registros FP.")
    print("   Recomendação: Verificar se FP deve ser adicionado a uma das listas.")

if __name__ == "__main__":
    investigar_activity_fp()
