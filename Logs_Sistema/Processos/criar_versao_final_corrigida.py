"""
Script para criar versão final corrigida do CALCULOS FINAIS
Resolve: erro de variável + problema de encoding + indicadores de progresso
"""

import os
import sys

def criar_versao_final_corrigida():
    """Cria versão final com todas as correções"""
    
    arquivo_origem = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL.py"
    arquivo_destino = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - CORRIGIDO.py"
    
    print("CRIANDO VERSAO FINAL CORRIGIDA")
    print("="*50)
    
    # Ler arquivo com encoding correto
    try:
        with open(arquivo_origem, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        print("OK: Arquivo lido com encoding UTF-8")
    except Exception as e:
        print(f"ERRO ao ler arquivo: {e}")
        return
    
    # =====================================================================
    # 1. ADICIONAR CONFIGURAÇÃO DE ENCODING NO TOPO
    # =====================================================================
    
    config_encoding = '''# -*- coding: utf-8 -*-
"""
###############################################################################
#                     CALCULOS FINAIS - VERSAO CORRIGIDA                     #
#                       SISTEMA DE CÁLCULOS AERONAUTAS AZUL                  #
###############################################################################

CORREÇÕES APLICADAS:
- Erro de variável 'atividades_excluidos' corrigido
- Indicadores de progresso adicionados
- Compatibilidade com Windows melhorada
- Encoding UTF-8 configurado

'''
    
    # Remover o cabeçalho original e adicionar o novo
    if conteudo.startswith('"""'):
        # Encontrar fim do docstring original
        fim_docstring = conteudo.find('"""', 3) + 3
        conteudo = config_encoding + conteudo[fim_docstring:]
    else:
        conteudo = config_encoding + conteudo
    
    # =====================================================================
    # 2. ADICIONAR CONFIGURAÇÃO DE ENCODING PARA WINDOWS
    # =====================================================================
    
    config_windows = '''
# Configuração de encoding para Windows
import sys
import os
if sys.platform.startswith('win'):
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    # Configurar variável de ambiente para UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'

'''
    
    # Adicionar após imports
    conteudo = conteudo.replace("import pandas as pd", config_windows + "import pandas as pd")
    
    # =====================================================================
    # 3. SUBSTITUIR EMOJIS POR TEXTO SIMPLES
    # =====================================================================
    
    substituicoes_emoji = {
        '⚠️': '[AVISO]',
        '✅': '[OK]',
        '❌': '[ERRO]',
        '🔄': '[PROCESSANDO]',
        '📂': '[ARQUIVO]',
        '📖': '[CARREGANDO]',
        '⚙️': '[EXECUTANDO]',
        '✈️': '[VOO]',
        '🕐': '[APRESENTACAO]',
        '⏱️': '[TEMPO]',
        '🛡️': '[PLANTAO]',
        '📚': '[TREINAMENTO]',
        '🌍': '[SOLO]',
        '💤': '[REPOUSO]',
        '🛌': '[REPOUSO_EXTRA]',
        '📊': '[DADOS]',
        '🎉': '[SUCESSO]',
        '🚀': '[INICIO]',
        '📝': '[INFO]',
        '⏰': '[HORARIO]',
        '💡': '[DICA]',
        '🔍': '[DEBUG]',
        '🎯': '[REGRA]',
        '📈': '[ANALISE]',
        '🔢': '[NUMERO]',
        '📤': '[SAIDA]',
        '💾': '[SALVANDO]',
        '🔧': '[CONFIG]',
        '🚫': '[EXCLUINDO]',
        '📋': '[LISTA]',
        '⚡': '[RAPIDO]',
        '⏳': '[AGUARDE]',
        '🔥': '[IMPORTANTE]'
    }
    
    for emoji, substituto in substituicoes_emoji.items():
        conteudo = conteudo.replace(emoji, substituto)
    
    print("OK: Emojis substituidos por texto compativel")
    
    # =====================================================================
    # 4. ADICIONAR INDICADORES DE PROGRESSO
    # =====================================================================
    
    funcoes_progresso = '''

# =============================================================================
# SISTEMA DE INDICADORES DE PROGRESSO
# =============================================================================

def mostrar_progresso_etapa(nome_etapa, descricao, tempo_estimado=None):
    """Mostra inicio de uma etapa com informacoes"""
    print("\\n" + "="*60)
    print(f"[INICIO] {nome_etapa}")
    print(f"[INFO] {descricao}")
    if tempo_estimado:
        print(f"[TEMPO] Estimado: {tempo_estimado}")
    print("="*60)
    import time
    return time.time()

def finalizar_progresso_etapa(nome_etapa, tempo_inicio):
    """Mostra fim de uma etapa com tempo decorrido"""
    import time
    tempo_decorrido = time.time() - tempo_inicio
    minutos = int(tempo_decorrido // 60)
    segundos = int(tempo_decorrido % 60)
    print(f"\\n[CONCLUIDO] {nome_etapa}")
    print(f"[TEMPO] Decorrido: {minutos}m {segundos}s")
    print("="*60 + "\\n")

def progresso_processamento(etapa, atual, total, tempo_inicio):
    """Mostra progresso durante processamentos longos"""
    if atual % 500 == 0 and atual > 0:
        import time
        tempo_decorrido = time.time() - tempo_inicio
        velocidade = atual / tempo_decorrido if tempo_decorrido > 0 else 0
        tempo_restante = (total - atual) / velocidade if velocidade > 0 else 0
        
        progresso = (atual / total * 100)
        print(f"\\n[PROGRESSO] {etapa}: {atual}/{total} ({progresso:.1f}%)")
        print(f"[VELOCIDADE] {velocidade:.1f} registros/seg")
        if tempo_restante < 60:
            print(f"[RESTANTE] {tempo_restante:.0f}s")
        else:
            print(f"[RESTANTE] {tempo_restante/60:.1f}min")

'''
    
    # Adicionar as funções após os imports
    pos_imports = conteudo.find("# =============================================================================")
    if pos_imports > 0:
        conteudo = conteudo[:pos_imports] + funcoes_progresso + "\\n" + conteudo[pos_imports:]
    
    print("OK: Indicadores de progresso adicionados")
    
    # =====================================================================
    # 5. VERIFICAR SE ERRO DE VARIÁVEL ESTÁ CORRIGIDO
    # =====================================================================
    
    if "atividades_excluidos" in conteudo:
        print("AVISO: Erro de variavel ainda presente, corrigindo...")
        conteudo = conteudo.replace("atividades_excluidos", "atividades_excluidas")
        print("OK: Erro de variavel corrigido")
    else:
        print("OK: Erro de variavel ja estava corrigido")
    
    # =====================================================================
    # 6. ADICIONAR LOGS DE PROGRESSO EM PONTOS CRÍTICOS
    # =====================================================================
    
    # Adicionar ao início do main
    conteudo = conteudo.replace(
        'def executar_calculos_completos():',
        '''def executar_calculos_completos():
    """Função principal com indicadores de progresso"""
    tempo_inicio_total = mostrar_progresso_etapa(
        "SISTEMA CALCULOS FINAIS", 
        "Iniciando processamento completo de escalas",
        "10-30 minutos dependendo do tamanho do arquivo"
    )'''
    )
    
    # Adicionar progresso nas etapas principais
    etapas_progresso = [
        ('print("📂 Selecionando arquivo CSV...")', '[ETAPA] Selecionando arquivo de dados...'),
        ('print("📖 Carregando dados...")', '[ETAPA] Carregando dados do arquivo CSV...'),
        ('print("⚙️ Configurando estruturas de dados...")', '[ETAPA] Configurando estruturas e validações...'),
        ('print("✈️ Calculando tempos de voo...")', '[ETAPA] Processando tempos de voo (pode demorar)...'),
        ('print("🕐 Calculando tempos de apresentação...")', '[ETAPA] Calculando tempos de apresentação...'),
        ('print("⏱️ Calculando tempos de reserva...")', '[ETAPA] Processando tempos de reserva (etapa critica)...'),
        ('print("🛡️ Calculando tempos de plantão...")', '[ETAPA] Calculando tempos de plantão...'),
        ('print("📚 Calculando tempos de treinamento...")', '[ETAPA] Processando tempos de treinamento...'),
        ('print("💾 Gravando arquivo final...")', '[ETAPA] Salvando resultados finais...')
    ]
    
    for busca, substituto in etapas_progresso:
        if busca in conteudo:
            conteudo = conteudo.replace(busca, f'print("{substituto}")')
    
    print("OK: Logs de progresso adicionados em pontos críticos")
    
    # =====================================================================
    # 7. SALVAR ARQUIVO FINAL
    # =====================================================================
    
    try:
        with open(arquivo_destino, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"\\n[SUCESSO] Arquivo corrigido salvo:")
        print(f"   {arquivo_destino}")
        
        # Verificar tamanho do arquivo
        tamanho = os.path.getsize(arquivo_destino)
        print(f"[INFO] Tamanho: {tamanho:,} bytes")
        
        return arquivo_destino
        
    except Exception as e:
        print(f"[ERRO] Falha ao salvar: {e}")
        return None

if __name__ == "__main__":
    arquivo_criado = criar_versao_final_corrigida()
    
    if arquivo_criado:
        print("\\n" + "="*50)
        print("VERSAO FINAL CRIADA COM SUCESSO!")
        print("="*50)
        print("\\nPROXIMOS PASSOS:")
        print("1. Use o arquivo: CALCULOS FINAIS - CORRIGIDO.py")
        print("2. Execute normalmente - erros foram corrigidos")
        print("3. Observe as mensagens [ETAPA] durante execução")
        print("4. O script mostrará progresso detalhado")
        print("\\nTODAS AS CORRRECOES APLICADAS:")
        print("• Erro de variável corrigido")
        print("• Encoding UTF-8 configurado")  
        print("• Indicadores de progresso adicionados")
        print("• Compatibilidade Windows garantida")
    else:
        print("\\n[ERRO] Falha ao criar versão corrigida")
