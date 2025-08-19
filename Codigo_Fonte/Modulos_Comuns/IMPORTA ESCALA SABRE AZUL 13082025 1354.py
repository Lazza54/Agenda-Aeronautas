# -*- coding: utf-8 -*-
"""
PDF -> CSV (escala) — parser por TEXTO (pdfplumber.extract_text)

CSV (UTF-8 BOM) com cabeçalho EXATO:
Activity, Checkin, Start, Dep, Arr, End, Checkout, AcVer, DD, CAT, Crew
"""

import os
import re
import sys
import unicodedata
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import pandas as pd
import pdfplumber

CSV_COLUMNS = ["Activity", "Checkin", "Start", "Dep", "Arr", "End", "Checkout", "AcVer", "DD", "CAT", "Crew"]
IATA_BLACKLIST = {"UTC", "LOC", "LT", "GND", "CA"}

# ---------------- UI ----------------
def _info(msg: str):
    print(msg)
    try: messagebox.showinfo("Informação", msg)
    except tk.TclError: pass

def _erro(msg: str):
    print("ERRO:", msg, file=sys.stderr)
    try: messagebox.showerror("Erro", msg)
    except tk.TclError: pass

def escolher_pdf() -> str:
    root = tk.Tk(); root.withdraw()
    path = filedialog.askopenfilename(
        title="Selecione o PDF de escala",
        filetypes=[("Arquivos PDF", "*.pdf")],
    )
    return path or ""

def csv_path_para(pdf_path: str) -> str:
    base, _ = os.path.splitext(pdf_path)
    return base + "_PRIMEIRA_VERSAO.csv"

# ---------------- helpers ----------------
MONTHS = {
    "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
    "july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
    "jan":1,"feb":2,"mar":3,"apr":4,"jun":6,"jul":7,"aug":8,"sep":9,"sept":9,"oct":10,"nov":11,"dec":12,
    "janeiro":1,"fevereiro":2,"março":3,"marco":3,"abril":4,"maio":5,"junho":6,
    "julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12,
    "jan.":1,"fev.":2,"mar.":3,"abr.":4,"mai.":5,"jun.":6,"jul.":7,"ago.":8,"set.":9,"out.":10,"nov.":11,"dez.":12,
}

def _strip_accents_lower(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower()

def _clean_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def _extract_lines(pdf_path: str) -> List[str]:
    lines: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            for ln in txt.splitlines():
                ln = _clean_spaces(ln)
                if ln:
                    lines.append(ln)
    return lines

def _parse_date_header(line: str) -> Optional[str]:
    """
    'Tue, 29th July 2025 (Local time)' -> '29/07/2025'
    """
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z\.]{3,})\s+(\d{4})\b", line)
    if not m: return None
    d = int(m.group(1)); mon_key = m.group(2).lower(); y = int(m.group(3))
    mth = MONTHS.get(mon_key)
    if not mth: return None
    return f"{d:02d}/{mth:02d}/{y:04d}"

def _times_with_plus_and_pos(line: str) -> List[Tuple[str, bool, int, int]]:
    """
    Retorna [(HH:MM, plus_one, start_idx, end_idx)].
    Detecta '12:00 +1' mesmo com espaços variados.
    """
    out = []
    for m in re.finditer(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", line):
        hhmm = f"{m.group(1)}:{m.group(2)}"
        tail = line[m.end():m.end()+6]
        plus = bool(re.match(r"\s*\+\s*1\b", tail))
        out.append((hhmm, plus, m.start(), m.end()))
    return out

def _combine_dt_plus(date_ddmmyyyy: Optional[str], hhmm: str, plus_one: bool) -> str:
    if not date_ddmmyyyy or not hhmm: return ""
    dt = datetime.strptime(f"{date_ddmmyyyy} {hhmm}", "%d/%m/%Y %H:%M")
    if plus_one:
        dt += timedelta(days=1)
    return dt.strftime("%d/%m/%Y %H:%M")

def _flight_code(line: str) -> Optional[str]:
    m = re.search(r"\b([A-Z]{1,3})[-\s]?(\d{3,5})\b", line)
    return f"{m.group(1)}{m.group(2)}".upper() if m else None

def _generic_code_at_start(line: str) -> Optional[str]:
    """
    Captura códigos tipo 'SFX', 'SIM', 'DUTY' etc no INÍCIO da linha,
    ignorando OFF/GROUND/APRESENTACAO/RELEASE.
    """
    m = re.match(r"^([A-Z]{2,8})\b", line)
    if not m: return None
    code = m.group(1)
    low = _strip_accents_lower(code)
    if low in {"off","ground","release"} or "apresenta" in low:
        return None
    return code

def _iatas_anywhere(line: str) -> List[str]:
    toks = re.findall(r"\b[A-Z]{3}\b", line)
    return [t for t in toks if t not in IATA_BLACKLIST]

def _iatas_after(line: str, pos: int) -> List[str]:
    seg = line[pos:]
    toks = re.findall(r"\b[A-Z]{3}\b", seg)
    return [t for t in toks if t not in IATA_BLACKLIST]

def _token_right_after(line: str, pos: int) -> str:
    """
    Pega o 1º token ÚTIL após 'pos', pulando '+1' e separadores.
    Preferência por IATA (AAA). Se não houver IATA, pega token alfanumérico.
    Ex.: '12:00 - 12:00 +1 VCP' -> 'VCP'
    """
    idx = pos
    while True:
        m_skip = re.match(r"\s*(\+1|[-–—/|])\s*", line[idx:])
        if not m_skip:
            break
        idx += m_skip.end()
    m_iata = re.search(r"\b([A-Z]{3})\b", line[idx:])
    if m_iata and m_iata.group(1) not in IATA_BLACKLIST:
        return m_iata.group(1)
    m_tok = re.search(r"\s*([A-Za-z0-9]{2,10})", line[idx:])
    return m_tok.group(1) if m_tok else ""

def _paren_content(line: str) -> str:
    m = re.search(r"\((.*?)\)", line)
    return m.group(1).strip() if m else ""

def _cat_token(line: str) -> str:
    if re.search(r"\bCA\b", line): return "CA"
    m = re.search(r"\b(FO|SFO|INSTRUCTOR|INSTR)\b", line, flags=re.I)
    return m.group(1).upper() if m else ""

# ---------------- core ----------------
def pdf_para_csv(pdf_path: str) -> str:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError("PDF não encontrado.")

    lines = _extract_lines(pdf_path)
    if not lines:
        raise RuntimeError("Nenhum texto extraído do PDF (OCR pode ser necessário).")

    current_date = None
    pending_checkin = ""           # gerado por 'Apresentação'
    rows: List[dict] = []
    last_task_idx: Optional[int] = None

    def _apply_pending_checkin(row: dict):
        """Se existe Apresentação pendente, aplica ao Checkin da PRIMEIRA tarefa criada."""
        nonlocal pending_checkin
        if pending_checkin:
            if (not row.get("Checkin")) or (row.get("Start") and row.get("Checkin") == row.get("Start")):
                row["Checkin"] = pending_checkin
                pending_checkin = ""

    for ln in lines:
        lnl = _strip_accents_lower(ln)

        # Cabeçalho do dia -> define data corrente
        dh = _parse_date_header(ln)
        if dh:
            current_date = dh
            continue

        # Ignorar itens que não viram linha
        if "deslocamento" in lnl or lnl.startswith("hotel") or " hotel " in lnl:
            continue

        # Apresentação -> define pending_checkin (1º horário)
        if "apresenta" in lnl:
            tms = _times_with_plus_and_pos(ln)
            pending_checkin = _combine_dt_plus(current_date, tms[0][0], tms[0][1]) if (tms and current_date) else ""
            continue

        # Release -> Checkout = 2º horário (+1 se houver) na última tarefa aberta
        if "release" in lnl:
            tms = _times_with_plus_and_pos(ln)
            if len(tms) >= 2 and current_date and last_task_idx is not None:
                rows[last_task_idx]["Checkout"] = _combine_dt_plus(current_date, tms[1][0], tms[1][1])
            continue

        # ========= OFF — horários reais e IATA após 2º horário (pulando +1) =========
        if lnl.startswith("off"):
            activity = _paren_content(ln) or "OFF"
            tms = _times_with_plus_and_pos(ln)

            # Dep/Arr logo após o 2º horário (pulando '+1')
            dep = arr = ""
            if tms:
                pos_after_last_time = tms[-1][3]
                token = _token_right_after(ln, pos_after_last_time)
                if token:
                    dep = token; arr = token

            # Horários reais (considerar +1 no segundo)
            if current_date:
                start = _combine_dt_plus(current_date, tms[0][0], tms[0][1]) if len(tms) >= 1 else f"{current_date} 00:00"
                end   = _combine_dt_plus(current_date, tms[1][0], tms[1][1]) if len(tms) >= 2 else start

                row = {
                    "Activity": activity,           # ex.: FR, FP, P-SNA
                    "Checkin":  start,
                    "Start":    start,
                    "Dep":      dep,
                    "Arr":      arr,
                    "End":      end,
                    "Checkout": end,
                    "AcVer":    "",
                    "DD":       "",
                    "CAT":      _cat_token(ln),
                    "Crew":     "",
                }
                _apply_pending_checkin(row)
                rows.append(row)
                last_task_idx = len(rows) - 1
            continue

        # ========= GROUND — preservado como estava (gera SAF/EAD/SFX) =========
        if lnl.startswith("ground") or " ground" in lnl:
            activity = _paren_content(ln) or "GROUND"
            tms = _times_with_plus_and_pos(ln)
            start = _combine_dt_plus(current_date, tms[0][0], tms[0][1]) if (current_date and len(tms) >= 1) else ""
            end   = _combine_dt_plus(current_date, tms[1][0], tms[1][1]) if (current_date and len(tms) >= 2) else ""
            dep = arr = ""
            if len(tms) >= 2:
                token = _token_right_after(ln, tms[1][3])  # pula '+1' e separadores
                if token:
                    dep = token; arr = token
                else:
                    after_iatas = _iatas_after(ln, tms[1][3])
                    if after_iatas:
                        dep = after_iatas[0]; arr = after_iatas[0]
            row = {
                "Activity": activity,   # SAF / EAD / SFX...
                "Checkin":  start,
                "Start":    start,
                "Dep":      dep,
                "Arr":      arr,
                "End":      end,
                "Checkout": end,
                "AcVer":    "",
                "DD":       "",
                "CAT":      _cat_token(ln),
                "Crew":     "",
            }
            _apply_pending_checkin(row)
            rows.append(row)
            last_task_idx = len(rows) - 1
            continue

        # ========= RESERVA (SEA) — tratar como voo normal =========
        if "reserva" in lnl and "(sea" in lnl:
            if current_date:
                tms = _times_with_plus_and_pos(ln)
                start = _combine_dt_plus(current_date, tms[0][0], tms[0][1]) if len(tms) >= 1 else ""
                end   = _combine_dt_plus(current_date, tms[1][0], tms[1][1]) if len(tms) >= 2 else ""
                iatas = _iatas_anywhere(ln)
                dep = iatas[0] if len(iatas) >= 1 else ""
                arr = iatas[1] if len(iatas) >= 2 else ""

                row = {
                    "Activity": "SEA",
                    "Checkin":  "",  # será preenchido pela Apresentação anterior
                    "Start":    start,
                    "Dep":      dep,
                    "Arr":      arr,
                    "End":      end,
                    "Checkout": "",
                    "AcVer":    "",
                    "DD":       "",
                    "CAT":      _cat_token(ln),
                    "Crew":     "",
                }
                _apply_pending_checkin(row)
                rows.append(row)
                last_task_idx = len(rows) - 1
            continue

        # ========= VOO (ADxxxx) =========
        act = _flight_code(ln)
        if act and current_date:
            tms = _times_with_plus_and_pos(ln)
            start = _combine_dt_plus(current_date, tms[0][0], tms[0][1]) if len(tms) >= 1 else ""
            end   = _combine_dt_plus(current_date, tms[1][0], tms[1][1]) if len(tms) >= 2 else ""
            iatas = _iatas_anywhere(ln)
            dep = iatas[0] if len(iatas) >= 1 else ""
            arr = iatas[1] if len(iatas) >= 2 else ""
            row = {
                "Activity": act,
                "Checkin":  "",
                "Start":    start,
                "Dep":      dep,
                "Arr":      arr,
                "End":      end,
                "Checkout": "",
                "AcVer":    "",
                "DD":       "",
                "CAT":      _cat_token(ln),
                "Crew":     "",
            }
            _apply_pending_checkin(row)
            rows.append(row)
            last_task_idx = len(rows) - 1
            continue

        # ========= Códigos genéricos no começo (SFX, SIM, DUTY etc.) =========
        gen = _generic_code_at_start(ln)
        if gen and current_date:
            tms = _times_with_plus_and_pos(ln)
            start = _combine_dt_plus(current_date, tms[0][0], tms[0][1]) if len(tms) >= 1 else ""
            end   = _combine_dt_plus(current_date, tms[1][0], tms[1][1]) if len(tms) >= 2 else ""
            iatas = _iatas_anywhere(ln)
            dep = iatas[0] if len(iatas) >= 1 else ""
            arr = iatas[1] if len(iatas) >= 2 else ""
            row = {
                "Activity": gen,
                "Checkin":  "",
                "Start":    start,
                "Dep":      dep,
                "Arr":      arr,
                "End":      end,
                "Checkout": "",
                "AcVer":    "",
                "DD":       "",
                "CAT":      _cat_token(ln),
                "Crew":     "",
            }
            _apply_pending_checkin(row)
            rows.append(row)
            last_task_idx = len(rows) - 1
            continue

        # demais linhas ignoradas

    # DataFrame final
    df = pd.DataFrame(rows, columns=CSV_COLUMNS).fillna("")
    for c in CSV_COLUMNS:
        if c not in df.columns: df[c] = ""
    df = df[CSV_COLUMNS]

    out_csv = csv_path_para(pdf_path)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    return out_csv

# ---------------- main ----------------
def main():
    pdf_path = escolher_pdf()
    if not pdf_path:
        _erro("Nenhum PDF selecionado.")
        return
    try:
        out_csv = pdf_para_csv(pdf_path)
    except Exception as e:
        _erro(str(e)); return
    _info(f"Concluído!\nCSV gerado em:\n{out_csv}")

if __name__ == "__main__":
    main()
