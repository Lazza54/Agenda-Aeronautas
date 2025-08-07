# chamar a função para escolher o diretorio
diretorio = escolher_diretorio()
if diretorio:
    print(f"✅ Diretório selecionado: {diretorio}")
else:
    print("⚠️ Nenhum diretório foi selecionado")

# chamar a função para escolher os arquivos csv
arquivos = escolher_arquivos()

# verificar se os arquivos foram escolhidos
if arquivos is None or len(arquivos) == 0:
    print("❌ Nenhum arquivo foi selecionado.")
    print("💡 Dica: Execute a célula novamente e selecione exatamente 2 arquivos CSV")
elif len(arquivos) != 2:
    print(f"⚠️ Foram selecionados {len(arquivos)} arquivos. Por favor, selecione exatamente 2 arquivos CSV.")
    print("💡 Execute a célula novamente e selecione apenas 2 arquivos")
else:
    print(f"✅ Exatos 2 arquivos selecionados!")
    
    # mostrar os arquivos selecionados
    arquivo1 = arquivos[0]
    arquivo2 = arquivos[1]
    print(f"1. {arquivo1.split('\\')[-1]}")
    print(f"2. {arquivo2.split('\\')[-1]}")
    
    print("\n📂 Carregando os arquivos...")
    
    def carregar_arquivo_robusto(caminho_arquivo):
        """
        Tenta carregar o arquivo com diferentes encodings
        """
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(caminho_arquivo, sep=',', encoding=encoding)
                print(f"✅ Arquivo carregado com encoding: {encoding}")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"⚠️ Erro com encoding {encoding}: {e}")
                continue
        
        # Se todos os encodings falharam, tentar com engine='python'
        try:
            df = pd.read_csv(caminho_arquivo, sep=',', encoding='utf-8', engine='python')
            print("✅ Arquivo carregado com engine='python'")
            return df
        except Exception as e:
            print(f"❌ Falha ao carregar arquivo: {e}")
            return None
    
    try:
        # carregar o primeiro arquivo
        print("🔄 Carregando arquivo 1...")
        df1 = carregar_arquivo_robusto(arquivo1)
        nome_arquivo1 = arquivo1.split('\\')[-1]
        
        if df1 is not None:
            print(f"✅ Arquivo 1 carregado: {nome_arquivo1} - Shape: {df1.shape}")
        else:
            print(f"❌ Falha ao carregar arquivo 1: {nome_arquivo1}")
            df1 = None
        
        # carregar o segundo arquivo
        print("🔄 Carregando arquivo 2...")
        df2 = carregar_arquivo_robusto(arquivo2)
        nome_arquivo2 = arquivo2.split('\\')[-1]
        
        if df2 is not None:
            print(f"✅ Arquivo 2 carregado: {nome_arquivo2} - Shape: {df2.shape}")
        else:
            print(f"❌ Falha ao carregar arquivo 2: {nome_arquivo2}")
            df2 = None
        
        # Exibir informações apenas se ambos os arquivos foram carregados
        if df1 is not None and df2 is not None:
            print("\n" + "="*60)
            print(f"📊 DISPLAY DO PRIMEIRO ARQUIVO: {nome_arquivo1}")
            print("="*60)
            print(f"🔹 Colunas ({len(df1.columns)}): {list(df1.columns)}")
            print(f"🔹 Primeiras 5 linhas:")
            try:
                display(df1.head())
            except:
                print(df1.head())
            
            print("\n" + "="*60)
            print(f"📊 DISPLAY DO SEGUNDO ARQUIVO: {nome_arquivo2}")
            print("="*60)
            print(f"🔹 Colunas ({len(df2.columns)}): {list(df2.columns)}")
            print(f"🔹 Primeiras 5 linhas:")
            try:
                display(df2.head())
            except:
                print(df2.head())
            
            # informações detalhadas usando info()
            print("\n📊 INFORMAÇÕES DETALHADAS DO ARQUIVO 1:")
            print(f"🔹 {nome_arquivo1}")
            try:
                df1.info(verbose=True)
            except Exception as e:
                print(f"⚠️ Erro ao exibir info do arquivo 1: {e}")
                print(f"📊 Resumo básico: {df1.shape[0]} linhas, {df1.shape[1]} colunas")
            
            print("\n📊 INFORMAÇÕES DETALHADAS DO ARQUIVO 2:")
            print(f"🔹 {nome_arquivo2}")
            try:
                df2.info(verbose=True)
            except Exception as e:
                print(f"⚠️ Erro ao exibir info do arquivo 2: {e}")
                print(f"📊 Resumo básico: {df2.shape[0]} linhas, {df2.shape[1]} colunas")
            
            # resumo rápido da comparação
            print(f"\n🔄 RESUMO COMPARATIVO:")
            print(f"📋 Arquivo 1: {df1.shape[0]:,} linhas x {df1.shape[1]} colunas")
            print(f"📋 Arquivo 2: {df2.shape[0]:,} linhas x {df2.shape[1]} colunas")
            print(f"📊 Diferença: {abs(df1.shape[0] - df2.shape[0]):,} linhas, {abs(df1.shape[1] - df2.shape[1])} colunas")
            
            # Verificar se as colunas são iguais
            colunas_iguais = list(df1.columns) == list(df2.columns)
            print(f"🔗 Colunas idênticas: {'✅ Sim' if colunas_iguais else '❌ Não'}")
            
            if not colunas_iguais:
                print("🔍 Diferenças nas colunas:")
                colunas_df1 = set(df1.columns)
                colunas_df2 = set(df2.columns)
                
                apenas_df1 = colunas_df1 - colunas_df2
                apenas_df2 = colunas_df2 - colunas_df1
                
                if apenas_df1:
                    print(f"   📋 Apenas no arquivo 1: {list(apenas_df1)}")
                if apenas_df2:
                    print(f"   📋 Apenas no arquivo 2: {list(apenas_df2)}")
            
            print("\n✅ PROCESSAMENTO CONCLUÍDO!")
            
        else:
            print("❌ Não foi possível carregar um ou ambos os arquivos.")
            
    except Exception as e:
        print(f"❌ Erro geral no processamento: {e}")
        import traceback
        traceback.print_exc()

# 📁 ORGANIZAÇÃO DOS ARQUIVOS GERADOS
print("📁 ORGANIZAÇÃO DOS ARQUIVOS GERADOS")
print("="*60)

import os
import shutil
from datetime import datetime

# Verificar se a estrutura de pastas existe
base_dir = "g:/PROJETOS PYTHON/aeronautas_azul"
estrutura_pastas = {
    "logs": os.path.join(base_dir, "RESULTADOS", "logs"),
    "relatorios": os.path.join(base_dir, "RESULTADOS", "relatorios"),
    "arquivos_padronizados": os.path.join(base_dir, "RESULTADOS", "arquivos_padronizados"),
    "codigos": os.path.join(base_dir, "CODIGOS GERADOS", "analises")
}

# Criar pastas se não existirem
print("🏗️ Verificando estrutura de pastas...")
for nome, caminho in estrutura_pastas.items():
    if not os.path.exists(caminho):
        try:
            os.makedirs(caminho, exist_ok=True)
            print(f"✅ Criada: {nome} -> {caminho}")
        except Exception as e:
            print(f"❌ Erro ao criar {nome}: {e}")
    else:
        print(f"✅ Existe: {nome} -> {caminho}")

print("\n📋 MAPEAMENTO DOS ARQUIVOS PARA ORGANIZAR:")

# Definir mapeamento dos arquivos
arquivos_mover = {
    # Arquivos de log -> pasta logs
    "logs": [
        "log.csv",
        "log_jornadas.csv", 
        "log_repouso.csv",
        "log_repousoextra.csv"
    ],
    
    # Relatórios de comparação -> pasta relatorios
    "relatorios": [
        "relatorio_comparacao_colunas_*.csv",
        "relatorio_comparacao_colunas_*.xlsx",
        "relatorio_comparacao_colunas_*.json",
        "relatorio_comparacao_colunas_*_resumo.txt"
    ],
    
    # Arquivos padronizados -> pasta arquivos_padronizados
    "arquivos_padronizados": [
        "arquivo1_padronizado.csv",
        "arquivo2_padronizado.csv",
        "*_CALCULOS_EM_TIMEDELTA.csv",
        "*_padronizado.csv"
    ]
}

# Função para encontrar arquivos com padrão
def encontrar_arquivos_padrao(padrao):
    """Encontra arquivos que correspondem ao padrão"""
    import glob
    return glob.glob(padrao)

# Função para mover arquivo com timestamp
def mover_arquivo_com_backup(origem, destino_pasta, nome_arquivo):
    """Move arquivo para pasta de destino, criando backup se já existir"""
    destino_completo = os.path.join(destino_pasta, nome_arquivo)
    
    try:
        # Se arquivo já existe no destino, criar backup
        if os.path.exists(destino_completo):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_base, extensao = os.path.splitext(nome_arquivo)
            backup_nome = f"{nome_base}_backup_{timestamp}{extensao}"
            backup_caminho = os.path.join(destino_pasta, backup_nome)
            shutil.move(destino_completo, backup_caminho)
            print(f"   📦 Backup criado: {backup_nome}")
        
        # Mover arquivo
        shutil.move(origem, destino_completo)
        return True, destino_completo
        
    except Exception as e:
        return False, str(e)

# Processar cada categoria de arquivos
print("\n🔄 MOVENDO ARQUIVOS...")

arquivos_movidos = []
arquivos_nao_encontrados = []
erros_movimento = []

for categoria, lista_arquivos in arquivos_mover.items():
    pasta_destino = estrutura_pastas[categoria]
    
    print(f"\n📂 Categoria: {categoria.upper()}")
    print(f"   Destino: {pasta_destino}")
    
    for padrao_arquivo in lista_arquivos:
        if '*' in padrao_arquivo:
            # Arquivo com padrão
            arquivos_encontrados = encontrar_arquivos_padrao(padrao_arquivo)
            
            if arquivos_encontrados:
                print(f"   🔍 Padrão '{padrao_arquivo}': {len(arquivos_encontrados)} arquivo(s)")
                
                for arquivo_completo in arquivos_encontrados:
                    nome_arquivo = os.path.basename(arquivo_completo)
                    
                    if os.path.exists(arquivo_completo):
                        sucesso, resultado = mover_arquivo_com_backup(arquivo_completo, pasta_destino, nome_arquivo)
                        
                        if sucesso:
                            print(f"      ✅ {nome_arquivo} -> movido")
                            arquivos_movidos.append({
                                'arquivo': nome_arquivo,
                                'categoria': categoria,
                                'destino': resultado
                            })
                        else:
                            print(f"      ❌ {nome_arquivo} -> erro: {resultado}")
                            erros_movimento.append({
                                'arquivo': nome_arquivo,
                                'erro': resultado
                            })
            else:
                print(f"   ⚠️ Padrão '{padrao_arquivo}': nenhum arquivo encontrado")
                arquivos_nao_encontrados.append(padrao_arquivo)
        
        else:
            # Arquivo específico
            if os.path.exists(padrao_arquivo):
                sucesso, resultado = mover_arquivo_com_backup(padrao_arquivo, pasta_destino, padrao_arquivo)
                
                if sucesso:
                    print(f"   ✅ {padrao_arquivo} -> movido")
                    arquivos_movidos.append({
                        'arquivo': padrao_arquivo,
                        'categoria': categoria,
                        'destino': resultado
                    })
                else:
                    print(f"   ❌ {padrao_arquivo} -> erro: {resultado}")
                    erros_movimento.append({
                        'arquivo': padrao_arquivo,
                        'erro': resultado
                    })
            else:
                print(f"   ⚠️ {padrao_arquivo} -> não encontrado")
                arquivos_nao_encontrados.append(padrao_arquivo)

# Relatório final
print("\n" + "="*60)
print("📊 RELATÓRIO FINAL DA ORGANIZAÇÃO")
print("="*60)

print(f"\n✅ ARQUIVOS MOVIDOS COM SUCESSO: {len(arquivos_movidos)}")
if arquivos_movidos:
    for item in arquivos_movidos:
        print(f"   📄 {item['arquivo']} -> {item['categoria']}")
        print(f"      📂 {item['destino']}")

print(f"\n⚠️ ARQUIVOS NÃO ENCONTRADOS: {len(arquivos_nao_encontrados)}")
if arquivos_nao_encontrados:
    for arquivo in arquivos_nao_encontrados:
        print(f"   📄 {arquivo}")

print(f"\n❌ ERROS NO MOVIMENTO: {len(erros_movimento)}")
if erros_movimento:
    for item in erros_movimento:
        print(f"   📄 {item['arquivo']}: {item['erro']}")

# Verificar arquivos restantes no diretório atual
print(f"\n📂 ARQUIVOS RESTANTES NO DIRETÓRIO ATUAL:")
arquivos_atuais = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(('.csv', '.xlsx', '.json', '.txt'))]

if arquivos_atuais:
    print("   Arquivos que podem precisar de organização manual:")
    for arquivo in arquivos_atuais:
        tamanho = os.path.getsize(arquivo)
        print(f"   📄 {arquivo} ({tamanho} bytes)")
else:
    print("   🎉 Nenhum arquivo de trabalho restante!")

# Criar índice dos arquivos organizados
print(f"\n📋 CRIANDO ÍNDICE DOS ARQUIVOS ORGANIZADOS...")

indice_organizacao = {
    'data_organizacao': datetime.now().isoformat(),
    'total_movidos': len(arquivos_movidos),
    'total_erros': len(erros_movimento),
    'total_nao_encontrados': len(arquivos_nao_encontrados),
    'estrutura_pastas': estrutura_pastas,
    'arquivos_movidos': arquivos_movidos,
    'erros': erros_movimento,
    'nao_encontrados': arquivos_nao_encontrados
}

# Salvar índice
import json
indice_path = os.path.join(estrutura_pastas['relatorios'], 'indice_organizacao.json')
try:
    with open(indice_path, 'w', encoding='utf-8') as f:
        json.dump(indice_organizacao, f, indent=2, ensure_ascii=False)
    print(f"✅ Índice salvo: {indice_path}")
except Exception as e:
    print(f"❌ Erro ao salvar índice: {e}")

print(f"\n🎯 ORGANIZAÇÃO CONCLUÍDA!")
print(f"   📊 Total de arquivos organizados: {len(arquivos_movidos)}")
print(f"   📂 Estrutura de pastas: {len(estrutura_pastas)} categorias")
print(f"   📋 Índice completo salvo para referência")

# Mostrar estrutura final
print(f"\n📁 ESTRUTURA FINAL ORGANIZADA:")
for categoria, caminho in estrutura_pastas.items():
    if os.path.exists(caminho):
        arquivos_na_pasta = [f for f in os.listdir(caminho) if os.path.isfile(os.path.join(caminho, f))]
        print(f"   📂 {categoria}: {len(arquivos_na_pasta)} arquivo(s)")
        for arquivo in arquivos_na_pasta[:5]:  # Mostrar apenas os primeiros 5
            print(f"      📄 {arquivo}")
        if len(arquivos_na_pasta) > 5:
            print(f"      ... e mais {len(arquivos_na_pasta) - 5} arquivo(s)")

print(f"\n✅ TODOS OS ARQUIVOS ESTÃO ORGANIZADOS!")