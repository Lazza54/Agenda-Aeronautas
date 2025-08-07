"""
Script para testar a versão corrigida do CALCULOS FINAIS com indicadores de progresso
Vai monitorar se o script executa corretamente e onde pode estar travando
"""

import subprocess
import os
import sys
import time
import threading
from datetime import datetime

def monitor_execucao():
    """Monitora a execução do script principal"""
    
    script_principal = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL - COM PROGRESSO.py"
    
    if not os.path.exists(script_principal):
        print(f"❌ Script não encontrado: {script_principal}")
        return
    
    print("🔄 TESTANDO VERSÃO CORRIGIDA COM INDICADORES DE PROGRESSO")
    print("="*70)
    print(f"📄 Script: {os.path.basename(script_principal)}")
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    # Opções de teste
    print("\\nEscolha o tipo de teste:")
    print("1 - Execução completa (pode demorar)")
    print("2 - Execução com timeout de 5 minutos")
    print("3 - Execução interativa (você pode parar manualmente)")
    
    escolha = input("\\nDigite sua escolha (1-3): ").strip()
    
    timeout = None
    if escolha == "2":
        timeout = 300  # 5 minutos
    
    print(f"\\n🚀 Iniciando teste...")
    print("💡 Observe os indicadores de progresso para identificar onde pode travar")
    print("⚠️ Pressione Ctrl+C para interromper se necessário")
    print("-" * 70)
    
    try:
        # Executar o script
        if timeout:
            processo = subprocess.Popen(
                [sys.executable, script_principal],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitorar com timeout
            try:
                stdout, stderr = processo.communicate(timeout=timeout)
                codigo_retorno = processo.returncode
                
                print("\\n" + "="*70)
                print("✅ EXECUÇÃO CONCLUÍDA DENTRO DO TIMEOUT")
                print(f"🔢 Código de retorno: {codigo_retorno}")
                
                if stdout:
                    print("\\n📤 SAÍDA PADRÃO:")
                    print(stdout[-2000:])  # Últimas 2000 chars
                
                if stderr:
                    print("\\n❌ ERROS:")
                    print(stderr[-1000:])  # Últimos 1000 chars
                    
            except subprocess.TimeoutExpired:
                processo.kill()
                print("\\n" + "="*70)
                print(f"⏰ TIMEOUT DE {timeout}s ATINGIDO - PROCESSO INTERROMPIDO")
                print("🔍 O script pode estar travado em algum ponto")
                print("💡 Use o script de investigação para identificar o problema")
                
        else:
            # Execução normal
            resultado = subprocess.run(
                [sys.executable, script_principal],
                capture_output=True,
                text=True
            )
            
            print("\\n" + "="*70)
            print("✅ EXECUÇÃO CONCLUÍDA")
            print(f"🔢 Código de retorno: {resultado.returncode}")
            
            if resultado.stdout:
                print("\\n📤 SAÍDA PADRÃO:")
                print(resultado.stdout[-2000:])  # Últimas 2000 chars
            
            if resultado.stderr:
                print("\\n❌ ERROS:")
                print(resultado.stderr[-1000:])  # Últimos 1000 chars
    
    except KeyboardInterrupt:
        print("\\n\\n⚠️ EXECUÇÃO INTERROMPIDA PELO USUÁRIO")
    except Exception as e:
        print(f"\\n❌ ERRO DURANTE EXECUÇÃO: {e}")
    
    print("\\n" + "="*70)
    print(f"⏰ Fim: {datetime.now().strftime('%H:%M:%S')}")
    print("📋 TESTE CONCLUÍDO")
    print("="*70)

def verificar_estrutura_arquivo():
    """Verifica se o arquivo tem as correções aplicadas"""
    
    script_principal = r"g:\PROJETOS PYTHON\aeronautas_azul\CODIGOS TERMINADOS\CALCULOS FINAIS - FINAL - COM PROGRESSO.py"
    
    print("🔍 VERIFICANDO CORREÇÕES APLICADAS")
    print("="*50)
    
    try:
        with open(script_principal, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar se tem indicadores de progresso
        tem_progresso = "mostrar_progresso_etapa" in conteudo
        print(f"✅ Indicadores de progresso: {'SIM' if tem_progresso else 'NÃO'}")
        
        # Verificar se a variável foi corrigida
        tem_erro_variavel = "atividades_excluidos" in conteudo
        print(f"✅ Erro de variável corrigido: {'NÃO' if tem_erro_variavel else 'SIM'}")
        
        # Verificar se tem imports necessários
        tem_time = "import time" in conteudo
        print(f"✅ Import time adicionado: {'SIM' if tem_time else 'NÃO'}")
        
        # Contar indicadores de progresso
        count_progresso = conteudo.count("mostrar_progresso_etapa")
        print(f"📊 Número de indicadores encontrados: {count_progresso}")
        
        if tem_progresso and not tem_erro_variavel and tem_time:
            print("\\n✅ ARQUIVO PARECE ESTAR CORRIGIDO")
        else:
            print("\\n⚠️ ARQUIVO PODE PRECISAR DE MAIS CORREÇÕES")
            
    except Exception as e:
        print(f"❌ Erro ao verificar arquivo: {e}")
    
    print("="*50)

if __name__ == "__main__":
    print("🧪 TESTE DO CALCULOS FINAIS CORRIGIDO")
    print("="*50)
    
    # Primeiro verificar se as correções estão aplicadas
    verificar_estrutura_arquivo()
    
    print("\\n")
    continuar = input("Deseja continuar com o teste de execução? (s/n): ").strip().lower()
    
    if continuar in ['s', 'sim', 'y', 'yes']:
        monitor_execucao()
    else:
        print("🛑 Teste cancelado pelo usuário")
