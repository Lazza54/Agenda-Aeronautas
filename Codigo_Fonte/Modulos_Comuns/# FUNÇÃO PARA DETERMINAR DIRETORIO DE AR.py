# FUNÇÃO PARA DETERMINAR DIRETORIO DE ARQUIVO E NOME DO ARQUIVO A SER UTILIZADO
import os
import tkinter as tk
from tkinter import messagebox, filedialog

def selecionar_diretorio():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    
    messagebox.showinfo("Seleção de Diretório", "Selecione o diretório onde estão os arquivos necessários - ddd.")

    path = filedialog.askdirectory()
    return path

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal

    messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo que deseja importar - aaa.")
    root.update()

    path = filedialog.askopenfilename()
    return path

diretorio_path = selecionar_diretorio()
print(f"📂 Diretório selecionado com sucesso! {diretorio_path}")

arquivo_path = selecionar_arquivo()
print(f"📄 Arquivo selecionado com sucesso! {arquivo_path}")

# extrair o nome do arquivo 
nome_arquivo = os.path.basename(arquivo_path)
print(f"Nome do arquivo selecionado: {nome_arquivo}")

# extrair do nome_arquivo o que estiver até o segundo '_' descartando esse valor
# Exemplo: '2023_10_01_Escala_Simplificada.pdf' -> '2023_10'
# Se não houver segundo '_', manter o nome original

# nome_arquivo = nome_arquivo.replace('.pdf', '.txt')  # substitui a extensão .pdf por .txt
nome_arquivo = nome_arquivo.replace('.pdf', '_PRIMEIRA_VERSAO.csv')

print(f"Nome do arquivo modificado: {nome_arquivo}")

def gravar_arquivo(diretorio_path, nome_arquivo, conteudo):
    if not os.path.exists(diretorio_path):
        os.makedirs(diretorio_path)
    
    caminho_completo = os.path.join(diretorio_path, nome_arquivo)
    
    with open(caminho_completo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(conteudo)
    
    print(f"Arquivo gravado com sucesso em: {caminho_completo}")
    return caminho_completo

# Exemplo de uso da função gravar_arquivo

diretorio_path = diretorio_path.replace('Escalas_Executadas', 'Auditoria_Calculos')

# chamar a função gravar_arquivo
conteudo_exemplo = "Este é um exemplo de conteúdo para o arquivo."
caminho_arquivo_gravado = gravar_arquivo(diretorio_path, nome_arquivo, conteudo_exemplo)

#, "exemplo.txt", conteudo_exemplo)
# %%
# FIM DA FUNÇÃO PARA DETERMINAR DIRETORIO DE ARQUIVO E NOME DO ARQUIVO A SER UTILIZADO
# %%
# IMPORTAÇÃO DO PDF ORIGINAL ESCALA SIMPLIFICADA - FINAL
