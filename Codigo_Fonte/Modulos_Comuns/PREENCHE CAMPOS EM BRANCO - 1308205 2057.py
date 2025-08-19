# -*- coding: utf-8 -*-
"""
PREENCHE CAMPOS EM BRANCO - FINAL (VERSAO 2.2)
----------------------------------------------
- Funciona mesmo com espaços/acentos no caminho.
- Abre diálogos para selecionar arquivo de ENTRADA e pasta de SAÍDA.
- Lê CSV (autodetect delimitador) e Excel (.xlsx/.xls).
- Limpa espaços, converte marcadores de vazio em NaN.
- Preenche:
    * Todas as colunas, EXCETO 'Checkout': ffill + bfill.
    * 'Checkout': primeiro preenche NaN com o PRÓXIMO valor válido (bfill);
      se restar NaN (no fim da coluna), preenche com o valor válido anterior (ffill).
      Resultado: nenhum NaN em 'Checkout'.
- Padroniza datas/horas nas colunas: Checkin, Start, End, Checkout.
- Salva no mesmo tipo da entrada (CSV => CSV; Excel => XLSX).

Requisitos: pandas, numpy, (openpyxl para .xlsx).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional

# ===== Caminho do script e CWD fixado na pasta do script =====
SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parent
os.chdir(ROOT)

# ===== Dependências de dados =====
import pandas as pd
import numpy as np


# =========================
# Impressão segura (evita UnicodeEncodeError no Windows)
# =========================
def safe_print(*args) -> None:
    """Imprime com fallback de encoding para evitar UnicodeEncodeError no Windows."""
    text = " ".join(str(a) for a in args)
    try:
        print(text)
    except UnicodeEncodeError:
        enc = (getattr(sys.stdout, "encoding", None) or "utf-8")
        try:
            sys.stdout.buffer.write((text + "\n").encode(enc, errors="replace"))
        except Exception:
            # Último fallback
            sys.stdout.write(text.encode(errors="replace").decode() + "\n")


# =========================
# Utilitários de interface
# =========================
def escolher_arquivo(titulo="Selecione o arquivo de entrada") -> Optional[Path]:
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    tipos = (
        ("CSV", "*.csv"),
        ("Excel", "*.xlsx;*.xls"),
        ("Todos", "*.*"),
    )
    caminho = filedialog.askopenfilename(
        title=titulo,
        initialdir=str(ROOT),
        filetypes=tipos,
    )
    if not caminho:
        messagebox.showwarning("Aviso", "Nenhum arquivo selecionado. Operação cancelada.")
        return None

    caminho = Path(caminho).resolve()
    messagebox.showinfo("Arquivo selecionado", f"Você selecionou:\n{caminho}")
    return caminho


def escolher_pasta(titulo="Selecione a pasta de saída") -> Path:
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    pasta = filedialog.askdirectory(
        title=titulo,
        initialdir=str(ROOT),
    )
    if not pasta:
        messagebox.showwarning("Aviso", "Nenhuma pasta selecionada. Usando a pasta do script.")
        return ROOT
    return Path(pasta).resolve()


def msg_info(titulo: str, texto: str) -> None:
    """Mostra messagebox; se não houver TK, imprime no console."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk()
        r.withdraw()
        r.attributes("-topmost", True)
        messagebox.showinfo(titulo, texto)
        r.destroy()
    except Exception:
        safe_print(f"[{titulo}] {texto}")


# =====================
# Leitura de dados
# =====================
def _ler_csv_robusto(path: Path) -> pd.DataFrame:
    """
    Lê CSV tentando detectar o delimitador automaticamente (engine='python', sep=None).
    Faz tentativas com encodings comuns.
    """
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    ultimo_erro = None
    for enc in encodings:
        try:
            df = pd.read_csv(
                path,
                engine="python",
                sep=None,           # autodetect delimitador
                encoding=enc,
                dtype=str,          # manter como string inicialmente
                keep_default_na=False,  # não transformar 'NA' em NaN automaticamente
                na_values=[],           # controlaremos NaN manualmente
                on_bad_lines="skip",
            )
            return df
        except Exception as e:
            ultimo_erro = e
    raise RuntimeError(f"Falha ao ler CSV com encodings {encodings}. Ultimo erro: {repr(ultimo_erro)}")


def _ler_excel_robusto(path: Path) -> pd.DataFrame:
    """Lê Excel usando pandas (openpyxl/xlrd conforme extensão)."""
    try:
        df = pd.read_excel(path, dtype=str)
        return df
    except Exception as e:
        raise RuntimeError(f"Falha ao ler Excel: {repr(e)}")


def ler_tabela(path: Path) -> Tuple[pd.DataFrame, str]:
    """Retorna (DataFrame, tipo) onde tipo é 'csv' ou 'excel'."""
    ext = path.suffix.lower()
    if ext == ".csv":
        return _ler_csv_robusto(path), "csv"
    elif ext in (".xlsx", ".xls"):
        return _ler_excel_robusto(path), "excel"
    else:
        # tentativa flexível
        try:
            df = _ler_csv_robusto(path)
            return df, "csv"
        except Exception:
            pass
        try:
            df = _ler_excel_robusto(path)
            return df, "excel"
        except Exception:
            pass
        raise ValueError(f"Extensão não suportada: {ext}. Forneça CSV ou Excel.")


# =====================
# Limpeza e preenchimento (geral)
# =====================
VALORES_VAZIOS = {
    "", " ", "-", "—", "–", "--", "---",
    "na", "n/a", "nao informado", "não informado", "null", "none",
    "sem dado", "indefinido",
}
VALORES_VAZIOS = VALORES_VAZIOS | {v.upper() for v in VALORES_VAZIOS}  # versões em maiúsculo


def limpar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # limpa nomes de colunas (BOM, espaços invisíveis)
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]

    def _strip_cell(x):
        if pd.isna(x):
            return np.nan
        s = str(x).replace("\ufeff", "").strip()
        return s

    # strip em todas as células
    df = df.applymap(_strip_cell)

    # marcadores de vazio -> NaN
    df = df.applymap(lambda x: np.nan if (isinstance(x, str) and x.strip() in VALORES_VAZIOS) else x)
    return df


# =====================
# Regra ESPECIAL para 'Checkout'
# =====================
def preencher_checkout_bfill_then_ffill(series: pd.Series) -> tuple[pd.Series, int]:
    """
    Preenche NaN de 'Checkout' priorizando o PRÓXIMO valor válido (bfill).
    Caso sobrem NaN (somente no final da coluna), preenche com o valor anterior (ffill).
    Retorna (serie_corrigida, qtd_celulas_preenchidas).
    """
    s = series.copy()
    nan_antes = int(s.isna().sum())

    # 1) usar o próximo valor válido para preencher lacunas
    s = s.bfill()

    # 2) qualquer NaN restante (tail sem próximo válido) recebe o anterior
    s = s.ffill()

    nan_depois = int(s.isna().sum())
    preenchidas = nan_antes - nan_depois
    return s, max(preenchidas, 0)


# =====================
# Datas/Horas
# =====================
COLUNAS_DATAHORA = ["Checkin", "Start", "End", "Checkout"]


def _tentar_parse_datetime(serie: pd.Series) -> pd.Series:
    """
    Converte uma série para datetime usando dayfirst=True.
    Retorna strings dd/MM/yyyy HH:mm; mantém original quando inválido.
    """
    parsed = pd.to_datetime(serie, errors="coerce", dayfirst=True)  # sem infer_datetime_format
    out = []
    for orig, dt in zip(serie, parsed):
        if pd.isna(dt):
            out.append(orig)
        else:
            out.append(dt.strftime("%d/%m/%Y %H:%M"))
    return pd.Series(out, index=serie.index)


def padronizar_colunas_datahora(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in COLUNAS_DATAHORA:
        if col in df.columns:
            df[col] = _tentar_parse_datetime(df[col].astype(str))
    return df


# =====================
# Escrita
# =====================
def escrever_saida(df: pd.DataFrame, base_path: Path, tipo: str, pasta_saida: Path) -> Path:
    """
    tipo: 'csv' ou 'excel' (tipo da ENTRADA; saída segue o tipo da entrada)
    Nomeia como <nome>_preenchido_YYYYmmdd_HHMMSS.<ext>
    """
    pasta_saida.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = base_path.stem
    # remover sufixo _PRIMEIRA_VERSAO, se houver
    stem = stem.replace('_PRIMEIRA_VERSAO', '_')

    if tipo == "csv":
        out = pasta_saida / f"{stem}_preenchido_{ts}_SEGUNDA_VERSAO.csv"
        # CSV compatível c/ Excel PT-BR: separador ';' e BOM
        df.to_csv(out, index=False, encoding="utf-8-sig", sep=",")
    else:
        out = pasta_saida / f"{stem}_preenchido_{ts}.xlsx"
        df.to_excel(out, index=False)
    return out


# =====================
# Pipeline principal
# =====================
def processar_arquivo(arquivo_entrada: Path, pasta_saida: Path) -> Path:
    # 1) Ler
    df, tipo = ler_tabela(arquivo_entrada)

    # 2) Limpar
    df = limpar_dataframe(df)

    # --- Contagem prévia de NaN para relatório ---
    antes = int(df.isna().sum().sum())

    # 3) Preencher brancos nas colunas EXCETO 'Checkout' (ffill + bfill)
    df_filled = df.copy()
    cols_except_checkout = [c for c in df_filled.columns if c != "Checkout"]
    if cols_except_checkout:
        df_filled[cols_except_checkout] = df_filled[cols_except_checkout].ffill().bfill()

    # 4) Regra ESPECIAL para 'Checkout': bfill e, se necessário, ffill (garantindo zero NaN)
    if "Checkout" in df_filled.columns:
        nova_checkout, _ = preencher_checkout_bfill_then_ffill(df_filled["Checkout"])
        df_filled["Checkout"] = nova_checkout

    # 5) Padronizar datas/horas (após preenchimentos)
    df_filled = padronizar_colunas_datahora(df_filled)

    # --- Contagem final de NaN para relatório ---
    depois = int(df_filled.isna().sum().sum())
    total_preenchidas = antes - depois

    # 6) Escrever saída
    saida = escrever_saida(df_filled, arquivo_entrada, tipo, pasta_saida)

    # Console (ASCII-safe)
    safe_print(f"Linhas: {len(df_filled)} | Colunas: {len(df_filled.columns)} | Celulas preenchidas: {total_preenchidas}")
    return saida


def main():
    entrada = escolher_arquivo("Selecione o arquivo (CSV ou Excel) para preencher brancos")
    if not entrada:
        return

    pasta_saida = escolher_pasta("Selecione a pasta de saída")
    try:
        out = processar_arquivo(entrada, pasta_saida)
        msg_info(
            "Concluido",
            f"Processamento finalizado com sucesso!\n\n"
            f"Arquivo de saida:\n{out}\n\n"
            f"Dica: o nome termina com _preenchido_YYYYmmdd_HHMMSS."
        )
        safe_print("[OK]", out)
    except Exception as e:
        msg_info("Erro", f"Ocorreu um erro durante o processamento:\n{repr(e)}")
        safe_print("[ERRO]", repr(e))


if __name__ == "__main__":
    main()
