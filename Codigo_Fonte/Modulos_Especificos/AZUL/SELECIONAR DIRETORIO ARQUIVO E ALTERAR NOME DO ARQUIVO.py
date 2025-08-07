import os
import tkinter as tk
from tkinter import filedialog

# Criar janela Tkinter oculta
root = tk.Tk()
root.withdraw()

def selecionar_arquivo():
    # 1. Selecionar diretório e armazenar na variável
    diretorio = filedialog.askdirectory(title="Selecione um diretório")
    if not diretorio:
        print("Nenhum diretório selecionado.")
        exit()

    # 2. Selecionar arquivo no diretório escolhido
    arquivo_path = filedialog.askopenfilename(initialdir=diretorio, title="Selecione um arquivo")
    if not arquivo_path:
        print("Nenhum arquivo selecionado.")
        exit()

    # Extrair nome do arquivo
    nome_arquivo = os.path.basename(arquivo_path)

    return diretorio, nome_arquivo

######################################

def gravar_arquivo(nome_arquivo, diretorio):
    # 3. Substituir tudo após ')' no nome do arquivo por "novo nome"
    novo_nome = nome_arquivo.split(")")[0] + ") - novo nome" #+ os.path.splitext(nome_arquivo)[1]

    # Exibir resultados
    print(f"Diretório selecionado: {diretorio}")
    print(f"Arquivo original: {nome_arquivo}")
    print(f"Novo nome do arquivo: {novo_nome}")

# Chamar a função selecionar_arquivo e armazenar os retornos
diretorio, nome_arquivo = selecionar_arquivo()

# Passar os valores retornados para a função gravar_arquivo
gravar_arquivo(nome_arquivo, diretorio)