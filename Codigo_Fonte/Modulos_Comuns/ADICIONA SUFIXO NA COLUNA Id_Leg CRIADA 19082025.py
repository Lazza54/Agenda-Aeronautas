# -*- coding: utf-8 -*-
"""
ADICIONA SUFIXO NAS PERNAS DE VOO (DEG + timestamp)
---------------------------------------------------
- Seleciona um CSV de entrada via diálogo.
- Adiciona/zera coluna 'Id_Leg' e preenche por grupos de 'Checkin':
    * tamanho 1 -> '-IF'
    * primeira  -> '-I'
    * meio      -> '-M'
    * última    -> '-F'
- Salva no MESMO diretório do arquivo de entrada, com nome:
    <stem_sem__SEGUNDA_VERSAO>_TERCEIRA_VERSAO_<YYYYmmdd_HHMMSS>.csv

Requisitos: pandas, tkinter
"""

from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime

import pandas as pd

# =========================
# Seleção de arquivo (DEG)
# =========================
def selecionar_arquivo_csv(inicial: Path | None = None) -> Path | None:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo CSV (_SEGUNDA_VERSAO).")
    except Exception:
        pass
    filetypes = [("CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    caminho = filedialog.askopenfilename(
        title="Selecione o CSV de entrada",
        initialdir=str(inicial or Path.cwd()),
        filetypes=filetypes
    )
    try:
        root.destroy()
    except Exception:
        pass
    return Path(caminho).resolve() if caminho else None

def caminho_saida_com_timestamp(entrada: Path) -> Path:
    """
    Gera:
      <stem_sem__SEGUNDA_VERSAO>_TERCEIRA_VERSAO_<YYYYmmdd_HHMMSS>.csv
    no MESMO diretório do arquivo de entrada.
    """
    stem = entrada.stem
    if stem.endswith("_SEGUNDA_VERSAO"):
        stem = stem[: -len("_SEGUNDA_VERSAO")]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{stem}_TERCEIRA_VERSAO_{ts}.csv"
    return entrada.with_name(out_name)

# =========================
# Leitura robusta (CSV)
# =========================
def ler_csv_robusto(path: Path) -> pd.DataFrame:
    # tenta encodings comuns; separador fixo vírgula
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    ultimo_erro = None
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc, dtype=str)
        except Exception as e:
            ultimo_erro = e
    raise RuntimeError(f"Falha ao ler CSV ({path.name}). Último erro: {repr(ultimo_erro)}")

# =========================
# Lógica de Id_Leg por grupo
# =========================
def preencher_id_leg_por_checkin(df: pd.DataFrame) -> pd.DataFrame:
    if "Checkin" not in df.columns:
        raise KeyError("Coluna 'Checkin' não encontrada no CSV.")

    out = df.copy()

    # Garante a coluna Id_Leg na posição 1 (após a primeira coluna)
    if "Id_Leg" not in out.columns:
        out.insert(1, "Id_Leg", "")
    else:
        out["Id_Leg"] = ""

    # Agrupa por Checkin preservando a ordem original
    chk = out["Checkin"].astype(str)

    # groupby ignora NaN; trataremos NaN separadamente como linhas isoladas
    groups = chk.groupby(chk, sort=False).groups  # dict: valor -> Index
    for key, idx in groups.items():
        # idx pode vir como Index; garantir lista em ordem pela posição original
        idx_list = list(sorted(idx))
        n = len(idx_list)
        if n == 0:
            continue
        if key in ("", "nan", "NaN", "None") or key.strip() == "":
            # sem valor real -> deixa em branco
            continue
        if n == 1:
            out.loc[idx_list[0], "Id_Leg"] = "-IF"
        else:
            out.loc[idx_list[0], "Id_Leg"] = "-I"
            if n > 2:
                out.loc[idx_list[1:-1], "Id_Leg"] = "-M"
            out.loc[idx_list[-1], "Id_Leg"] = "-F"

    return out

# =========================
# Pipeline principal
# =========================
def main():
    entrada = selecionar_arquivo_csv()
    if not entrada:
        print("Nenhum arquivo selecionado. Operação cancelada.")
        return
    if entrada.suffix.lower() != ".csv":
        print(f"O arquivo selecionado não é CSV: {entrada.name}")
        return

    print(f"📄 Arquivo de entrada: {entrada}")

    df = ler_csv_robusto(entrada)
    print("Colunas do arquivo lido:", list(df.columns))

    df_final = preencher_id_leg_por_checkin(df)

    saida = caminho_saida_com_timestamp(entrada)
    df_final.to_csv(saida, index=False, encoding="utf-8-sig")
    print(f"✅ Arquivo gravado: {saida}")

    # Mensagem visual (opcional)
    try:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk(); r.withdraw(); r.attributes("-topmost", True)
        messagebox.showinfo("Concluído", f"Processamento finalizado!\n\nArquivo de saída:\n{saida}")
        r.destroy()
    except Exception:
        pass

if __name__ == "__main__":
    main()
