# -*- coding: utf-8 -*-
"""
IMPORTA O PDF ORIGINAL ESCALA SIMPLIFICADA -> CSV

Regra de nome do CSV:
  <nome_do_pdf>_PRIMEIRA_VERSAO.csv  (no diretório de saída)

Saída: por padrão substitui 'Escalas_Executadas' por 'Auditoria_Calculos' no caminho.

Requisitos: Java (para tabula), tabula-py, pandas, tqdm, tkinter
"""

import os
import warnings
import subprocess
from datetime import datetime

import pandas as pd
import tabula
from tabula.io import read_pdf  # noqa: F401
from tqdm import tqdm

import tkinter as tk
from tkinter import messagebox, filedialog

warnings.filterwarnings("ignore")

# --- Java (tabula) ---
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'
os.environ['PATH'] = r'C:\Program Files\Java\jdk-21\bin;' + os.environ.get('PATH', '')

try:
    result = subprocess.run(['java', '-version'], capture_output=True, text=True, shell=True)
    print("   ✅ Java configurado com sucesso" if result.returncode == 0 else "   ⚠️ Aviso: Java pode não estar configurado corretamente")
except Exception as e:
    print(f"   ⚠️ Erro ao verificar Java: {e}")

# =============================================================================
# BLOCO "DEG": seleção de arquivo PDF e geração do nome de saída
# =============================================================================

diretorio_entrada = ""
arquivo_entrada = ""

def selecionar_diretorio_arquivo():
    """Abre diálogo para escolher um PDF; retorna (diretório, arquivo)."""
    global diretorio_entrada, arquivo_entrada
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Seleção de Arquivo", "Selecione o PDF da Escala Simplificada.")
        caminho_completo = filedialog.askopenfilename(
            title="Selecione o PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        if not caminho_completo:
            print("Nenhum arquivo foi selecionado.")
            return None, None
        diretorio_entrada = os.path.dirname(caminho_completo)
        arquivo_entrada = os.path.basename(caminho_completo)
        print(f"📂 Diretório selecionado: {diretorio_entrada}")
        print(f"📄 Arquivo selecionado: {arquivo_entrada}")
        return diretorio_entrada, arquivo_entrada
    finally:
        try:
            root.destroy()
        except:
            pass

def nome_csv_saida_para(pdf_path: str) -> str:
    """<base do PDF>_PRIMEIRA_VERSAO.csv (no diretório calculado de saída)."""
    dir_pdf  = os.path.dirname(pdf_path)
    base_pdf = os.path.splitext(os.path.basename(pdf_path))[0]
    # Regra de pasta de saída igual ao seu script: troca 'Escalas_Executadas' por 'Auditoria_Calculos'
    dir_out = dir_pdf.replace('Escalas_Executadas', 'Auditoria_Calculos')
    os.makedirs(dir_out, exist_ok=True)
    return os.path.join(dir_out, f"{base_pdf}_PRIMEIRA_VERSAO.csv")

# =============================================================================
# Funções auxiliares
# =============================================================================

def _info(msg: str):
    print(msg)
    try:
        messagebox.showinfo("Informação", msg)
    except tk.TclError:
        pass

def _erro(msg: str):
    print("ERRO:", msg)
    try:
        messagebox.showerror("Erro", msg)
    except tk.TclError:
        pass

# =============================================================================
# Pipeline principal
# =============================================================================

def main():
    # 1) Selecionar PDF
    dir_in, arq_in = selecionar_diretorio_arquivo()
    if not (dir_in and arq_in):
        _erro("Nenhum PDF selecionado.")
        return

    arquivo_path = os.path.join(dir_in, arq_in)
    if not arquivo_path.lower().endswith(".pdf"):
        _erro("O arquivo selecionado não é um PDF.")
        return

    # 2) Ler todas as páginas com tabula
    imported_data = tabula.read_pdf(arquivo_path, lattice=True, encoding='utf-8', pages="all")  # lista de DataFrames
    if not imported_data or len(imported_data) == 0:
        _erro("Não foi possível extrair tabelas do PDF (tente 'stream=True' ou verifique o PDF).")
        return

    # 3) Concatenar
    df_merged = imported_data[0]
    for df_to_concat in imported_data[1:]:
        df_merged = pd.concat([df_merged, df_to_concat])

    # 4) Pré-processamento (mesmo do seu script base)
    pd.set_option('display.max_rows', None)
    df_merged.replace(',\r', ' ', regex=True, inplace=True)
    df_merged.replace('\r', ' ', regex=True, inplace=True)
    df_merged.replace(',', ' ', regex=True, inplace=True)

    df_merged.dropna(how='all', inplace=True)
    if 'Activity' in df_merged.columns:
        df_merged['Activity'].fillna('OCULTO', inplace=True)
    df_merged.dropna(thresh=3, inplace=True)
    df_merged.reset_index(drop=True, inplace=True)

    # --- Unir linhas "quebradas" por mudança de página (mantido do seu script) ---
    start_row = 0
    for i in tqdm(range(start_row, len(df_merged)), desc="Processando"):
        if 'Activity' in df_merged.columns and df_merged['Activity'].iloc[i] == 'OCULTO':
            # Guarda tempos da linha 'OCULTO'
            tm  = df_merged['Checkin'].iloc[i]  if 'Checkin'  in df_merged.columns else None
            tm1 = df_merged['Start'].iloc[i]    if 'Start'    in df_merged.columns else None
            tm2 = df_merged['End'].iloc[i]      if 'End'      in df_merged.columns else None
            tm3 = df_merged['Checkout'].iloc[i] if 'Checkout' in df_merged.columns else None

            # Volta uma linha
            i -= 1
            dt  = df_merged['Checkin'].iloc[i]  if 'Checkin'  in df_merged.columns else None
            dt1 = df_merged['Start'].iloc[i]    if 'Start'    in df_merged.columns else None
            dt2 = df_merged['End'].iloc[i]      if 'End'      in df_merged.columns else None
            dt3 = df_merged['Checkout'].iloc[i] if 'Checkout' in df_merged.columns else None

            if 'Checkin' in df_merged.columns and dt is not None and tm is not None:
                df_merged.at[i, 'Checkin'] = f"{dt} {tm}"
            if 'Start' in df_merged.columns and dt1 is not None and tm1 is not None:
                df_merged.at[i, 'Start'] = f"{dt1} {tm1}"
            if 'End' in df_merged.columns and dt2 is not None and tm2 is not None:
                df_merged.at[i, 'End'] = f"{dt2} {tm2}"
            if 'Checkout' in df_merged.columns and dt3 is not None and tm3 is not None:
                df_merged.at[i, 'Checkout'] = f"{dt3} {tm3}"

    df_merged.reset_index(drop=True, inplace=True)

    # Remoções e ajustes
    if 'Activity' in df_merged.columns:
        df_merged.drop(df_merged.loc[df_merged['Activity'] == 'OCULTO'].index, inplace=True)
        df_merged.drop(df_merged.loc[df_merged['Activity'] == 'TOTAL:'].index, inplace=True)

    df_merged.replace('\r', ' ', regex=True, inplace=True)
    df_merged.replace('- nan', '-', regex=True, inplace=True)
    df_merged.reset_index(drop=True, inplace=True)

    # Preenche Checkout vazio com End; em não-voo, Checkin = Start quando Checkin = '-'
    for i in range(len(df_merged)):
        if 'Activity' in df_merged.columns and 'Checkin' in df_merged.columns and 'Start' in df_merged.columns:
            if not str(df_merged.at[i, 'Activity']).startswith('AD') and str(df_merged.at[i, 'Checkin']) == '-':
                df_merged.at[i, 'Checkin'] = df_merged.at[i, 'Start']
        if 'Checkout' in df_merged.columns and 'End' in df_merged.columns:
            if str(df_merged.at[i, 'Checkout']) in ('-', ''):
                df_merged.at[i, 'Checkout'] = df_merged.at[i, 'End']

    df_merged.reset_index(drop=True, inplace=True)

    # Blocos entre checkins definidos: propagar Checkin inicial e Checkout final
    if {'Checkin', 'Checkout'}.issubset(df_merged.columns):
        indices = df_merged.index[df_merged['Checkin'] != '-'].tolist()
        for j in range(len(indices)):
            idx_inicio = indices[j]
            idx_fim = indices[j + 1] if j + 1 < len(indices) else len(df_merged)
            bloco = df_merged.iloc[idx_inicio:idx_fim].copy()
            if bloco.empty:
                continue
            checkin_inicial = bloco.iloc[0]['Checkin']
            checkout_final = bloco.iloc[-1]['Checkout']
            bloco['Checkin'] = bloco['Checkin'].replace('-', checkin_inicial)
            bloco['Checkout'] = checkout_final
            df_merged.iloc[idx_inicio:idx_fim] = bloco.values

    # Conversão de datas (mantida do seu script; compactada)
    def convert_date_column(series, column_name):
        def fix_year_format(date_str):
            if pd.isna(date_str) or date_str == '-':
                return date_str
            s = str(date_str).strip().upper()

            # Normaliza abreviações/meses PT->EN e casos "DEC18" etc.
            repl = {
                'DEC18':'DEC2018','DEZ18':'DEC2018','JAN18':'JAN2018','FEB18':'FEB2018','MAR18':'MAR2018',
                'APR18':'APR2018','MAY18':'MAY2018','JUN18':'JUN2018','JUL18':'JUL2018','AUG18':'AUG2018',
                'SEP18':'SEP2018','OCT18':'OCT2018','NOV18':'NOV2018','FEV18':'FEB2018','ABR18':'APR2018',
                'MAI18':'MAY2018','AGO18':'AUG2018','SET18':'SEP2018','OUT18':'OCT2018'
            }
            for k, v in repl.items():
                s = s.replace(k, v)
            return s

        corrected = series.apply(fix_year_format)

        # Tenta vários formatos específicos
        formats = [
            "%d%b%Y %H:%M", "%d%b%y %H:%M",
            "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M",
            "%d/%m/%y %H:%M",  "%d-%m-%y %H:%M",
        ]

        # começa tudo como NaT (dtype datetime64[ns])
        converted = pd.Series(pd.NaT, index=corrected.index, dtype="datetime64[ns]")

        # somente valores “parseáveis” (não nulos e não '-')
        parse_mask = corrected.notna() & (corrected != '-')

        # aplica cada formato onde ainda está NaT
        for fmt in formats:
            mask = parse_mask & converted.isna()
            if mask.any():
                conv = pd.to_datetime(corrected[mask], format=fmt, errors='coerce')
                converted.loc[mask & conv.notna()] = conv[conv.notna()]

        # PASSO DE SEGURANÇA: tenta parsing genérico (dayfirst) para o que restou
        mask = parse_mask & converted.isna()
        if mask.any():
            conv = pd.to_datetime(corrected[mask], errors='coerce', dayfirst=True)
            converted.loc[mask & conv.notna()] = conv[conv.notna()]

        # === AQUI ESTAVA O PROBLEMA ===
        # Garante dtype datetime64[ns] (mesmo se veio misto)
        converted = pd.to_datetime(converted, errors='coerce', dayfirst=True)

        # Monta a série final: datas formatadas, '-' preservado, demais ficam como estavam
        result = corrected.astype('object')
        ok = converted.notna()
        if ok.any():
            result.loc[ok] = converted.loc[ok].dt.strftime("%d/%m/%Y %H:%M")
        # '-' já está em corrected; demais não parseadas permanecem como texto original

        return result

    for col in ['Checkin','Start','End','Checkout']:
        if col in df_merged.columns:
            print(f"🔄 Convertendo coluna {col}...")
            df_merged[col] = convert_date_column(df_merged[col], col)

    df_merged.reset_index(drop=True, inplace=True)

    # 5) Gravar CSV com regra <pdf>_PRIMEIRA_VERSAO.csv no diretório de saída
    csv_out = nome_csv_saida_para(arquivo_path)
    df_merged.to_csv(csv_out, index=False, encoding="utf-8-sig")

    data_completa = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"✅ TAREFA CONCLUÍDA: {data_completa}")
    print(f"📦 CSV gerado em: {csv_out}")

    try:
        messagebox.showinfo("Concluído", f"CSV gerado em:\n{csv_out}")
    except tk.TclError:
        pass

if __name__ == "__main__":
    main()
