"""
Script para investigar por que os cálculos param a partir da linha 1516
Especificamente na coluna Tempo Reserva Especial Diurno
"""

import pandas as pd
import os
import sys

def investigar_linha_1516():
    """Investiga o problema a partir da linha 1516"""
    
    arquivo_csv = input("Digite o caminho do arquivo CSV para investigação: ").strip().strip('"')
    
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        return
    
    print(f"📂 Carregando: {arquivo_csv}")
    
    try:
        df = pd.read_csv(arquivo_csv, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(arquivo_csv, encoding='latin-1', low_memory=False)
        except:
            print("❌ Erro ao carregar arquivo")
            return
    
    print(f"📊 Total de registros: {len(df)}")
    
    # =========================================================================
    # ANÁLISE GERAL DA LINHA 1516
    # =========================================================================
    
    linha_problema = 1516
    if linha_problema >= len(df):
        print(f"⚠️ O arquivo só tem {len(df)} linhas. Linha {linha_problema} não existe.")
        return
    
    print(f"\\n🔍 INVESTIGANDO LINHA {linha_problema}")
    print("="*60)
    
    # Mostrar dados da linha específica
    registro = df.iloc[linha_problema - 1]  # -1 porque pandas é 0-indexed
    
    print(f"📅 Data: {registro.get('Data', 'N/A')}")
    print(f"🔖 Id_Leg: {registro.get('Id_Leg', 'N/A')}")
    print(f"📍 Activity: {registro.get('Activity', 'N/A')}")
    print(f"⏰ Start: {registro.get('Start', 'N/A')}")
    print(f"🏁 End: {registro.get('End', 'N/A')}")
    print(f"📝 Reserva: {registro.get('Reserva', 'N/A')}")
    
    # =========================================================================
    # VERIFICAR COLUNAS DE TEMPO DE RESERVA
    # =========================================================================
    
    colunas_reserva = [
        'Tempo Reserva Diurno',
        'Tempo Reserva Noturno', 
        'Tempo Reserva Especial Diurno',
        'Tempo Reserva Especial Noturno'
    ]
    
    print(f"\\n📊 COLUNAS DE TEMPO DE RESERVA NA LINHA {linha_problema}:")
    for coluna in colunas_reserva:
        if coluna in df.columns:
            valor = registro.get(coluna, 'N/A')
            print(f"   {coluna}: {valor}")
        else:
            print(f"   {coluna}: ❌ COLUNA NÃO EXISTE")
    
    # =========================================================================
    # ANÁLISE DE PADRÕES ANTES E DEPOIS DA LINHA 1516
    # =========================================================================
    
    print(f"\\n🔍 ANÁLISE DE PADRÕES (LINHAS {linha_problema-10} A {linha_problema+10})")
    print("="*80)
    
    inicio = max(0, linha_problema - 11)  # -11 porque vamos usar slice de 10 para cada lado
    fim = min(len(df), linha_problema + 10)
    
    subset = df.iloc[inicio:fim].copy()
    subset['Linha'] = range(inicio + 1, fim + 1)  # +1 para linha real (1-indexed)
    
    # Focar na coluna problemática
    coluna_problema = 'Tempo Reserva Especial Diurno'
    
    if coluna_problema in df.columns:
        print(f"\\n📈 VALORES DA COLUNA '{coluna_problema}':")
        for i, row in subset.iterrows():
            linha_num = row['Linha']
            valor = row.get(coluna_problema, 'N/A')
            reserva = row.get('Reserva', 'N/A')
            activity = row.get('Activity', 'N/A')
            
            marcador = "🔴" if linha_num == linha_problema else "  "
            print(f"{marcador} Linha {linha_num:4d}: {valor:15} | Reserva: {reserva:15} | Activity: {activity}")
    
    # =========================================================================
    # VERIFICAR SE EXISTE PADRÃO GERAL DE ZEROS
    # =========================================================================
    
    print(f"\\n🔍 ANÁLISE DE ZEROS EM TODAS AS COLUNAS DE TEMPO")
    print("="*60)
    
    colunas_tempo = [col for col in df.columns if col.startswith('Tempo ')]
    
    # Contar zeros antes e depois da linha 1516
    antes_1516 = df.iloc[:linha_problema-1]
    depois_1516 = df.iloc[linha_problema-1:]
    
    print(f"\\n📊 COMPARAÇÃO ANTES/DEPOIS DA LINHA {linha_problema}:")
    print(f"{'Coluna':<35} {'Zeros Antes':<12} {'Total Antes':<12} {'Zeros Depois':<12} {'Total Depois':<12}")
    print("-" * 85)
    
    for coluna in colunas_tempo:
        if coluna in df.columns:
            # Contar zeros antes
            zeros_antes = (antes_1516[coluna] == '0 days 00:00:00').sum() if not antes_1516.empty else 0
            zeros_antes += (antes_1516[coluna] == '0 days').sum() if not antes_1516.empty else 0
            zeros_antes += (antes_1516[coluna] == 0).sum() if not antes_1516.empty else 0
            total_antes = len(antes_1516)
            
            # Contar zeros depois
            zeros_depois = (depois_1516[coluna] == '0 days 00:00:00').sum() if not depois_1516.empty else 0
            zeros_depois += (depois_1516[coluna] == '0 days').sum() if not depois_1516.empty else 0
            zeros_depois += (depois_1516[coluna] == 0).sum() if not depois_1516.empty else 0
            total_depois = len(depois_1516)
            
            print(f"{coluna:<35} {zeros_antes:<12} {total_antes:<12} {zeros_depois:<12} {total_depois:<12}")
    
    # =========================================================================
    # VERIFICAR REGISTROS COM RESERVA NÃO ZERO
    # =========================================================================
    
    print(f"\\n🔍 REGISTROS COM RESERVA NÃO ZERO APÓS LINHA {linha_problema}")
    print("="*60)
    
    # Filtrar registros depois da linha 1516 que tenham reserva
    depois_com_reserva = depois_1516[
        (pd.notna(depois_1516.get('Reserva', pd.Series()))) & 
        (depois_1516.get('Reserva', pd.Series()) != '0 days 00:00:00') &
        (depois_1516.get('Reserva', pd.Series()) != '0 days') &
        (depois_1516.get('Reserva', pd.Series()) != 0)
    ]
    
    if not depois_com_reserva.empty:
        print(f"📊 Encontrados {len(depois_com_reserva)} registros com reserva após linha {linha_problema}")
        print("\\nPrimeiros 10 registros:")
        
        for i, (idx, row) in enumerate(depois_com_reserva.head(10).iterrows()):
            linha_real = idx + 1
            reserva = row.get('Reserva', 'N/A')
            activity = row.get('Activity', 'N/A')
            tempo_res_esp_diurno = row.get('Tempo Reserva Especial Diurno', 'N/A')
            
            print(f"   Linha {linha_real:4d}: Reserva={reserva:15} | Activity={activity:10} | Tempo_Res_Esp_Diurno={tempo_res_esp_diurno}")
    else:
        print(f"❌ Nenhum registro com reserva encontrado após linha {linha_problema}")
    
    # =========================================================================
    # PROCURAR MOMENTO EXATO ONDE PARAM OS CÁLCULOS
    # =========================================================================
    
    print(f"\\n🎯 PROCURANDO MOMENTO EXATO ONDE PARAM OS CÁLCULOS")
    print("="*60)
    
    # Procurar a última linha com cálculo não zero
    ultima_linha_calculada = None
    primeira_linha_zero = None
    
    for i in range(len(df)):
        tem_calculo = False
        for coluna in colunas_tempo:
            if coluna in df.columns:
                valor = df.iloc[i][coluna]
                if pd.notna(valor) and valor != '0 days 00:00:00' and valor != '0 days' and valor != 0:
                    tem_calculo = True
                    break
        
        if tem_calculo:
            ultima_linha_calculada = i + 1  # +1 para linha real
        elif ultima_linha_calculada is not None and primeira_linha_zero is None:
            primeira_linha_zero = i + 1  # +1 para linha real
    
    if ultima_linha_calculada:
        print(f"✅ Última linha com cálculos: {ultima_linha_calculada}")
    if primeira_linha_zero:
        print(f"🔴 Primeira linha só com zeros: {primeira_linha_zero}")
    
    print(f"\\n📋 INVESTIGAÇÃO CONCLUÍDA")
    print("="*60)

if __name__ == "__main__":
    investigar_linha_1516()
