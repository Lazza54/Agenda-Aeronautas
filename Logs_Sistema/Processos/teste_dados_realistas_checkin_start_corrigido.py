#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste com dados realistas para validar as regras especiais de Checkin == Start
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Importar a função usando importlib para arquivos com espaços no nome
import importlib.util
spec = importlib.util.spec_from_file_location("calculos_finais", "CALCULOS FINAIS.py")
calculos_finais = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calculos_finais)
calcular_tempos_apresentacao = calculos_finais.calcular_tempos_apresentacao

def criar_dados_realistas():
    """Cria um DataFrame com dados mais realistas de voos"""
    
    dados = [
        # Casos típicos de voos comerciais com Checkin == Start
        {
            'Activity': 'AD 2971 GRU-SDU',
            'Checkin': '2024-01-15 07:30:00',  # Segunda, 07:30
            'Start': '2024-01-15 07:30:00',    # Checkin == Start
            'End': '2024-01-15 09:45:00',
            'Checkout': '2024-01-15 10:15:00',
            'Tempo Apresentacao': '01:00:00',
            'Dia_Semana': 0,  # Segunda-feira
            'Esperado': 'Diurno'
        },
        {
            'Activity': 'AD 4152 SDU-GRU',
            'Checkin': '2024-01-19 19:15:00',  # Sexta, 19:15
            'Start': '2024-01-19 19:15:00',    # Checkin == Start
            'End': '2024-01-19 21:30:00',
            'Checkout': '2024-01-19 22:00:00',
            'Tempo Apresentacao': '01:30:00',
            'Dia_Semana': 4,  # Sexta-feira (≠ 5)
            'Esperado': 'Noturno'
        },
        {
            'Activity': 'AD 2756 GRU-CGH',
            'Checkin': '2024-01-20 20:00:00',  # Sábado, 20:00
            'Start': '2024-01-20 20:00:00',    # Checkin == Start
            'End': '2024-01-20 21:15:00',
            'Checkout': '2024-01-20 21:45:00',
            'Tempo Apresentacao': '01:15:00',
            'Dia_Semana': 5,  # Sábado
            'Esperado': 'Especial_Noturno'
        },
        {
            'Activity': 'AD 4891 CGH-BSB',
            'Checkin': '2024-01-21 08:00:00',  # Domingo, 08:00
            'Start': '2024-01-21 08:00:00',    # Checkin == Start
            'End': '2024-01-21 10:30:00',
            'Checkout': '2024-01-21 11:00:00',
            'Tempo Apresentacao': '02:00:00',
            'Dia_Semana': 6,  # Domingo
            'Esperado': 'Especial_Diurno'
        },
        {
            'Activity': 'AD 4323 BSB-GRU',
            'Checkin': '2024-01-21 03:30:00',  # Domingo, 03:30 (madrugada)
            'Start': '2024-01-21 03:30:00',    # Checkin == Start
            'End': '2024-01-21 05:45:00',
            'Checkout': '2024-01-21 06:15:00',
            'Tempo Apresentacao': '01:45:00',
            'Dia_Semana': 6,  # Domingo
            'Esperado': 'Especial_Noturno'
        },
        
        # Casos com Checkin ≠ Start para comparação
        {
            'Activity': 'AD 2845 GRU-REC',
            'Checkin': '2024-01-16 06:30:00',  # Terça, 06:30
            'Start': '2024-01-16 07:30:00',    # Checkin ≠ Start
            'End': '2024-01-16 10:45:00',
            'Checkout': '2024-01-16 11:15:00',
            'Tempo Apresentacao': '02:30:00',
            'Dia_Semana': 1,  # Terça-feira
            'Esperado': 'Diurno'  # Regra geral
        },
        {
            'Activity': 'AD 4567 REC-GRU',
            'Checkin': '2024-01-21 09:00:00',  # Domingo, 09:00
            'Start': '2024-01-21 10:00:00',    # Checkin ≠ Start
            'End': '2024-01-21 13:15:00',
            'Checkout': '2024-01-21 13:45:00',
            'Tempo Apresentacao': '01:00:00',
            'Dia_Semana': 6,  # Domingo
            'Esperado': 'Especial_Noturno'  # Regra geral para domingo
        },
        
        # Casos limite
        {
            'Activity': 'AD 5621 GRU-POA',
            'Checkin': '2024-01-17 06:01:00',  # Quarta, 06:01 (limite diurno)
            'Start': '2024-01-17 06:01:00',    # Checkin == Start
            'End': '2024-01-17 08:30:00',
            'Checkout': '2024-01-17 09:00:00',
            'Tempo Apresentacao': '01:30:00',
            'Dia_Semana': 2,  # Quarta-feira (≠ 6)
            'Esperado': 'Diurno'
        },
        {
            'Activity': 'AD 7834 POA-GRU',
            'Checkin': '2024-01-21 06:01:00',  # Domingo, 06:01 (limite especial diurno)
            'Start': '2024-01-21 06:01:00',    # Checkin == Start
            'End': '2024-01-21 08:45:00',
            'Checkout': '2024-01-21 09:15:00',
            'Tempo Apresentacao': '01:15:00',
            'Dia_Semana': 6,  # Domingo
            'Esperado': 'Especial_Diurno'
        },
        {
            'Activity': 'AD 9876 GRU-FOR',
            'Checkin': '2024-01-21 06:00:00',  # Domingo, 06:00 (limite especial noturno)
            'Start': '2024-01-21 06:00:00',    # Checkin == Start
            'End': '2024-01-21 09:30:00',
            'Checkout': '2024-01-21 10:00:00',
            'Tempo Apresentacao': '02:00:00',
            'Dia_Semana': 6,  # Domingo
            'Esperado': 'Especial_Noturno'
        }
    ]
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Converter colunas para os tipos corretos
    df['Checkin'] = pd.to_datetime(df['Checkin'])
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = pd.to_datetime(df['End'])
    df['Checkout'] = pd.to_datetime(df['Checkout'])
    df['Apresentacao'] = pd.to_timedelta(df['Apresentacao'])
    
    # Criar colunas de tempo de apresentação
    df['Tempo Apresentacao Diurno'] = pd.Timedelta(0)
    df['Tempo Apresentacao Noturno'] = pd.Timedelta(0)
    df['Tempo Apresentacao Especial Noturno'] = pd.Timedelta(0)
    df['Tempo Apresentacao Especial Diurno'] = pd.Timedelta(0)
    
    return df

def analisar_resultados(df):
    """Analisa os resultados detalhadamente"""
    
    print("📋 ANÁLISE DETALHADA DOS RESULTADOS:")
    print("=" * 100)
    
    for index, row in df.iterrows():
        activity = row['Activity']
        checkin_start_igual = row['Checkin'] == row['Start']
        checkin_str = row['Checkin'].strftime('%a %H:%M')
        
        # Verificar qual categoria foi preenchida
        categorias = {
            'Diurno': row['Tempo Apresentacao Diurno'],
            'Noturno': row['Tempo Apresentacao Noturno'],
            'Especial_Noturno': row['Tempo Apresentacao Especial Noturno'],
            'Especial_Diurno': row['Tempo Apresentacao Especial Diurno']
        }
        
        categorias_preenchidas = [cat for cat, tempo in categorias.items() if tempo > pd.Timedelta(0)]
        
        print(f"✈️ {activity}")
        print(f"   📅 {checkin_str} | Dia_Semana: {row['Dia_Semana']} | Checkin==Start: {checkin_start_igual}")
        print(f"   ⏱️ Apresentação: {row['Apresentacao']} | Esperado: {row['Esperado']}")
        print(f"   🎯 Categoria(s): {categorias_preenchidas}")
        
        if len(categorias_preenchidas) == 1:
            categoria_real = categorias_preenchidas[0]
            tempo_real = categorias[categoria_real]
            status = "✅" if categoria_real == row['Esperado'] else "❌"
            print(f"   {status} Resultado: {categoria_real} ({tempo_real})")
        else:
            print(f"   ❌ ERRO: Múltiplas categorias preenchidas!")
        
        print()

def main():
    """Função principal de teste com dados realistas"""
    print("🧪 TESTE COM DADOS REALISTAS - REGRAS ESPECIAIS (Checkin == Start)")
    print("=" * 100)
    
    # Criar DataFrame de teste
    df_teste = criar_dados_realistas()
    
    print(f"📊 Total de voos para teste: {len(df_teste)}")
    print(f"✈️ Casos Checkin == Start: {(df_teste['Checkin'] == df_teste['Start']).sum()}")
    print(f"✈️ Casos Checkin ≠ Start: {(df_teste['Checkin'] != df_teste['Start']).sum()}")
    
    print("\n" + "=" * 100)
    
    # Aplicar a função de cálculo
    df_resultado = calcular_tempos_apresentacao(df_teste)
    
    print("\n" + "=" * 100)
    
    # Analisar resultados
    analisar_resultados(df_resultado)
    
    # Validação final
    sucessos = 0
    falhas = 0
    
    for index, row in df_resultado.iterrows():
        categorias = {
            'Diurno': row['Tempo Apresentacao Diurno'],
            'Noturno': row['Tempo Apresentacao Noturno'],
            'Especial_Noturno': row['Tempo Apresentacao Especial Noturno'],
            'Especial_Diurno': row['Tempo Apresentacao Especial Diurno']
        }
        
        categorias_preenchidas = [cat for cat, tempo in categorias.items() if tempo > pd.Timedelta(0)]
        
        if len(categorias_preenchidas) == 1 and categorias_preenchidas[0] == row['Esperado']:
            sucessos += 1
        else:
            falhas += 1
    
    print("=" * 100)
    print(f"📊 RESULTADO FINAL: {sucessos} sucessos, {falhas} falhas")
    
    if falhas == 0:
        print("🎉 TODOS OS TESTES COM DADOS REALISTAS PASSARAM!")
        print("✅ A implementação está funcionando corretamente!")
    else:
        print(f"⚠️ {falhas} testes falharam - Revisar implementação")
    
    return falhas == 0

if __name__ == "__main__":
    main()
