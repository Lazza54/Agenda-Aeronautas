import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd

class FiltroCSVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filtro de Planilha CSV")
        self.df = None

        # Botão para carregar arquivo
        self.botao_carregar = tk.Button(root, text="Carregar CSV", command=self.carregar_csv)
        self.botao_carregar.pack(pady=10)

        # Label e Combobox para selecionar coluna
        tk.Label(root, text="Selecione a coluna:").pack(pady=(10,0))
        self.coluna_var = tk.StringVar()
        self.combo_colunas = ttk.Combobox(root, textvariable=self.coluna_var, state="readonly")
        self.combo_colunas.pack(pady=5)

        # Label e Combobox para selecionar valor
        tk.Label(root, text="Selecione o valor para filtrar:").pack(pady=(10,0))
        self.valor_var = tk.StringVar()
        self.combo_valores = ttk.Combobox(root, textvariable=self.valor_var, state="readonly")
        self.combo_valores.pack(pady=5)

        # Botão para aplicar filtro
        self.botao_filtrar = tk.Button(root, text="Aplicar Filtro", command=self.aplicar_filtro)
        self.botao_filtrar.pack(pady=5)
        
        # Botão para limpar filtro
        self.botao_limpar = tk.Button(root, text="Limpar Filtro", command=self.limpar_filtro)
        self.botao_limpar.pack(pady=5)

        # Tabela para mostrar resultados
        self.tabela = ttk.Treeview(root)
        self.tabela.pack(expand=True, fill="both", padx=10, pady=10)

        # Atualiza valores ao mudar coluna
        self.combo_colunas.bind("<<ComboboxSelected>>", self.atualizar_valores)

    def carregar_csv(self):
        caminho = filedialog.askopenfilename(
            title="Selecione um arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
        if caminho:
            try:
                # Tentar diferentes encodings para arquivos CSV brasileiros
                try:
                    self.df = pd.read_csv(caminho, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        self.df = pd.read_csv(caminho, encoding='latin-1')
                    except UnicodeDecodeError:
                        self.df = pd.read_csv(caminho, encoding='cp1252')
                
                self.combo_colunas['values'] = list(self.df.columns)
                self.combo_colunas.set('')
                self.combo_valores.set('')
                self.tabela.delete(*self.tabela.get_children())
                
                # Mostrar informações do arquivo carregado
                total_linhas = len(self.df)
                total_colunas = len(self.df.columns)
                messagebox.showinfo(
                    "Sucesso", 
                    f"Arquivo CSV carregado com sucesso!\n"
                    f"Linhas: {total_linhas:,}\n"
                    f"Colunas: {total_colunas}"
                )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo CSV: {e}")

    def atualizar_valores(self, event=None):
        coluna = self.coluna_var.get()
        if self.df is not None and coluna:
            valores_unicos = sorted(self.df[coluna].dropna().unique())
            self.combo_valores['values'] = valores_unicos
            self.combo_valores.set('')

    def aplicar_filtro(self):
        coluna = self.coluna_var.get()
        valor = self.valor_var.get()
        
        if self.df is None:
            messagebox.showwarning("Aviso", "Por favor, carregue um arquivo CSV primeiro!")
            return
            
        if not coluna:
            messagebox.showwarning("Aviso", "Por favor, selecione uma coluna!")
            return
            
        if not valor:
            messagebox.showwarning("Aviso", "Por favor, selecione um valor!")
            return
            
        try:
            df_filtrado = self.df[self.df[coluna] == valor]
            total_filtrado = len(df_filtrado)
            total_original = len(self.df)
            
            if total_filtrado == 0:
                messagebox.showinfo(
                    "Resultado", 
                    f"Nenhum registro encontrado para:\n"
                    f"Coluna: {coluna}\n"
                    f"Valor: {valor}"
                )
            else:
                messagebox.showinfo(
                    "Resultado", 
                    f"Filtro aplicado com sucesso!\n"
                    f"Registros encontrados: {total_filtrado:,}\n"
                    f"Total original: {total_original:,}\n"
                    f"Percentual: {total_filtrado/total_original*100:.1f}%"
                )
                
            self.exibir_resultado(df_filtrado)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar filtro: {e}")

    def limpar_filtro(self):
        """Remove o filtro e mostra todos os dados"""
        if self.df is not None:
            self.combo_colunas.set('')
            self.combo_valores.set('')
            self.exibir_resultado(self.df)
            messagebox.showinfo("Info", "Filtro removido. Mostrando todos os dados.")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo carregado!")

    def exibir_resultado(self, df):
        """Exibe o DataFrame na tabela, limitando a 1000 linhas para performance"""
        self.tabela.delete(*self.tabela.get_children())
        
        if df.empty:
            return
            
        # Limitar a 1000 linhas para performance
        max_linhas = 1000
        df_exibir = df.head(max_linhas)
        
        # Configurar colunas
        self.tabela["columns"] = list(df_exibir.columns)
        self.tabela["show"] = "headings"
        
        # Configurar cabeçalhos e largura das colunas
        for col in df_exibir.columns:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=120, minwidth=80)
        
        # Inserir dados
        for _, row in df_exibir.iterrows():
            # Converter valores NaN para string vazia
            valores = [str(val) if pd.notna(val) else "" for val in row]
            self.tabela.insert("", "end", values=valores)
        
        # Mostrar aviso se há mais dados
        if len(df) > max_linhas:
            messagebox.showinfo(
                "Informação",
                f"Mostrando apenas as primeiras {max_linhas:,} linhas.\n"
                f"Total de registros: {len(df):,}"
            )

# Executar a interface
root = tk.Tk()
root.geometry("1000x600")  # Tamanho inicial da janela
app = FiltroCSVApp(root)
root.mainloop()