# -*- coding: utf-8 -*-
# =============================================================================
# CÁLCULO DE VALORES BÁSICOS - PROCESSAMENTO DE ESCALAS AERONÁUTICAS (DEG + timestamp)
# Entrada: CSV (normalmente *_TERCEIRA_VERSAO*.csv)
# Saída:  (<stem sem _TERCEIRA_VERSAO>)_QUARTA_VERSAO_<YYYYmmdd_HHMMSS>.csv
#         No mesmo diretório do PDF/CSV; se caminho contiver 'Escalas_Executadas',
#         grava em 'Auditoria_Calculos'.
# =============================================================================

from __future__ import annotations

from datetime import timedelta, time, datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm
import pandas as pd
import os
import warnings
import json

warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# =============================================================================
# Seleção e nomes (DEG)
# =============================================================================
def selecionar_arquivo_csv() -> Path | None:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo CSV (_TERCEIRA_VERSAO).")
    except Exception:
        pass
    caminho = filedialog.askopenfilename(
        title="Selecione o CSV de entrada",
        filetypes=[("CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    try:
        root.destroy()
    except Exception:
        pass
    return Path(caminho).resolve() if caminho else None

import re
from datetime import datetime
from pathlib import Path

def _remover_versao_e_timestamp(stem: str) -> str:
    """
    Remove do final do nome qualquer um destes padrões (uma ou mais vezes):
      _PRIMEIRA_VERSAO
      _SEGUNDA_VERSAO
      _TERCEIRA_VERSAO
      _QUARTA_VERSAO
    opcionalmente seguidos de _YYYYmmdd ou _YYYYmmdd_HHMMSS.
    """
    padrao = re.compile(
        r'(?:_(?:PRIMEIRA|SEGUNDA|TERCEIRA|QUARTA)_VERSAO)'
        r'(?:_\d{8}(?:_\d{6})?)?$',  # timestamp opcional
        flags=re.IGNORECASE
    )
    while True:
        novo = padrao.sub('', stem)
        if novo == stem:
            return novo
        stem = novo

def caminho_saida_quarta_versao(entrada: Path) -> Path:
    """
    Grava em 'Auditoria_Calculos' se 'Escalas_Executadas' estiver no caminho;
    caso contrário, grava no mesmo diretório. Nome final:
      <stem_limpo>_QUARTA_VERSAO_YYYYmmdd_HHMMSS.csv
    """
    dir_in  = entrada.parent
    dir_out = Path(str(dir_in).replace('Escalas_Executadas', 'Auditoria_Calculos'))
    dir_out.mkdir(parents=True, exist_ok=True)

    stem_base = _remover_versao_e_timestamp(entrada.stem)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{stem_base}_QUARTA_VERSAO_{ts}.csv"
    return dir_out / out_name


def ler_csv_robusto(path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    ultimo_erro = None
    for enc in encodings:
        try:
            return pd.read_csv(path, sep=",", encoding=enc)
        except Exception as e:
            ultimo_erro = e
    raise RuntimeError(f"Falha ao ler CSV ({path.name}). Último erro: {repr(ultimo_erro)}")

# =============================================================================
# Conversão de datas (mantida e reforçada)
# =============================================================================

def converter_data_flexivel(data_str):
    """
    Converte datas em múltiplos formatos para datetime.
    Suporta: "01DEZ17 02:00", "2017-12-01 02:00", "01/12/2017 02:00", etc.
    - Sempre interpreta com dayfirst=True quando possível.
    - Se não der para converter, retorna o valor ORIGINAL (string) para não perder dados.
    """
    if pd.isna(data_str) or str(data_str).strip() in ("", "-", "None", "NaN", "nan"):
        return pd.NaT  # manter NaT nos vazios explícitos

    s = str(data_str).strip()

    # 1) Tentativa direta (cobre ISO e dd/mm)
    dt = pd.to_datetime(s, errors="coerce", dayfirst=True)
    if pd.notna(dt):
        return dt

    # 2) Mapas de meses mais completos (PT e EN), com e sem ponto
    meses_pt = {
        # Português extenso
        "janeiro":1,"fevereiro":2,"março":3,"marco":3,"abril":4,"maio":5,"junho":6,
        "julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12,
        # Português abreviado (com e sem ponto)
        "jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12,
        "jan.":1,"fev.":2,"mar.":3,"abr.":4,"mai.":5,"jun.":6,"jul.":7,"ago.":8,"set.":9,"out.":10,"nov.":11,"dez.":12,
        # Inglês extenso/abreviado
        "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
        "jan_en":1,"feb":2,"mar_en":3,"apr":4,"may_en":5,"jun_en":6,"jul_en":7,"aug":8,"sep":9,"sept":9,"oct":10,"nov_en":11,"dec":12,
    }

    # 3) Padrões tipo "01DEZ17 02:00" (dia + letras + ano)
    import re as _re
    m = _re.match(r'^\s*(\d{1,2})\s*([A-Za-z\.]{3,9})\s*(\d{2,4})(?:\s+(\d{2}:\d{2}(?::\d{2})?))?\s*$', s, flags=_re.IGNORECASE)
    if not m:
        # Também aceita sem espaços entre dia/mês: "01DEZ17 02:00"
        m = _re.match(r'^\s*(\d{1,2})([A-Za-z\.]{3,9})(\d{2,4})(?:\s+(\d{2}:\d{2}(?::\d{2})?))?\s*$', s, flags=_re.IGNORECASE)

    if m:
        dia, mes_txt, ano_txt, hora = m.groups()
        mes_txt_low = mes_txt.lower()
        # normaliza chaves que colidem com inglês/português
        key = mes_txt_low
        if key == "jan":  # pode ser en/pt, tanto faz (1)
            pass
        elif key == "mar":  # en/pt (3)
            pass
        elif key == "may":  # inglês
            key = "may_en"
        elif key == "jun":  # ambíguo, mas numérico é igual
            key = "jun_en"
        elif key == "jul":
            key = "jul_en"
        elif key == "nov":
            key = "nov_en"
        # demais permanecem

        mes_num = meses_pt.get(key)
        if mes_num:
            ano = int(ano_txt)
            if ano < 100:  # 2 dígitos
                ano += 2000
            try:
                if not hora:
                    hora = "00:00"
                composed = f"{ano:04d}-{mes_num:02d}-{int(dia):02d} {hora}"
                dt2 = pd.to_datetime(composed, errors="coerce")
                if pd.notna(dt2):
                    return dt2
            except Exception:
                pass

    # 4) Tentativas por formato explícito
    formatos = [
        "%d/%m/%Y %H:%M:%S","%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M:%S","%d-%m-%Y %H:%M",
        "%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M",
        "%d/%m/%Y","%d-%m-%Y","%Y-%m-%d",
    ]
    for fmt in formatos:
        try:
            dt3 = pd.to_datetime(s, format=fmt, errors="coerce")
            if pd.notna(dt3):
                return dt3
        except Exception:
            continue

    # 5) Último recurso: retorna NaT (deixa a célula como estava para não apagar mais tarde)
    return pd.NaT

# =============================================================================
# Funções de cálculo (mantidas do original)
# =============================================================================
def diurno(start, end):
    if pd.isna(start) or pd.isna(end):
        return timedelta(0)
    if start.time() >= time(6, 0) and start.time() < time(18, 0):
        if end.time() >= time(6, 0) and end.time() < time(18, 0):
            return end - start
        elif end.time() >= time(18, 0):
            return datetime.combine(start.date(), time(18, 0)) - start
    elif start.time() < time(6, 0):
        if end.time() >= time(6, 0):
            return datetime.combine(start.date(), time(6, 0)) - start
    return timedelta(0)

def noturno(operacao, diurno_val):
    return operacao - diurno_val

def verificar_internacional(row, aeroportos_IATA):
    dep_presente = row['Dep'] in aeroportos_IATA['IATA'].values
    arr_presente = row['Arr'] in aeroportos_IATA['IATA'].values
    return 'N' if dep_presente and arr_presente else 'S'

# =============================================================================
# Pipeline principal
# =============================================================================
def main():
    # 1) Selecionar CSV de entrada
    entrada = selecionar_arquivo_csv()
    if not entrada:
        print("Nenhum arquivo selecionado. Operação cancelada.")
        return
    if entrada.suffix.lower() != ".csv":
        print(f"O arquivo selecionado não é CSV: {entrada.name}")
        return
    print(f"📄 Arquivo selecionado: {entrada}")

    # 2) Ler CSV
    tabela = ler_csv_robusto(entrada)

    # 3) Carregar aeroportos (JSON) — caminhos conforme seu ambiente
    path_aeroportos = Path(r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\todos_aeroportos.json")
    if not path_aeroportos.exists():
        path_aeroportos = Path(r"G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS\airports2.csv")
        if not path_aeroportos.exists():
            print("Arquivo de aeroportos não encontrado em nenhum caminho!")
            return

    try:
        if path_aeroportos.suffix.lower() == ".json":
            with open(path_aeroportos, "r", encoding="utf-8") as f:
                dados_aeroportos = json.load(f)
            df_aeroportos_IATA = pd.DataFrame(dados_aeroportos)
        else:
            df_aeroportos_IATA = pd.read_csv(path_aeroportos, encoding="utf-8", dtype=str)
        if 'IATA' not in df_aeroportos_IATA.columns:
            if 'iata' in df_aeroportos_IATA.columns:
                df_aeroportos_IATA = df_aeroportos_IATA.rename(columns={'iata': 'IATA'})
            elif 'code' in df_aeroportos_IATA.columns:
                df_aeroportos_IATA = df_aeroportos_IATA.rename(columns={'code': 'IATA'})
        df_aeroportos_IATA = df_aeroportos_IATA.reset_index(drop=True)
    except Exception as e:
        print(f"Erro ao carregar aeroportos: {e}")
        return

    # 4) Carregar feriados
    print("Carregando arquivo de feriados...")
    path_feriados = Path(r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\feriados.json")
    try:
        with open(path_feriados, 'r', encoding='utf-8') as f:
            feriados_originais = json.load(f)
        feriados = []
        for feriado in feriados_originais:
            try:
                data_original = feriado.get('date', '')
                if '/' in data_original:
                    feriados.append(feriado)
                elif '-' in data_original and len(data_original) == 10:
                    data_convertida = datetime.strptime(data_original, '%Y-%m-%d')
                    feriados.append({
                        'date': data_convertida.strftime('%d/%m/%Y'),
                        'name': feriado.get('name', ''),
                        'type': feriado.get('type', '')
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"Erro ao carregar feriados: {e}")
        feriados = []

    # 5) Conversão de datas e criação de colunas base
    print("Convertendo datas com formato flexível...")
    for col in ['Checkin', 'Start', 'End', 'Checkout']:
        if col in tabela.columns:
            tabela[col] = tabela[col].apply(converter_data_flexivel)

    for col in ['Tempo Apresentacao','Operacao','Tempo Solo','Jornada','Repouso',
                'Repouso Extra','Diurno','Noturno','Especial','Especial Noturno']:
        if col not in tabela.columns:
            tabela[col] = pd.to_timedelta(0)
        else:
            tabela[col] = pd.to_timedelta(tabela[col])

    # 6) Cálculos
    tabela = tabela.reset_index(drop=True)
    tqdm.pandas()

    tabela['Operacao'] = tabela['End'] - tabela['Start']

    tabela.loc[tabela['Id_Leg'].isin(['-I','-IF']), 'Tempo Apresentacao'] = tabela['Start'] - tabela['Checkin']

    mask1 = (tabela['Id_Leg'] == '-I') & (tabela['Id_Leg'].shift(-1) == '-M')
    mask2 = (tabela['Id_Leg'] == '-M') & (tabela['Id_Leg'].shift(-1) == '-M')
    mask3 = (tabela['Id_Leg'] == '-I') & (tabela['Id_Leg'].shift(-1) == '-F')
    mask4 = (tabela['Id_Leg'] == '-M') & (tabela['Id_Leg'].shift(-1) == '-F')
    for m in [mask1, mask2, mask3, mask4]:
        tabela.loc[m, 'Tempo Solo'] = tabela['Start'].shift(-1) - tabela['End']

    tabela.loc[tabela['Id_Leg'].isin(['-F','-IF']), 'Jornada'] = (tabela['Checkout'] - tabela['Checkin']) + timedelta(minutes=30)
    tabela.loc[tabela['Id_Leg'].isin(['-F','-IF']), 'Repouso'] = tabela['Checkin'].shift(-1) - tabela['Checkout']
    tabela.loc[(tabela['Id_Leg'].isin(['-F','-IF'])) & (tabela['Repouso'] > timedelta(hours=12)), 'Repouso Extra'] = tabela['Repouso'] - timedelta(hours=12)

    tabela['Diurno'] = tabela.apply(lambda row: diurno(row['Start'], row['End']), axis=1)
    tabela['Noturno'] = tabela.apply(lambda row: noturno(row['Operacao'], row['Diurno']), axis=1)

    # Especial / Especial Noturno — finais de semana
    tabela['Especial Noturno'] = tabela.apply(
        lambda row: row['Noturno'] if (pd.notna(row['Start']) and row['Start'].weekday() == 5 and row['Start'].time() >= time(21, 0)) else timedelta(0),
        axis=1
    )
    tabela['Especial Noturno'] = tabela.apply(
        lambda row: row['Noturno'] if (pd.notna(row['Start']) and row['Start'].weekday() == 6 and row['Start'].time() <= time(21, 0)) else row['Especial Noturno'],
        axis=1
    )
    tabela['Especial'] = tabela.apply(
        lambda row: row['Diurno'] if (pd.notna(row['Start']) and row['Start'].weekday() == 6 and row['Start'].time() <= time(18, 0)) else timedelta(0),
        axis=1
    )

    # Feriados
    try:
        tabela['Start_date'] = tabela['Start'].dt.date
        feriados_dates = []
        for feriado in feriados:
            try:
                feriados_dates.append(datetime.strptime(feriado['date'], '%d/%m/%Y').date())
            except Exception:
                pass
        tabela['Especial'] = tabela.apply(
            lambda row: row['Diurno'] if (pd.notna(row['Start_date']) and row['Start_date'] in feriados_dates) else row['Especial'],
            axis=1
        )
        tabela['Especial Noturno'] = tabela.apply(
            lambda row: row['Noturno'] if (pd.notna(row['Start_date']) and row['Start_date'] in feriados_dates) else row['Especial Noturno'],
            axis=1
        )
    except Exception as e:
        print(f"Aviso: cálculo de feriados ignorado ({e}).")

    # Internacional
    tabela['Internacional'] = tabela.apply(lambda row: verificar_internacional(row, df_aeroportos_IATA), axis=1)

    
    # 7) Padronizar datas para saída (sem apagar valores não reconhecidos)
    def _formatar_datas_para_saida(df: pd.DataFrame, cols=("Checkin","Start","End","Checkout")) -> pd.DataFrame:
        out = df.copy()
        for col in cols:
            if col in out.columns:
                s = out[col]
                if pd.api.types.is_datetime64_any_dtype(s):
                    out[col] = s.dt.strftime("%d/%m/%Y %H:%M")
                else:
                    s_str = s.astype(str)
                    mask = ~s_str.str.fullmatch(r"\s*|\-\s*|NaT|nan|NaN|None", na=True)
                    parsed = pd.to_datetime(s_str[mask], errors="coerce", dayfirst=True)
                    out[col] = s_str
                    ok = parsed.notna()
                    if ok.any():
                        out.loc[s_str[mask].index[ok], col] = parsed[ok].dt.strftime("%d/%m/%Y %H:%M")
        return out

    tabela = _formatar_datas_para_saida(tabela)

    # 8) Gravar CSV de saída (QUARTA_VERSAO + timestamp)
    saida = caminho_saida_quarta_versao(entrada)
    tabela.to_csv(saida, index=False, encoding="utf-8-sig")
    print(f"✅ Arquivo gravado: {saida}")

    try:
        r = tk.Tk(); r.withdraw(); r.attributes("-topmost", True)
        messagebox.showinfo("Concluído", f"Cálculo finalizado!\n\nArquivo de saída:\n{saida}")
        r.destroy()
    except Exception:
        pass

if __name__ == "__main__":
    main()
