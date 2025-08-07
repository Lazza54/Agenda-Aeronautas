import tkinter as tk
from tkinter import filedialog, messagebox
import re

def escolher_arquivo():
    # armazenar na variável diretorio_arquivo o endereço que está selecionado
    diretorio_arquivo = filedialog.askdirectory()
    
    """
    if diretorio_arquivo: 
        messagebox.showinfo("Diretório Selecionado", f"Diretório: {diretorio_arquivo}")
    else:
        messagebox.showwarning("Nenhum diretório selecionado", "Por favor, selecione um diretório.")
    """ 
    nome_arquivo = filedialog.askopenfilename(title="Selecione um arquivo")
    
    """
    if caminho_arquivo:
        messagebox.showinfo("Arquivo Selecionado", f"Caminho: {caminho_arquivo}")
    else:
        messagebox.showwarning("Nenhum arquivo selecionado", "Por favor, selecione um arquivo.")
    """
    
    return nome_arquivo, diretorio_arquivo
    
    
# Criando a janela principal
root = tk.Tk()
root.withdraw()  # Oculta a janela principal

# Chama a função para escolher o arquivo e armazena o caminho do arquivo selecionado
nome_arquivo, diretorio_arquivo = escolher_arquivo()
#nome_arquivo = nome_arquivo.split("/")[-1]

# Extrair o nome do aeronauta
#file_path = path
file_path = nome_arquivo

match = re.search(r'-\s*(.*?)\s*\(', file_path)
extracted_text = match.group(1) if match else "Texto não encontrado"

#23638 - GABRIEL DAGLI LAZZARINI PORTELLA  ( 05-08-2019 - 01-04-2024 ) -_CALCULOS_EM_TIMEDELTA


#print("Nome do arquivo selecionado:", nome_arquivo) 
print("CAMINHO DO ARQUIVO SELECIONADO:", nome_arquivo)

# utilizar o caminho do arquivo selecionado para abrir e gravar o arquivo alterando o nome do arquivo
print("Aqui você pode abrir e gravar o arquivo com o caminho:", nome_arquivo)

# em nome_arquivo a partir do primeiro ( substituir tudo por '_HORAS JORNADA'
nome_arquivo = nome_arquivo.split("(")[0] + "_com tempos calculados.csv"
print("Nome do arquivo alterado:", nome_arquivo)

print("O DIRETÓRIO A SER UTILIZADO É:", diretorio_arquivo)

print('='*50)

arq = diretorio_arquivo + '/' + nome_arquivo 
print("O ARQUIVO SERÁ GRAVADO COM O NOME:", arq)

# apenas gravar o arquivo com o nome alterado

 