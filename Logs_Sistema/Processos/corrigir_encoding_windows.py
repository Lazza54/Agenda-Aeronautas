"""
Script para criar versão compatível com Windows (sem emojis problemáticos)
Para evitar problemas de encoding no terminal
"""

import os

def corrigir_encoding_windows():
    """Remove emojis problemáticos para compatibilidade com Windows"""
    
    arquivo_origem = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL - COM PROGRESSO.py"
    arquivo_destino = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL - WINDOWS.py"
    
    print("🔄 Criando versão compatível com Windows...")
    
    with open(arquivo_origem, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # =========================================================================
    # SUBSTITUIR EMOJIS PROBLEMÁTICOS POR TEXTO SIMPLES
    # =========================================================================
    
    substituicoes = {
        '⚠️': '[AVISO]',
        '✅': '[OK]',
        '❌': '[ERRO]',
        '🔄': '[PROCESSANDO]',
        '📂': '[ARQUIVO]',
        '📖': '[CARREGANDO]',
        '⚙️': '[CONFIG]',
        '✈️': '[VOO]',
        '🕐': '[TEMPO]',
        '⏱️': '[CRONOMETRO]',
        '🛡️': '[PLANTAO]',
        '📚': '[TREINAMENTO]',
        '🌍': '[SOLO]',
        '💤': '[REPOUSO]',
        '🛌': '[REPOUSO_EXTRA]',
        '📊': '[RELATORIO]',
        '🎉': '[SUCESSO]',
        '🚀': '[INICIO]',
        '📝': '[DESCRICAO]',
        '⏰': '[HORARIO]',
        '💡': '[DICA]',
        '🔍': '[BUSCA]',
        '🎯': '[ALVO]',
        '📈': '[GRAFICO]',
        '🔢': '[NUMERO]',
        '📤': '[SAIDA]',
        '🧪': '[TESTE]',
        '🛑': '[PARAR]',
        '🔴': '[MARCADOR]',
        '📋': '[LISTA]',
        '⚡': '[VELOCIDADE]',
        '⏳': '[TEMPO_RESTANTE]',
        '🔥': '[IMPORTANTE]',
        '🎲': '[ALEATORIO]'
    }
    
    for emoji, substituto in substituicoes.items():
        conteudo = conteudo.replace(emoji, substituto)
    
    # =========================================================================
    # ADICIONAR CONFIGURAÇÃO DE ENCODING NO INÍCIO
    # =========================================================================
    
    configuracao_encoding = '''# -*- coding: utf-8 -*-
import sys
import io

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

'''
    
    # Adicionar após a primeira linha de comentário
    linhas = conteudo.split('\n')
    if linhas[0].startswith('"""'):
        # Encontrar o fim do docstring
        fim_docstring = 1
        while fim_docstring < len(linhas) and not linhas[fim_docstring].endswith('"""'):
            fim_docstring += 1
        fim_docstring += 1
        
        # Inserir configuração após o docstring
        linhas.insert(fim_docstring, configuracao_encoding)
        conteudo = '\n'.join(linhas)
    else:
        conteudo = configuracao_encoding + conteudo
    
    # =========================================================================
    # SALVAR VERSÃO CORRIGIDA
    # =========================================================================
    
    with open(arquivo_destino, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"[OK] Versão para Windows criada: {arquivo_destino}")
    
    return arquivo_destino

if __name__ == "__main__":
    corrigir_encoding_windows()
