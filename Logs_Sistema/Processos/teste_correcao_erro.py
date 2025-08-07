"""
Teste rápido para verificar se o erro da variável foi corrigido
"""

import subprocess
import sys
import os

def testar_correcao_erro():
    """Testa se a correção do erro de variável funcionou"""
    
    script_principal = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL.py"
    
    print("TESTE DE CORRECAO - ERRO DE VARIAVEL")
    print("="*50)
    
    if not os.path.exists(script_principal):
        print("ERRO: Script nao encontrado")
        return
    
    # Verificar se a correção foi aplicada no código
    print("1. VERIFICANDO CORRECAO NO CODIGO...")
    
    with open(script_principal, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    if "atividades_excluidos" in conteudo:
        print("   ERRO: Ainda existe 'atividades_excluidos' no codigo!")
        print("   Buscando localização...")
        linhas = conteudo.split('\n')
        for i, linha in enumerate(linhas):
            if "atividades_excluidos" in linha:
                print(f"   Linha {i+1}: {linha.strip()}")
    else:
        print("   OK: Erro de variavel corrigido no codigo")
    
    # Teste básico de sintaxe
    print("\n2. TESTANDO SINTAXE...")
    try:
        compile(conteudo, script_principal, 'exec')
        print("   OK: Sintaxe do arquivo esta correta")
    except SyntaxError as e:
        print(f"   ERRO DE SINTAXE: {e}")
        print(f"   Linha {e.lineno}: {e.text}")
        return
    
    # Teste de execução inicial (apenas imports e definições)
    print("\n3. TESTANDO EXECUCAO INICIAL...")
    try:
        # Testar apenas se consegue importar e definir funções sem executar main
        codigo_teste = '''
import sys
sys.path.append(r"g:\\PROJETOS PYTHON\\aeronautas_azul\\CODIGOS TERMINADOS")

# Tentar importar apenas as funções do arquivo
exec(open(r"g:\\PROJETOS PYTHON\\aeronautas_azul\\CODIGOS TERMINADOS\\CALCULOS FINAIS - FINAL.py").read().replace("if __name__ == '__main__':", "if False:"))

print("TESTE: Importacao e definicoes OK")
'''
        
        resultado = subprocess.run(
            [sys.executable, "-c", codigo_teste],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        if resultado.returncode == 0:
            print("   OK: Execucao inicial bem-sucedida")
            if resultado.stdout:
                print("   SAIDA:", resultado.stdout.strip())
        else:
            print(f"   ERRO: Codigo de retorno {resultado.returncode}")
            if resultado.stderr:
                print("   ERRO DETALHADO:")
                print(resultado.stderr)
                
                # Verificar se ainda é o erro da variável
                if "atividades_excluidos" in resultado.stderr:
                    print("   >>> AINDA EXISTE O ERRO DA VARIAVEL!")
                else:
                    print("   >>> Erro da variavel corrigido, mas existe outro problema")
            
    except subprocess.TimeoutExpired:
        print("   TIMEOUT: Script levou muito tempo para executar")
    except Exception as e:
        print(f"   ERRO: {e}")
    
    print("\n" + "="*50)
    print("TESTE CONCLUIDO")

if __name__ == "__main__":
    testar_correcao_erro()
