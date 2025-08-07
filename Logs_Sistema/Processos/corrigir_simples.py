"""
Versão simplificada para corrigir o erro de sintaxe
"""

def corrigir_arquivo_simples():
    """Corrige erros de sintaxe de forma mais direta"""
    
    arquivo = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - CORRIGIDO.py"
    
    print("CORRIGINDO ARQUIVO DE FORMA SIMPLES")
    print("="*40)
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        print(f"OK: {len(linhas)} linhas carregadas")
    except Exception as e:
        print(f"ERRO: {e}")
        return
    
    # Buscar e corrigir linha por linha
    correcoes = 0
    for i, linha in enumerate(linhas):
        linha_original = linha
        
        # Corrigir padrões específicos que causam erro
        # Exemplo: hora_checkin == 06 -> hora_checkin == 6
        substituicoes = [
            (' == 01', ' == 1'),
            (' == 02', ' == 2'),
            (' == 03', ' == 3'),
            (' == 04', ' == 4'),
            (' == 05', ' == 5'),
            (' == 06', ' == 6'),
            (' == 07', ' == 7'),
            (' == 08', ' == 8'),
            (' == 09', ' == 9'),
            (' > 06', ' > 6'),
            (' >= 06', ' >= 6'),
            (' < 06', ' < 6'),
            (' <= 06', ' <= 6'),
            ('(hora_checkin == 6 and minuto_checkin >= 01)', '(hora_checkin == 6 and minuto_checkin >= 1)'),
            ('minuto_checkin >= 01', 'minuto_checkin >= 1'),
        ]
        
        for antigo, novo in substituicoes:
            if antigo in linha:
                linha = linha.replace(antigo, novo)
                if linha != linha_original:
                    print(f"Linha {i+1}: {antigo} -> {novo}")
                    correcoes += 1
        
        linhas[i] = linha
    
    print(f"\\nTotal de correções: {correcoes}")
    
    if correcoes > 0:
        # Salvar arquivo corrigido
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.writelines(linhas)
            print("OK: Arquivo salvo")
            
            # Testar sintaxe
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            try:
                compile(conteudo, arquivo, 'exec')
                print("OK: Sintaxe corrigida com sucesso!")
            except SyntaxError as e:
                print(f"ERRO: Linha {e.lineno}: {e.msg}")
                if e.text:
                    print(f"   Texto: {e.text.strip()}")
                    
        except Exception as e:
            print(f"ERRO ao salvar: {e}")
    else:
        print("Nenhuma correção necessária")

if __name__ == "__main__":
    corrigir_arquivo_simples()
