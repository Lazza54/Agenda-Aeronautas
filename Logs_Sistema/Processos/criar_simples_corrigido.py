"""
Criar versão final SIMPLES apenas com a correção essencial do erro de variável
"""

def criar_versao_simples_corrigida():
    """Cria versão com APENAS a correção do erro de variável"""
    
    arquivo_origem = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL.py"
    arquivo_destino = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - ERRO CORRIGIDO.py"
    
    print("CRIANDO VERSAO SIMPLES CORRIGIDA")
    print("="*50)
    
    try:
        with open(arquivo_origem, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        print("OK: Arquivo original carregado")
    except Exception as e:
        print(f"ERRO: {e}")
        return
    
    # ÚNICA CORREÇÃO: trocar atividades_excluidos por atividades_excluidas
    if "atividades_excluidos" in conteudo:
        conteudo = conteudo.replace("atividades_excluidos", "atividades_excluidas")
        print("OK: Erro de variável corrigido")
    else:
        print("OK: Erro já estava corrigido")
    
    # Salvar
    try:
        with open(arquivo_destino, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"OK: Arquivo salvo: {arquivo_destino}")
        
        # Testar sintaxe
        try:
            compile(conteudo, arquivo_destino, 'exec')
            print("OK: Sintaxe correta")
        except SyntaxError as e:
            print(f"AVISO: Erro de sintaxe na linha {e.lineno}: {e.msg}")
            
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    criar_versao_simples_corrigida()
