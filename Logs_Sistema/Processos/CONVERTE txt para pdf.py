import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

# Selecionar o diretório e o arquivo .txt de entrada
def selecionar_arquivo_txt():
    root = tk.Tk()
    root.withdraw()  # Ocultar a janela principal
    arquivo_txt = filedialog.askopenfilename(title="Selecione o arquivo .txt", filetypes=[("Text files", "*.txt")])
    root.destroy()  # Fechar a janela do tkinter
    if arquivo_txt:
        return arquivo_txt
    else:
        return None

# Função para converter .txt para .pdf
def converter_txt_para_pdf(txt_path):
    if not os.path.isfile(txt_path):
        messagebox.showerror("Erro", "Arquivo .txt não encontrado.")
        return
    if not txt_path.endswith('.txt'):
        messagebox.showerror("Erro", "Selecione um arquivo .txt válido.")
        return

    pdf_path = txt_path.replace('.txt', '.pdf')
    pdf_path = pdf_path.replace('REL', 'RELATÓRIO')

    # criar a variavel nome do cabecalho utiliando o pdf_path após o ultimo espaço
    nome_cabecalho = pdf_path.split(' ')[-1].replace('.pdf', '')
    
    # Verificar se o arquivo PDF já existe
    if os.path.isfile(pdf_path):
        resposta = messagebox.askyesno("Arquivo existente", f"O arquivo {pdf_path} já existe. Deseja sobrescrever?")
        if not resposta:
            return  
          
    # Configurar página em paisagem (landscape)
    page_width, page_height = landscape(A4)

    # Criar PDF
    c = canvas.Canvas(pdf_path, pagesize=(page_width, page_height))

    # Definir posição inicial (margem esquerda e topo)
    x = 50  # margem esquerda
    y = page_height - 50  # topo da página

    # Usar fonte monoespaçada
    c.setFont("Courier", 10)  # Fonte monoespaçada para preservar alinhamento

    # Função para imprimir o cabeçalho
    def imprimir_cabecalho():
        nonlocal y
        c.setFont("Courier-Bold", 12)
        c.drawString(x, y, nome_cabecalho)  # Nome do cabeçalho
        y -= 20  # Espaço após o cabeçalho
        c.setFont("Courier", 10)  # Retornar à fonte padrão

    # Ler e armazenar o conteúdo do arquivo
    with open(txt_path, "r", encoding="utf-8") as f:
        conteudo = f.readlines()

    # Gerar o PDF
    y = page_height - 50  # Redefinir posição inicial
    imprimir_cabecalho()  # Imprimir o cabeçalho na primeira página

    for line in conteudo:
        # Verificar se a linha contém o comando de salto de página
        if "\f" in line:  # Detectar o caractere de form feed
            c.showPage()
            y = page_height - 50
            imprimir_cabecalho()
            continue

        if y < 50:  # Nova página se o limite inferior for atingido
            c.showPage()
            y = page_height - 50
            imprimir_cabecalho()

        c.drawString(x, y, line.rstrip())
        y -= 12

    c.save()
    print(f"PDF gerado em: {pdf_path}")
    return pdf_path

# Criar um PDF consolidado com índice e links
def criar_pdf_consolidado_com_links(arquivos_pdf, pdf_saida):
    page_width, page_height = landscape(A4)
    indice_pdf = "indice_temp.pdf"

    # Criar o índice em paisagem
    c = canvas.Canvas(indice_pdf, pagesize=(page_width, page_height))
    c.setFont("Courier-Bold", 14)
    c.drawString(50, page_height - 50, "ÍNDICE DOS ARQUIVOS ANEXADOS")
    c.setFont("Courier", 12)

    y = page_height - 80
    links = []  # Lista para armazenar os links e suas posições
    for i, arquivo in enumerate(arquivos_pdf, start=1):
        nome_arquivo = os.path.basename(arquivo)
        c.drawString(50, y, f"{i}. {nome_arquivo}")
        links.append((nome_arquivo, i, y))  # Armazena o nome, índice e posição Y
        y -= 20
        if y < 50:
            c.showPage()
            y = page_height - 50

    c.save()

    # Consolidar os PDFs
    writer = PdfWriter()
    reader_indice = PdfReader(indice_pdf)
    writer.append(indice_pdf)  # Adicionar o índice como a primeira página

    pagina_atual = len(reader_indice.pages)  # Contar as páginas do índice
    for arquivo in arquivos_pdf:
        reader = PdfReader(arquivo)
        writer.append(arquivo)

        # Adicionar marcador para o relatório
        nome_arquivo = os.path.basename(arquivo).replace('.pdf', '')
        writer.add_outline_item(nome_arquivo, pagina_atual)
        pagina_atual += len(reader.pages)

    # Adicionar links na página de índice
    for i, (nome_arquivo, indice, y) in enumerate(links):
        writer.add_annotation(
            page_number=0,  # Página do índice (primeira página)
            rect=(50, page_height - y - 10, 300, page_height - y + 10),  # Retângulo do link
            uri=None,  # Sem URI, pois é um link interno
            target_page=indice  # Página de destino
        )

    # Salvar o PDF consolidado
    with open(pdf_saida, "wb") as f:
        writer.write(f)

    os.remove(indice_pdf)  # Remover o índice temporário
    print(f"PDF consolidado gerado em: {pdf_saida}")

# Loop para converter vários arquivos
arquivos_gerados = []
while True:
    txt_path = selecionar_arquivo_txt()
    if txt_path:
        pdf_gerado = converter_txt_para_pdf(txt_path)
        if pdf_gerado:
            arquivos_gerados.append(pdf_gerado)
        continuar = messagebox.askyesno("Continuar", "Deseja converter outro arquivo?")
        if not continuar:
            break
    else:
        break

# Verificar se há arquivos gerados para consolidar
if arquivos_gerados:
    pdf_saida = filedialog.asksaveasfilename(
        title="Salvar PDF consolidado",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if pdf_saida:
        criar_pdf_consolidado_com_links(arquivos_gerados, pdf_saida)
        print("PDF consolidado gerado com sucesso.")
else:
    print("Nenhum arquivo foi gerado para consolidar.")

print("Processo concluído.")

