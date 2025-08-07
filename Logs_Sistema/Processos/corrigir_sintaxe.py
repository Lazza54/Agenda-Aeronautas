"""
Corrige erros de sintaxe no arquivo CALCULOS FINAIS - CORRIGIDO.py
"""

import re

def corrigir_zeros_leading():
    """Corrige números com zeros à esquerda que causam erro de sintaxe"""
    
    arquivo = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - CORRIGIDO.py"
    
    print("CORRIGINDO ERROS DE SINTAXE")
    print("="*40)
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        print("OK: Arquivo carregado")
    except Exception as e:
        print(f"ERRO: {e}")
        return
    
    # Buscar padrões problemáticos
    print("\\nBuscando padrões problemáticos...")
    
    # Padrão: números que começam com 0 seguido de dígitos (mas não são strings)
    # Exemplo: 06, 07, 08, 09
    padrao_zeros = r'\\b0([1-9]\\d*)\\b'
    
    matches = re.findall(padrao_zeros, conteudo)
    if matches:
        print(f"Encontrados {len(matches)} números com zeros à esquerda:")
        for match in set(matches):
            print(f"   0{match}")
    
    # Corrigir: remover zero à esquerda, mas apenas para números (não strings)
    # Usar contexto para evitar corrigir strings como "R01", "S02", etc.
    
    conteudo_corrigido = conteudo
    
    # Buscar contextos específicos onde zeros à esquerda são problemáticos
    # Exemplo: hora_checkin == 06 (número), mas não "R06" (string)
    
    padroes_corrigir = [
        (r'== 0([1-9])', r'== \\1'),  # == 06 -> == 6
        (r'> 0([1-9])(?!\\d)', r'> \\1'),   # > 06 -> > 6 (não seguido de dígito)
        (r'< 0([1-9])(?!\\d)', r'< \\1'),   # < 06 -> < 6
        (r'>= 0([1-9])(?!\\d)', r'>= \\1'), # >= 06 -> >= 6
        (r'<= 0([1-9])(?!\\d)', r'<= \\1'), # <= 06 -> <= 6
        (r'\\( 0([1-9])(?!\\d)', r'( \\1'),  # ( 06 -> ( 6
        (r', 0([1-9])(?!\\d)', r', \\1'),   # , 06 -> , 6
    ]
    
    correcoes = 0
    for padrao, substituicao in padroes_corrigir:
        matches_antes = len(re.findall(padrao, conteudo_corrigido))
        conteudo_corrigido = re.sub(padrao, substituicao, conteudo_corrigido)
        matches_depois = len(re.findall(padrao, conteudo_corrigido))
        correcoes_feitas = matches_antes - matches_depois
        if correcoes_feitas > 0:
            print(f"Corrigido padrão {padrao}: {correcoes_feitas} ocorrências")
            correcoes += correcoes_feitas
    
    print(f"\\nTotal de correções: {correcoes}")
    
    # Salvar arquivo corrigido
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_corrigido)
        print("OK: Arquivo salvo com correções")
        
        # Testar sintaxe
        try:
            compile(conteudo_corrigido, arquivo, 'exec')
            print("OK: Sintaxe agora está correta")
        except SyntaxError as e:
            print(f"ERRO: Ainda há problema de sintaxe:")
            print(f"   Linha {e.lineno}: {e.text}")
            print(f"   Erro: {e.msg}")
            
    except Exception as e:
        print(f"ERRO ao salvar: {e}")

if __name__ == "__main__":
    corrigir_zeros_leading()
