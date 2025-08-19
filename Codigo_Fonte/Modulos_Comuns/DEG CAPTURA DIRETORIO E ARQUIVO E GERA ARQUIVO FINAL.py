import os
from tkinter import filedialog, messagebox
import tkinter as tk

# Variáveis globais para armazenar o diretório e arquivo de entrada
diretorio_entrada = ""
arquivo_entrada = ""
sufixo = 'Apresentacao'

def selecionar_diretorio_arquivo():
    """
    Função para selecionar um arquivo através de uma interface gráfica.
    Armazena o caminho do diretório na variável global 'diretorio_entrada'
    e o nome do arquivo na variável global 'arquivo_entrada'.
    
    Returns:
        tuple: (diretorio_entrada, arquivo_entrada) ou (None, None) se cancelado
    """
    global diretorio_entrada, arquivo_entrada
    
    try:
        # Cria uma janela root oculta
        root = tk.Tk()
        root.withdraw()
        
        # Abre o diálogo para seleção de arquivo
        caminho_completo = filedialog.askopenfilename(
            title="Selecione um arquivo",
            filetypes=[
                ("Todos os arquivos", "*.*"),
                ("Arquivos de texto", "*.txt"),
                ("Arquivos Python", "*.py"),
                ("Arquivos CSV", "*.csv")
            ]
        )
        
        # Verifica se um arquivo foi selecionado
        if caminho_completo:
            # Separa o diretório e o nome do arquivo
            diretorio_entrada = os.path.dirname(caminho_completo)
            arquivo_entrada = os.path.basename(caminho_completo)
            
            print(f"Diretório selecionado: {diretorio_entrada}")
            print(f"Arquivo selecionado: {arquivo_entrada}")
            
            return diretorio_entrada, arquivo_entrada
        else:
            print("Nenhum arquivo foi selecionado.")
            return None, None
            
    except Exception as e:
        print(f"Erro ao selecionar arquivo: {e}")
        return None, None
    finally:
        # Destrói a janela root
        if 'root' in locals():
            root.destroy()

def gera_arquivo_saida(sufixo=None):
    """
    Gera o caminho e nome do arquivo de saída baseado no arquivo de entrada.
    
    A função pega o arquivo de entrada, remove a extensão, substitui tudo após o 
    último '-' por um espaço seguido do sufixo fornecido, e adiciona a extensão original.
    
    Args:
        sufixo (str, optional): Sufixo a ser adicionado após o espaço no nome do arquivo.
                               Se não fornecido, usa a variável global 'sufixo'.
        
    Returns:
        str: Caminho completo do arquivo de saída ou None se não houver arquivo de entrada
        
    Exemplo:
        Se arquivo_entrada = "relatorio-dados-2024.txt" e sufixo = "Apresentacao"
        O resultado será: "relatorio-dados Apresentacao.txt"
    """
    global diretorio_entrada, arquivo_entrada
    
    # Verifica se as variáveis globais estão definidas
    if not diretorio_entrada or not arquivo_entrada:
        print("Erro: Nenhum arquivo de entrada foi selecionado. Execute selecionar_diretorio_arquivo() primeiro.")
        return None
    
    # Se sufixo não foi fornecido, usa a variável global
    if sufixo is None:
        sufixo = globals().get('sufixo', 'Apresentacao')
    
    try:
        # Separa nome do arquivo e extensão
        nome_sem_extensao, extensao = os.path.splitext(arquivo_entrada)
        
        # Encontra a última ocorrência de '-' no nome do arquivo
        if '-' in nome_sem_extensao:
            # Divide o nome no último '-'
            partes = nome_sem_extensao.rsplit('-', 1)
            nome_base = partes[0]
            
            # Constrói o novo nome: nome_base + espaço + sufixo + extensão
            novo_nome = f"{nome_base} {sufixo}{extensao}"
        else:
            # Se não houver '-', apenas adiciona o sufixo com espaço
            novo_nome = f"{nome_sem_extensao} {sufixo}{extensao}"
        
        # Constrói o caminho completo do arquivo de saída
        arquivo_saida = os.path.join(diretorio_entrada, novo_nome)
        
        print(f"Arquivo de saída gerado: {arquivo_saida}")
        return arquivo_saida
        
    except Exception as e:
        print(f"Erro ao gerar arquivo de saída: {e}")
        return None

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo de uso das funções
    print("=== Exemplo de uso ===")
    
    # Seleciona o arquivo
    diretorio, arquivo = selecionar_diretorio_arquivo()
    
    if diretorio and arquivo:
        # Gera arquivo de saída usando o sufixo padrão 'Apresentacao'
        arquivo_saida_padrao = gera_arquivo_saida()
        
        print("\nArquivo de saída gerado:")
        print(f"Arquivo final: {arquivo_saida_padrao}")
    else:
        print("Operação cancelada pelo usuário.")