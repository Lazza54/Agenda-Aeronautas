"""
Script para adicionar indicadores de progresso ao CALCULOS FINAIS - FINAL.py
Para evitar que o usuário tenha a impressão de que o script travou

Características dos indicadores:
1. Progresso visual com barras TQDM
2. Contadores de etapas concluídas
3. Estimativas de tempo restante
4. Mensagens informativas em pontos críticos
5. Indicação clara de início/fim de cada etapa
"""

import os
import sys

def adicionar_indicadores_progresso():
    """Adiciona indicadores de progresso ao script principal"""
    
    arquivo_origem = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL.py"
    arquivo_destino = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL - COM PROGRESSO.py"
    
    print("🔄 Adicionando indicadores de progresso...")
    
    with open(arquivo_origem, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # =========================================================================
    # 1. ADICIONAR IMPORTS NECESSÁRIOS
    # =========================================================================
    
    # Adicionar time import se não existir
    if "import time" not in conteudo:
        conteudo = conteudo.replace("import warnings", "import warnings\nimport time")
    
    # =========================================================================
    # 2. FUNÇÃO DE PROGRESSO
    # =========================================================================
    
    funcao_progresso = '''
# =============================================================================
# SISTEMA DE INDICADORES DE PROGRESSO
# =============================================================================

def mostrar_progresso_etapa(etapa, descricao, total_estimado=None):
    """Mostra o início de uma etapa com estimativa de tempo"""
    print(f"\\n{'='*60}")
    print(f"🚀 INICIANDO ETAPA: {etapa}")
    print(f"📝 {descricao}")
    if total_estimado:
        print(f"⏱️ Tempo estimado: {total_estimado}")
    print(f"{'='*60}")
    return time.time()

def finalizar_progresso_etapa(etapa, tempo_inicio):
    """Mostra o fim de uma etapa com tempo decorrido"""
    tempo_decorrido = time.time() - tempo_inicio
    minutos = int(tempo_decorrido // 60)
    segundos = int(tempo_decorrido % 60)
    print(f"\\n✅ ETAPA CONCLUÍDA: {etapa}")
    print(f"⏱️ Tempo decorrido: {minutos}m {segundos}s")
    print(f"{'='*60}\\n")

def progresso_calculo(descricao, registros_processados, total_registros, tempo_inicio):
    """Mostra progresso durante cálculos extensos"""
    if registros_processados % 500 == 0 and registros_processados > 0:
        tempo_decorrido = time.time() - tempo_inicio
        velocidade = registros_processados / tempo_decorrido if tempo_decorrido > 0 else 0
        tempo_restante = (total_registros - registros_processados) / velocidade if velocidade > 0 else 0
        
        progresso_pct = (registros_processados / total_registros * 100)
        
        print(f"\\n📊 {descricao}: {registros_processados}/{total_registros} ({progresso_pct:.1f}%)")
        print(f"⚡ Velocidade: {velocidade:.1f} registros/seg")
        if tempo_restante < 60:
            print(f"⏳ Tempo restante estimado: {tempo_restante:.0f}s")
        else:
            print(f"⏳ Tempo restante estimado: {tempo_restante/60:.1f}min")
'''
    
    # Adicionar após as importações
    conteudo = conteudo.replace("DIAGNOSTICO_ATIVO = True", 
                               funcao_progresso + "\n\nDIAGNOSTICO_ATIVO = True")
    
    # =========================================================================
    # 3. ADICIONAR PROGRESSO NO INÍCIO DO MAIN
    # =========================================================================
    
    conteudo = conteudo.replace(
        'def main():',
        '''def main():
    print("\\n" + "="*80)
    print("🎯 SISTEMA DE CÁLCULOS AERONAUTAS AZUL - INICIANDO PROCESSAMENTO")
    print("="*80)
    tempo_inicio_total = time.time()'''
    )
    
    # =========================================================================
    # 4. PROGRESSO NA LEITURA DO ARQUIVO
    # =========================================================================
    
    conteudo = conteudo.replace(
        'print("📂 Selecionando arquivo CSV...")',
        '''tempo_etapa = mostrar_progresso_etapa("SELEÇÃO DE ARQUIVO", 
                                              "Aguardando seleção do arquivo CSV para processamento")
    print("📂 Selecionando arquivo CSV...")'''
    )
    
    conteudo = conteudo.replace(
        'print("✅ Arquivo selecionado!")',
        '''print("✅ Arquivo selecionado!")
    finalizar_progresso_etapa("SELEÇÃO DE ARQUIVO", tempo_etapa)'''
    )
    
    # =========================================================================
    # 5. PROGRESSO NA CARGA INICIAL
    # =========================================================================
    
    conteudo = conteudo.replace(
        'print("📖 Carregando dados...")',
        '''tempo_etapa = mostrar_progresso_etapa("CARREGAMENTO DE DADOS", 
                                              "Lendo arquivo CSV e inicializando estruturas de dados",
                                              "30-60 segundos")
    print("📖 Carregando dados...")'''
    )
    
    conteudo = conteudo.replace(
        'print(f"✅ Arquivo carregado com sucesso! {len(df)} registros encontrados.")',
        '''print(f"✅ Arquivo carregado com sucesso! {len(df)} registros encontrados.")
    finalizar_progresso_etapa("CARREGAMENTO DE DADOS", tempo_etapa)'''
    )
    
    # =========================================================================
    # 6. PROGRESSO NAS CONFIGURAÇÕES INICIAIS
    # =========================================================================
    
    conteudo = conteudo.replace(
        'print("⚙️ Configurando estruturas de dados...")',
        '''tempo_etapa = mostrar_progresso_etapa("CONFIGURAÇÃO INICIAL", 
                                              "Aplicando configurações, validações e estruturas de dados",
                                              "1-2 minutos")
    print("⚙️ Configurando estruturas de dados...")'''
    )
    
    # =========================================================================
    # 7. PROGRESSO NOS CÁLCULOS PRINCIPAIS
    # =========================================================================
    
    # Calcular tempo de voo
    conteudo = conteudo.replace(
        'print("✈️ Calculando tempos de voo...")',
        '''finalizar_progresso_etapa("CONFIGURAÇÃO INICIAL", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("CÁLCULO DE TEMPO DE VOO", 
                                        "Processando registros de voo e calculando tempos por categoria",
                                        "2-5 minutos")
    print("✈️ Calculando tempos de voo...")'''
    )
    
    # Apresentação
    conteudo = conteudo.replace(
        'print("🕐 Calculando tempos de apresentação...")',
        '''finalizar_progresso_etapa("CÁLCULO DE TEMPO DE VOO", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("CÁLCULO DE APRESENTAÇÃO", 
                                        "Classificando tempos de apresentação por horário e dia da semana",
                                        "1-3 minutos")
    print("🕐 Calculando tempos de apresentação...")'''
    )
    
    # Reserva
    conteudo = conteudo.replace(
        'print("⏱️ Calculando tempos de reserva...")',
        '''finalizar_progresso_etapa("CÁLCULO DE APRESENTAÇÃO", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("CÁLCULO DE RESERVA", 
                                        "Processando diferentes tipos de reserva e aplicando regras específicas",
                                        "3-8 minutos")
    print("⏱️ Calculando tempos de reserva...")'''
    )
    
    # Plantão
    conteudo = conteudo.replace(
        'print("🛡️ Calculando tempos de plantão...")',
        '''finalizar_progresso_etapa("CÁLCULO DE RESERVA", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("CÁLCULO DE PLANTÃO", 
                                        "Classificando atividades de plantão por período e tipo",
                                        "2-4 minutos")
    print("🛡️ Calculando tempos de plantão...")'''
    )
    
    # Treinamento
    conteudo = conteudo.replace(
        'print("📚 Calculando tempos de treinamento...")',
        '''finalizar_progresso_etapa("CÁLCULO DE PLANTÃO", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("CÁLCULO DE TREINAMENTO", 
                                        "Processando atividades de treinamento e simulação",
                                        "1-2 minutos")
    print("📚 Calculando tempos de treinamento...")'''
    )
    
    # Solo
    conteudo = conteudo.replace(
        'print("🌍 Calculando tempos em solo entre etapas...")',
        '''finalizar_progresso_etapa("CÁLCULO DE TREINAMENTO", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("CÁLCULO DE TEMPO EM SOLO", 
                                        "Analisando intervalos entre etapas de voo",
                                        "2-4 minutos")
    print("🌍 Calculando tempos em solo entre etapas...")'''
    )
    
    # Repouso
    conteudo = conteudo.replace(
        'print("💤 Calculando tempos de repouso...")',
        '''finalizar_progresso_etapa("CÁLCULO DE TEMPO EM SOLO", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("CÁLCULO DE REPOUSO", 
                                        "Processando períodos de repouso obrigatório",
                                        "1-2 minutos")
    print("💤 Calculando tempos de repouso...")'''
    )
    
    # Repouso Extra
    conteudo = conteudo.replace(
        'print("🛌 Calculando tempos de repouso extra...")',
        '''finalizar_progresso_etapa("CÁLCULO DE REPOUSO", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("CÁLCULO DE REPOUSO EXTRA", 
                                        "Processando períodos de repouso adicional",
                                        "1-2 minutos")
    print("🛌 Calculando tempos de repouso extra...")'''
    )
    
    # =========================================================================
    # 8. PROGRESSO NA FINALIZAÇÃO
    # =========================================================================
    
    conteudo = conteudo.replace(
        'print("📊 Finalizando processamento...")',
        '''finalizar_progresso_etapa("CÁLCULO DE REPOUSO EXTRA", tempo_etapa)
    
    tempo_etapa = mostrar_progresso_etapa("FINALIZAÇÃO", 
                                        "Salvando resultados e gerando relatórios finais",
                                        "30-60 segundos")
    print("📊 Finalizando processamento...")'''
    )
    
    # =========================================================================
    # 9. TEMPO TOTAL NO FINAL
    # =========================================================================
    
    conteudo = conteudo.replace(
        'print("✅ Processamento concluído com sucesso!")',
        '''finalizar_progresso_etapa("FINALIZAÇÃO", tempo_etapa)
    
    tempo_total = time.time() - tempo_inicio_total
    horas = int(tempo_total // 3600)
    minutos = int((tempo_total % 3600) // 60)
    segundos = int(tempo_total % 60)
    
    print("\\n" + "="*80)
    print("🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print(f"⏱️ Tempo total de execução: {horas}h {minutos}m {segundos}s")
    print("="*80)'''
    )
    
    # =========================================================================
    # 10. PROGRESSO EM LOOPS EXTENSOS (ADICIONAR CONTADORES)
    # =========================================================================
    
    # No loop de reserva (que pode ser longo)
    conteudo = conteudo.replace(
        'for index, row in tqdm(registros_com_reserva.iterrows(), total=len(registros_com_reserva), desc="Reserva"):',
        '''print(f"\\n🔄 Processando {len(registros_com_reserva)} registros de reserva...")
    tempo_inicio_reserva = time.time()
    contador_reserva = 0
    
    for index, row in tqdm(registros_com_reserva.iterrows(), total=len(registros_com_reserva), desc="Reserva"):
        contador_reserva += 1
        if contador_reserva % 500 == 0:
            progresso_calculo("Processamento de Reserva", contador_reserva, len(registros_com_reserva), tempo_inicio_reserva)'''
    )
    
    # No loop de apresentação
    conteudo = conteudo.replace(
        'for index, row in tqdm(registros_com_apresentacao.iterrows(), total=len(registros_com_apresentacao), desc="Apresentação"):',
        '''print(f"\\n🔄 Processando {len(registros_com_apresentacao)} registros de apresentação...")
    tempo_inicio_apresentacao = time.time()
    contador_apresentacao = 0
    
    for index, row in tqdm(registros_com_apresentacao.iterrows(), total=len(registros_com_apresentacao), desc="Apresentação"):
        contador_apresentacao += 1
        if contador_apresentacao % 500 == 0:
            progresso_calculo("Processamento de Apresentação", contador_apresentacao, len(registros_com_apresentacao), tempo_inicio_apresentacao)'''
    )
    
    # =========================================================================
    # 11. SALVAR ARQUIVO COM INDICADORES
    # =========================================================================
    
    with open(arquivo_destino, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ Arquivo com indicadores de progresso salvo em:")
    print(f"   {arquivo_destino}")
    
    return arquivo_destino

if __name__ == "__main__":
    adicionar_indicadores_progresso()
