"""
Teste rápido da versão Windows do CALCULOS FINAIS
"""

import subprocess
import sys
import os

def testar_versao_windows():
    script = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL - WINDOWS.py"
    
    print("TESTE DA VERSAO WINDOWS")
    print("="*50)
    
    if not os.path.exists(script):
        print("ERRO: Script nao encontrado")
        return
    
    print("Iniciando teste com timeout de 2 minutos...")
    print("Pressione Ctrl+C para interromper")
    print("-" * 50)
    
    try:
        # Testar apenas o início do script
        resultado = subprocess.run(
            [sys.executable, "-c", f"exec(open(r'{script}').read())"],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutos
            encoding='utf-8',
            errors='replace'
        )
        
        print("RESULTADO:")
        print(f"Codigo retorno: {resultado.returncode}")
        
        if resultado.stdout:
            print("SAIDA:")
            print(resultado.stdout[-1000:])  # Últimos 1000 chars
        
        if resultado.stderr:
            print("ERROS:")
            print(resultado.stderr[-500:])   # Últimos 500 chars
            
    except subprocess.TimeoutExpired:
        print("TIMEOUT atingido - script pode estar funcionando ou travado")
    except KeyboardInterrupt:
        print("Interrompido pelo usuario")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    testar_versao_windows()
