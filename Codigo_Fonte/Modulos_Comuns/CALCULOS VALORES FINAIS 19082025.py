# -*- coding: utf-8 -*-
"""
Exported from Jupyter notebook: CALCULOS FINAIS JUPYTER 14082025.ipynb
Converted on: 2025-08-14 19:42:46

Notes:
- Markdown cells were converted to comments.
- IPython magics and shell escapes were commented out.
"""
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox

import os
import sys
import re
import warnings
import time
import json
import sys
import locale

from tabnanny import check
from datetime import datetime, time, timedelta


def _stdout_supports_utf8():
    enc = (getattr(sys.stdout, "encoding", None) or locale.getpreferredencoding(False) or "").upper()
    return "UTF-8" in enc

try:
    # Force UTF-8 to avoid UnicodeEncodeError on cp1252 consoles (emojis etc.)
    if not _stdout_supports_utf8():
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

EMOJI = {
    "calendar": "📅" if _stdout_supports_utf8() else "[CAL]",
    "warn": "⚠️" if _stdout_supports_utf8() else "[!]",
}
# ###############################################################################
# #                            CALCULOS FINAIS                                 #
# #                       SISTEMA DE CÁLCULOS AERONAUTAS AZUL                  #
# ###############################################################################
# 
# Descrição: Script principal para processamento completo de escalas de aeronautas
#            com cálculos de horas diurnas, noturnas, especiais e regulamentares
# 
# Autor: Ricardo Lazzarini
# Data: 27/06/2024
# Versão: 2.1 - Integração com tipos_reserva.json
# Última atualização: 29/06/2025
# 
# Funcionalidades:
# - Importação e validação de dados de escala
# - Cálculos automáticos de todas as categorias de tempo
# - Classificação de atividades (voo, reserva, plantão, treinamento)
# - Carregamento automático de tipos de reserva do arquivo JSON
# - Tratamento robusto de datas brasileiras
# - Interface de usuário aprimorada
# - Relatórios de execução detalhados
# - Sistema de monitoramento e debug avançado
# 
# ###############################################################################
# # =============================================================================
# # 1. IMPORTAÇÃO DE BIBLIOTECAS
# # =============================================================================
################################################################################

def select_working_directory():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter
    working_directory = filedialog.askdirectory(title="Selecione o diretório de trabalho")
    
    if not working_directory:
        messagebox.showerror("Erro", "Nenhum diretório selecionado.")
        sys.exit(1)
    
    os.chdir(working_directory)
    print(f"Diretório de trabalho definido para: {working_directory}")
    return working_directory  # <-- Adicione este return

# selecionar o arquivo de entrada
def select_input_file():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter
    input_file = filedialog.askopenfilename(title="Selecione o arquivo de entrada", filetypes=[("CSV files", "*.csv")])
    
    if not input_file:
        messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
        sys.exit(1)
    
    print(f"Arquivo de entrada selecionado: {input_file}")
    return input_file

arquivo_entrada = select_input_file()

################################################################################

# ======= SELEÇÃO ÚNICA DE DIRETÓRIO E ARQUIVO =======
WORKING_DIRECTORY = select_working_directory()
INPUT_FILE = select_input_file()
try:
    os.chdir(WORKING_DIRECTORY)
except Exception as _e:
    print(f"[AVISO] Não foi possível mudar diretório: {WORKING_DIRECTORY} -> {_e}")
print(f"DIRETÓRIO DE TRABALHO: {WORKING_DIRECTORY}")
print(f"ARQUIVO DE ENTRADA: {INPUT_FILE}")
# =====================================================
def montar_caminho_arquivo(working_directory, input_file, texto_substituicao):
    # Simulando as funções existentes
    #diretorio = "G:\\SPECTRUM_SYSTEM\\Aeronautas\\AZUL\\RICARDO LAZZARINI\\Auditoria_Calculos"
    #nome_arquivo = "ricardo_lazzarini_vcp_3394_112017_022023_QUARTA_VERSAO"
    diretorio = working_directory
    nome_arquivo = input_file
    
    # Substituindo 'QUARTA_VERSAO' pelo texto recebido
    nome_arquivo_final = nome_arquivo.replace('QUARTA_VERSAO', texto_substituicao)
    
    # Montando o caminho completo
    caminho_completo = os.path.join(diretorio, nome_arquivo_final)
    
    return caminho_completo

##### CRIAR DATAFRAME A PARTIR DO ARQUIVO CSV SELECIONADO #####
from string import printable

try:
    df = pd.read_csv(arquivo_entrada, sep=',', encoding='utf-8')
    print(f"DataFrame criado com sucesso a partir do arquivo: {arquivo_entrada}")
except Exception as e:
    messagebox.showerror("Erro", f"Erro ao ler o arquivo CSV: {e}")
    sys.exit(1)

################################################################################
##### importar arquivos comuns que estão no diretório de trabalho
#caminho_diretorio_arquivos_comuns ="G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS"

import dis

# ==== Padronização definitiva de datas/horas ====
import re as _re_datefmt
_RE_YMD = _re_datefmt.compile(r'^\d{4}-\d{2}-\d{2}')
_RE_DMY = _re_datefmt.compile(r'^\d{2}/\d{2}/\d{4}')

def parse_datetime_safe(val):
    """
    Converte qualquer valor para pandas.Timestamp, detectando formato por valor.
    - ISO (YYYY-MM-DD[ HH:MM:SS]) -> dayfirst=False
    - BR  (DD/MM/YYYY[ HH:MM:SS]) -> dayfirst=True
    - datetime/Timestamp -> retornado coerced
    """
    if isinstance(val, (pd.Timestamp, datetime)):
        return pd.to_datetime(val, errors='coerce', dayfirst=True)
    s = str(val).strip()
    if _RE_YMD.match(s):
        return pd.to_datetime(s, errors='coerce', dayfirst=True)
    if _RE_DMY.match(s):
        return pd.to_datetime(s, errors='coerce', dayfirst=True)
    # Fallback conservador
    return pd.to_datetime(s, errors='coerce', dayfirst=True)

def parse_mixed_datetime_series(serie):
    """Aplica parse_datetime_safe elemento a elemento (suporta formatos mistos)."""
    return serie.apply(parse_datetime_safe)
# ================================================

######
def carregar_feriados():
    """
    Carrega dados de feriados nacionais (coluna 'date' como datetime64[ns]).
    Nunca converte 'date' para string dentro da função.
    """
    try:
        caminho_feriados = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\feriados.json"
        feriados = pd.read_json(caminho_feriados)

        # Garantir datetime real na coluna 'date'
        feriados['date'] = pd.to_datetime(feriados['date'], errors='coerce', dayfirst=True)

        print(f"📅 Feriados carregados: {len(feriados)}")
        # Para exibição, use uma cópia formatada
        _show = feriados.head().copy()
        _show['date'] = _show['date'].dt.strftime("%d/%m/%Y")
        print(_show)
        return feriados

    except Exception as e:
        print(f"⚠️ Erro ao carregar feriados: {e}")
        return pd.DataFrame(columns=['date','name','type'])
#####

def carregar_siglas_sabre():
    """
    Carrega e classifica siglas SABRE por tipo de atividade
    
    Returns:
        tuple: (lista_reservas, lista_plantoes, lista_treinamentos, lista_tipos_voo)
    """
    try:
        caminho_siglas = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\Siglas Sabre 1.xlsx"
        siglas_sabre = pd.read_excel(caminho_siglas, engine='openpyxl')
        
        # Usar arquivo JSON para reservas
        l_reservas = carregar_tipos_reserva()
        
        # Carregar tipos de voo do arquivo JSON
        l_tipos_voo = carregar_tipos_voo()
        
        l_plantoes = siglas_sabre[siglas_sabre['SIGLA'].str.startswith(('P', 'p'), na=False)]['SIGLA'].tolist()
        
        l_treinamentos = carregar_tipos_treinamentos()
        
        """
        l_treinamentos = [
            'ALA', 'ANC', 'ATR', 'AV', 'AVI', 'AVS', 'AVT', 'CA2', 'CA3',
            'CAA', 'CAE', 'CAP', 'CB2', 'CB3', 'CBA', 'CBE', 'CCL', 'CEA', 'CFI',
            'CI2', 'CI3', 'CIA', 'CIE', 'COL', 'CP2', 'CP3', 'CPA', 'CPE', 'CRM',
            'DGR', 'DH', 'DL', 'DOB', 'EGP', 'ENP', 'EPA', 'EPI', 'FIV',
            'G3', 'GCI', 'GF', 'GS', 'ICM', 'JJ', 'OPT', 'PC1', 'PC2', 'PC3',
            'PIP', 'PIV', 'PP1', 'PP2', 'PSM', 'REI', 'REQ',
            'SIT', 'SLC', 'SCL', 'SLF', 'T20', 'T30',
            'TAI', 'TEM', 'TFX', 'UA', 'UNI', 'V20', 'V30', 'VAE', 'VAT', 'VEB',
            'VFT', 'XEA', 'XQ2', 'XQ3'
        ]
        """

        print("📋 Siglas carregadas:")
        print(f"   • Reservas: {len(l_reservas)} - {l_reservas[:10]}{'...' if len(l_reservas) > 10 else ''}")
        print(f"   • Tipos de voo: {len(l_tipos_voo)} (do arquivo JSON)")
        print(f"   • Plantões: {len(l_plantoes)}")  
        print(f"   • Treinamentos: {len(l_treinamentos)}")
        
        return l_reservas, l_plantoes, l_treinamentos, l_tipos_voo
        
    except Exception as e:
        print(f"❌ Erro ao carregar siglas SABRE: {e}")
        # Fallback usando tipos de reserva e voo do JSON
        l_reservas_fallback = carregar_tipos_reserva()
        l_tipos_voo_fallback = carregar_tipos_voo()
        return l_reservas_fallback, [], [], l_tipos_voo_fallback

def carregar_tipos_treinamentos():
    
    try:
        # Primeiro tenta carregar do arquivo JSON local
        caminho_json_local = "tipos_treinamentos.json"
        if os.path.exists(caminho_json_local):
            with open(caminho_json_local, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                tipos = dados.get('tipos_treinamentos', [])
                print(f"📋 Tipos de treinamentos carregados do JSON local: {len(tipos)}")
                return tipos
        
        # Se não encontrar local, tenta o diretório comum
        caminho_json_comum = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\tipos_treinamentos.json"
        if os.path.exists(caminho_json_comum):
            with open(caminho_json_comum, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                tipos = dados.get('tipos_treinamentos', [])
                print(f"📋 Tipos de treinamentos carregados do JSON comum: {len(tipos)}")
                return tipos
        
        # Fallback: lista hardcoded
        print("⚠️ Arquivos JSON não encontrados, usando lista padrão")
        return [
            'ALA', 'ANC', 'ATR', 'AV', 'AVI', 'AVS', 'AVT', 'CA2', 'CA3',
            'CAA', 'CAE', 'CAP', 'CB2', 'CB3', 'CBA', 'CBE', 'CCL', 'CEA', 'CFI',
            'CI2', 'CI3', 'CIA', 'CIE', 'COL', 'CP2', 'CP3', 'CPA', 'CPE', 'CRM',
            'DGR', 'DH', 'DL', 'DOB', 'EGP', 'ENP', 'EPA', 'EPI', 'FIV',
            'G3', 'GCI', 'GF', 'GS', 'ICM', 'JJ', 'OPT', 'PC1', 'PC2', 'PC3',
            'PIP', 'PIV', 'PP1', 'PP2', 'PSM', 'REI', 'REQ',
            'SIT', 'SLC', 'SCL', 'SLF', 'T20', 'T30',
            'TAI', 'TEM', 'TFX', 'UA', 'UNI', 'V20', 'V30', 'VAE', 'VAT', 'VEB',
            'VFT', 'XEA', 'XQ2', 'XQ3', "R0", "RF1", "RF2", "RF3",
            "RF4", "RF5", "RF6", "RF7", "RF8", "RF9"
        ]
        
    except Exception as e:
        print(f"❌ Erro ao carregar tipos de treinamentos: {e}")
        return []

def carregar_tipos_reserva():
    """
    Carrega tipos de reserva do arquivo JSON criado especificamente
    
    Returns:
        list: Lista de códigos de reserva
    """
    
    try:
        # Primeiro tenta carregar do arquivo JSON local
        caminho_json_local = "tipos_reserva.json"
        if os.path.exists(caminho_json_local):
            with open(caminho_json_local, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                tipos = dados.get('tipos_reserva', [])
                print(f"📋 Tipos de reserva carregados do JSON local: {len(tipos)}")
                return tipos
        
        # Se não encontrar local, tenta o diretório comum
        caminho_json_comum = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\tipos_reserva.json"
        if os.path.exists(caminho_json_comum):
            with open(caminho_json_comum, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                tipos = dados.get('tipos_reserva', [])
                print(f"📋 Tipos de reserva carregados do JSON comum: {len(tipos)}")
                return tipos
        
        # Fallback: lista hardcoded
        print("⚠️ Arquivos JSON não encontrados, usando lista padrão")
        return [
            "R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10",
            "R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19", "R20",
            "R21", "R22", "R23", "R24", "RES", "REX", "R0", "RF1", "RF2", "RF3",
            "RF4", "RF5", "RF6", "RF7", "RF8", "RF9"
        ]
        
    except Exception as e:
        print(f"❌ Erro ao carregar tipos de reserva: {e}")
        return []

def carregar_tipos_plantao():
    """
    Carrega tipos de reserva do arquivo JSON criado especificamente
    
    Returns:
        list: Lista de códigos de reserva
    """
    
    try:
        # Primeiro tenta carregar do arquivo JSON local
        caminho_json_local = "tipos_plantao.json"
        if os.path.exists(caminho_json_local):
            with open(caminho_json_local, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                tipos = dados.get('tipos_reserva', [])
                print(f"📋 Tipos de Treinamento carregados do JSON local: {len(tipos)}")
                return tipos
        
        # Se não encontrar local, tenta o diretório comum
        caminho_json_comum = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\Treinamento.json"
        if os.path.exists(caminho_json_comum):
            with open(caminho_json_comum, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                tipos = dados.get('tipos_plantao', [])
                print(f"📋 Tipos de plantao carregados do JSON comum: {len(tipos)}")
                return tipos
        
        # Fallback: lista hardcoded
        print("⚠️ Arquivos JSON não encontrados, usando lista padrão")
        return [
            "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P10",
            "P11", "P12", "P13", "P14", "P15", "P16", "P17", "P18", "P19", "P20",
            "P21", "P22", "P23", "P24"
        ]
        
    except Exception as e:
        print(f"❌ Erro ao carregar tipos de reserva: {e}")
        return []

def carregar_tipos_voo():
    """
    Carrega tipos de voo do arquivo JSON
    
    Returns:
        list: Lista de códigos de atividades de voo
    """
    
    try:
        # Primeiro tenta carregar do diretório local
        caminho_json_local = r"G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\tipos_voo.json"
        
        if os.path.exists(caminho_json_local):
            with open(caminho_json_local, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                tipos = dados.get('tipos_voo', [])
                print(f"✈️ Tipos de voo carregados do JSON local: {len(tipos)}")
                return tipos
        
        # Se não encontrar local, tenta o diretório ARQUIVOS COMUNS
        caminho_json_comum = r"G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS\tipos_voo.json"
        if os.path.exists(caminho_json_comum):
            with open(caminho_json_comum, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                tipos = dados.get('tipos_voo', [])
                print(f"✈️ Tipos de voo carregados do diretório ARQUIVOS COMUNS: {len(tipos)}")
                return tipos
        
        # Se não encontrou em nenhum lugar
        print("❌ Arquivo tipos_voo.json não encontrado em nenhum diretório")
        raise FileNotFoundError("Arquivo tipos_voo.json não encontrado")
        
    except Exception as e:
        print(f"❌ Erro ao carregar tipos de voo: {e}")
        raise

################################################################################

carregar_feriados()
carregar_siglas_sabre()
carregar_tipos_voo()

################################################################################
feriados = carregar_feriados()
# Coloque este bloco logo após o carregamento:
if isinstance(feriados, pd.DataFrame) and not feriados.empty:
    feriados['date'] = pd.to_datetime(feriados['date'], errors='coerce', dayfirst=True)
    datas_feriado = set(feriados['date'].dt.date)
    datas_vespera = set((feriados['date'] - pd.Timedelta(days=1)).dt.date)
    print(f"✅ Feriados carregados: {len(datas_feriado)} datas")
    print(f"✅ Vésperas carregadas: {len(datas_vespera)} datas")
else:
    datas_feriado = set()
    datas_vespera = set()
    print("⚠️ Nenhum feriado carregado - usando conjuntos vazios")
print(feriados)

################################################################################
tipos_voo = carregar_tipos_voo()
#print(tipos_voo)

################################################################################
siglas_sabre = carregar_siglas_sabre()
print(siglas_sabre)   

################################################################################
import dis

def formatar_timedelta(td):
    """
    Formata um objeto timedelta como HH:MM:SS.
    """
    total_seconds = int(td.total_seconds())
    horas = total_seconds // 3600
    minutos = (total_seconds % 3600) // 60
    segundos = total_seconds % 60
    return f"{horas:02}:{minutos:02}:{segundos:02}"

def classificar_horas_especiais(checkin, checkout, feriados_list=None):
    """
    Classifica as horas trabalhadas em categorias específicas.
    
    Regras:
    1. Noturno: 18:00 às 06:00
    2. Especiais:
       - Domingos até às 21:00
       - Feriados até às 21:00
       - Sábados a partir das 21:00
       - Vésperas de feriado a partir das 21:00
    
    Args:
        checkin (str): Data/hora de entrada no formato 'YYYY-MM-DD HH:MM:SS'
        checkout (str): Data/hora de saída no formato 'YYYY-MM-DD HH:MM:SS'
        feriados_list (list): Lista de datas de feriados no formato 'YYYY-MM-DD'
    
    Returns:
        dict: Horas classificadas por categoria
    """
    
    # Converter strings para datetime
    #dt_checkin = datetime.strptime(checkin, '%Y-%m-%d %H:%M')
    #dt_checkout = datetime.strptime(checkout, '%Y-%m-%d %H:%M')

#############################################

   # 🔍 DEBUG: Verificar dados recebidos
    print(f"🔍 DEBUG - Parâmetros recebidos:")
    print(f"   • checkin: {checkin} (tipo: {type(checkin)})")
    print(f"   • checkout: {checkout} (tipo: {type(checkout)})")
    print(f"   • feriados_list: {feriados_list} (tipo: {type(feriados_list)})")
    
    # Verificar se são strings
    if isinstance(checkin, str):
       print(f"   • checkin string: '{checkin}'")
    if isinstance(checkout, str):
       print(f"   • checkout string: '{checkout}'")
    
    # Verificar se são datetime
    if hasattr(checkin, 'strftime'):
       print(f"   • checkin datetime: {checkin.strftime('%Y-%m-%d %H:%M:%S')}")
    if hasattr(checkout, 'strftime'):
       print(f"   • checkout datetime: {checkout.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Converter strings para datetime
    try:
        checkin = parse_datetime_safe(checkin)
        checkout = parse_datetime_safe(checkout)
        print(f"✅ Conversão bem-sucedida:")
        print(f"   • checkin convertido: {checkin}")
        print(f"   • checkout convertido: {checkout}")
    except Exception as e:
        print(f"❌ Erro na conversão: {e}")
        raise ValueError(f"Erro na conversão de datas: {e}")
    
    # Validação final
    if pd.isnull(checkin) or pd.isnull(checkout):
        print(f"❌ Valores nulos detectados!")
        raise ValueError(f"Checkin ou Checkout inválido: {checkin} - {checkout}")
    
########################################

    # como verificar se checkin e checkout são válidos
    #checkin = pd.to_datetime(checkin, format="%Y-%m-%d %H:%M:%S", dayfirst=True)
    #checkout = pd.to_datetime(checkout, format="%Y-%m-%d %H:%M:%S", dayfirst=True)
    checkin = parse_datetime_safe(checkin)
    checkout = parse_datetime_safe(checkout)
    
    if pd.isnull(checkin) or pd.isnull(checkout):
        raise ValueError(f"Checkin ou Checkout inválido: {checkin} - {checkout}")
    print(f"🔍 Classificando horas especiais de {checkin} até {checkout}")
    # Verificar se checkin e checkout são válidos
    if not isinstance(checkin, datetime) or not isinstance(checkout, datetime):
        raise ValueError("Checkin e Checkout devem ser objetos datetime válidos")

    # Usar lista de feriados fornecida ou carregar da variável global
    if feriados_list is None:
        try:
            # Tentar usar a variável global feriados
            if 'feriados' in globals() and isinstance(feriados, pd.DataFrame) and not feriados.empty:
                feriados_list = feriados['date'].dt.strftime('%Y-%m-%d').tolist()
                print(f"📅 Usando feriados da variável global: {len(feriados_list)}")
            else:
                print("⚠️ Nenhum feriado disponível, usando lista vazia")
                feriados_list = []
        except Exception as e:
            print(f"⚠️ Erro ao acessar feriados: {e}")
            feriados_list = []
    
    # Converter feriados para objetos date
    feriados_dates = []
    for f in feriados_list:
        try:
            feriados_dates.append(datetime.strptime(f, '%Y-%m-%d').date())
        except:
            continue
    
    print(f"📅 Processando com {len(feriados_dates)} feriados")

    # Verificar se é véspera de feriado
    def is_vespera_feriado(data):
        data_seguinte = data + timedelta(days=1)
        return data_seguinte.date() in feriados_dates
    
    # Inicializar contadores como timedelta
    resultado = {
        'hora_diurna_normal': timedelta(),
        'hora_noturna_normal': timedelta(),
        'hora_especial_diurna': timedelta(),
        'hora_especial_noturna': timedelta(),
        'detalhes': []
    }
    
    # Processar por períodos definidos pelos marcos horários
    atual = checkin #dt_checkin
    
    while atual < checkout: #dt_checkout:
        # Determinar próximo marco horário relevante
        proximos_marcos = []
        
        # Marco das 18:00 (início noturno)
        marco_18h = atual.replace(hour=18, minute=0, second=0, microsecond=0)
        if marco_18h > atual:
            proximos_marcos.append(marco_18h)
        elif marco_18h <= atual:
            # Próximo dia às 18:00
            marco_18h = marco_18h + timedelta(days=1)
            proximos_marcos.append(marco_18h)
        
        # Marco das 06:00 (fim noturno)
        marco_06h = atual.replace(hour=6, minute=0, second=0, microsecond=0)
        if marco_06h > atual:
            proximos_marcos.append(marco_06h)
        elif marco_06h <= atual:
            # Próximo dia às 06:00
            marco_06h = marco_06h + timedelta(days=1)
            proximos_marcos.append(marco_06h)
        
        # Marco das 21:00 (limite especial domingo/feriado ou início especial sábado/véspera)
        marco_21h = atual.replace(hour=21, minute=0, second=0, microsecond=0)
        if marco_21h > atual:
            proximos_marcos.append(marco_21h)
        elif marco_21h <= atual:
            # Próximo dia às 21:00
            marco_21h = marco_21h + timedelta(days=1)
            proximos_marcos.append(marco_21h)
        
        # Marco da meia-noite (mudança de dia)
        marco_00h = atual.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        if marco_00h > atual:
            proximos_marcos.append(marco_00h)
        
        # Escolher o próximo marco mais próximo (ou final do período)
        proximos_marcos.append(checkout)
        proxima = min(proximos_marcos)
        
        # Calcular duração do período atual como timedelta
        duracao = proxima - atual
        
        # Determinar tipo de hora baseado no horário de INÍCIO do período
        hora_atual = atual.hour
        dia_semana = atual.weekday()  # 0=segunda, 6=domingo
        data_atual = atual.date()
        
        # Verificar se é período noturno (18:00 às 06:00)
        is_noturno = hora_atual >= 18 or hora_atual < 6
        
        # Verificar se é período especial
        is_especial = False
        motivo_especial = ""
        
        # Domingo (até às 21:00)
        if dia_semana == 6 and hora_atual < 21:
            is_especial = True
            motivo_especial = "Domingo"
        
        # Feriado (até às 21:00)
        elif data_atual in feriados_dates and hora_atual < 21:
            is_especial = True
            motivo_especial = "Feriado"
        
        # Sábado a partir das 21:00
        elif dia_semana == 5 and hora_atual >= 21:
            is_especial = True
            motivo_especial = "Sábado após 21:00"
        
        # Véspera de feriado a partir das 21:00
        elif is_vespera_feriado(atual) and hora_atual >= 21:
            is_especial = True
            motivo_especial = "Véspera de feriado após 21:00"
        
        # Classificar em uma das 4 categorias
        if is_noturno and is_especial:
            resultado['hora_especial_noturna'] += duracao
            categoria = "Hora Especial Noturna"
        elif is_noturno:
            resultado['hora_noturna_normal'] += duracao
            categoria = "Hora Noturna Normal"
        elif is_especial:
            resultado['hora_especial_diurna'] += duracao
            categoria = "Hora Especial Diurna"
        else:
            resultado['hora_diurna_normal'] += duracao
            categoria = "Hora Diurna Normal"
        
        # Adicionar aos detalhes
        resultado['detalhes'].append({
            'inicio': atual.strftime('%Y-%m-%d %H:%M'),
            'fim': proxima.strftime('%Y-%m-%d %H:%M'),
            'duracao': formatar_timedelta(duracao),
            'categoria': categoria,
            'motivo_especial': motivo_especial if is_especial else None
        })
        
        # Avançar para próximo período
        atual = proxima
    
    return resultado

# Teste corrigido

# ===================== UNIVERSAL DEG + DATAS (v5 final) =====================
from pathlib import Path as _P
from datetime import datetime as _DT
import re as _R
import tkinter as _TK
from tkinter import filedialog as _FD
import pandas as _PD
from pandas import DataFrame as _DF

# 1) Seleção única + nomes com timestamp
_SEL = None  # type: _P | None
def select_working_directory() -> str:
    global _SEL
    _root = _TK.Tk(); _root.withdraw(); _root.attributes("-topmost", True)
    caminho = _FD.askopenfilename(title="Selecione o CSV de entrada", filetypes=[("CSV","*.csv"),("Todos","*.*")])
    try: _root.destroy()
    except Exception: pass
    if not caminho: raise SystemExit("Nenhum arquivo selecionado. Operação cancelada.")
    _SEL = _P(caminho).resolve()
    outdir = _P(str(_SEL.parent).replace("Escalas_Executadas","Auditoria_Calculos"))
    outdir.mkdir(parents=True, exist_ok=True)
    return str(outdir)

def select_input_file() -> str:
    if _SEL is None: raise RuntimeError("select_input_file() antes de select_working_directory().")
    return _SEL.name

_RX = _R.compile(r"(?:_(?:PRIMEIRA|SEGUNDA|TERCEIRA|QUARTA)_VERSAO)(?:_\d{8}(?:_\d{6})?)?$", _R.IGNORECASE)
def _clean(stem:str)->str:
    while True:
        n = _RX.sub("", stem)
        if n == stem: return n
        stem = n

def montar_caminho_arquivo(working_directory:str, input_file:str, sufixo:str, ext:str=".csv", add_timestamp:bool=True)->str:
    base = _P(working_directory); base.mkdir(parents=True, exist_ok=True)
    stem = _clean(_P(input_file).stem)
    ts = f"_{_DT.now().strftime('%Y%m%d_%H%M%S')}" if add_timestamp else ""
    return str(base / f"{stem}_{sufixo}{ts}{ext}")

# 2) Uniformização de datas ao SALVAR (sem apagar valores não reconhecidos)
_DATE_COLS = ("Checkin","Start","End","Checkout")
_ISO_RX = _R.compile(r"^\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(:\d{2})?\s*$")
_DDMM_RX = _R.compile(r"^\s*\d{1,2}/\d{1,2}/\d{4}\s+\d{2}:\d{2}(:\d{2})?\s*$")
_EMPTY_RX = _R.compile(r"^\s*$|^-\s*$|^(nan|NaN|null|None)$")

def _fmt_dates(df:_PD.DataFrame)->_PD.DataFrame:
    out = df.copy()
    for col in _DATE_COLS:
        if col not in out.columns: continue
        s = out[col].astype(str)
        empty = s.str.match(_EMPTY_RX, na=True)
        iso   = s.str.match(_ISO_RX, na=False)
        ddmm  = s.str.match(_DDMM_RX, na=False)
        # default: keep original text
        out[col] = s

        # ISO → parse seguro
        if iso.any():
            p = _PD.to_datetime(s[iso], errors="coerce", dayfirst=False)
            ok = p.notna()
            out.loc[iso & ok, col] = p[ok].dt.strftime("%d/%m/%Y %H:%M")
        # DD/MM → parse com dayfirst
        if ddmm.any():
            p = _PD.to_datetime(s[ddmm], errors="coerce", dayfirst=True)
            ok = p.notna()
            out.loc[ddmm & ok, col] = p[ok].dt.strftime("%d/%m/%Y %H:%M")
        # vazios mantêm
        out.loc[empty, col] = s[empty]
    return out

_APOS_COLS = [
    "Activity","Id_Leg","Checkin","Start","End","Checkout",
    "Tempo Apos Corte Diurno","Tempo Apos Corte Noturno",
    "Tempo Apos Corte Especial Diurno","Tempo Apos Corte Especial Noturno",
]

if not hasattr(_DF, "_v5_to_csv"):
    _orig_to_csv = _DF.to_csv
    def _to_csv_v5(self, path_or_buf=None, *args, **kwargs):
        try: name = str(path_or_buf) if path_or_buf is not None else ""
        except Exception: name = ""
        df = self.copy()
        if "_APOS_CORTE" in name:
            for c in _APOS_COLS:
                if c not in df.columns: df[c] = ""
            for extra in ("Dep","Arr","Tempo Apos Corte"):
                if extra in df.columns: df = df.drop(columns=[extra])
            df = df.reindex(columns=_APOS_COLS)
        df = _fmt_dates(df)  # aplica datas uniformes
        return _orig_to_csv(df, path_or_buf, *args, **kwargs)
    _DF.to_csv = _to_csv_v5
    _DF._v5_to_csv = True

# ===================== FIM UNIVERSAL DEG + DATAS (v5 final) =====================


if __name__ == "__main__":
    # Exemplo com o caso apresentado
    #checkin = "2017-11-15 04:00:00"
    #checkout = "2017-11-16 16:00:00"
    
    # Carregar feriados se disponível
    try:
        feriados_para_teste = carregar_feriados()
        if isinstance(feriados_para_teste, pd.DataFrame) and not feriados_para_teste.empty:
            lista_feriados = feriados_para_teste['date'].dt.strftime('%Y-%m-%d').tolist()
        else:
            lista_feriados = []
    except:
        lista_feriados = []
    
    # Definir checkin e checkout usando o primeiro registro do DataFrame df
    checkin = df.loc[0, 'Checkin']
    checkout = df.loc[0, 'Checkout']

    resultado = classificar_horas_especiais(checkin, checkout, lista_feriados)
    
    def exibir_classificacao(resultado):
        print("Resumo das Horas Classificadas:")
        for k, v in resultado.items():
            if k != 'detalhes':
               print(f"{k}: {v}")
        print("\nDetalhes dos Períodos:")
        for d in resultado['detalhes']:
           print(f"{d['inicio']} até {d['fim']} | {d['duracao']} | {d['categoria']} | {d.get('motivo_especial', '')}")

    exibir_classificacao(resultado)

################################################################################
##### CÁLCULO DE DIURNO E NOTURNO #####
# Criar regras para iniciar os cálculos

def calcular_diurno_noturno(checkin, start, end, checkout):
    """
    Calcula o tempo total em períodos diurno e noturno entre checkin e checkout.

    Args:
        checkin (str): Horário de entrada.
        start (str): Início da atividade (referência, mas não usado no cálculo).
        end (str): Fim da atividade (referência, mas não usado no cálculo).
        checkout (str): Horário de saída.

    Returns:
        tuple: (tempo_diurno, tempo_noturno) como timedelta.
    """
    # Converte strings para datetime
    checkin_dt = datetime.strptime(checkin, "%d/%m/%Y %H:%M")
    start_dt = datetime.strptime(start, "%d/%m/%Y %H:%M")
    end_dt = datetime.strptime(end, "%d/%m/%Y %H:%M")
    checkout_dt = datetime.strptime(checkout, "%d/%m/%Y %H:%M")

    #if checkout_dt < checkin_dt:
    #    raise ValueError("Checkout anterior ao checkin.")

    tempo_diurno = timedelta()
    tempo_noturno = timedelta()

    atual = checkin_dt
    while atual < checkout_dt:
        proximo = atual + timedelta(minutes=1)
        hora = atual.time()
        if time(6, 0) <= hora < time(18, 0):
            tempo_diurno += timedelta(minutes=1)
        else:
            tempo_noturno += timedelta(minutes=1)
        atual = proximo

    return tempo_diurno, tempo_noturno

################################################################################
checkin = datetime.strptime("2023-10-01 17:55", "%Y-%m-%d %H:%M")
start = datetime.strptime("2023-10-01 18:05", "%Y-%m-%d %H:%M")
end = datetime.strptime("2023-10-02 05:55", "%Y-%m-%d %H:%M")
checkout = datetime.strptime("2023-10-02 06:05", "%Y-%m-%d %H:%M")

# Converter para string no formato esperado pela função
checkin_str = checkin.strftime("%d/%m/%Y %H:%M")
start_str = start.strftime("%d/%m/%Y %H:%M")
end_str = end.strftime("%d/%m/%Y %H:%M")
checkout_str = checkout.strftime("%d/%m/%Y %H:%M")

# Calcular os períodos diurno e noturno
tempo_diurno, tempo_noturno = calcular_diurno_noturno(checkin_str, start_str, end_str, checkout_str)

# Exibir os resultados originais
print(f"Check-in: {checkin}")
print(f"Início: {start}")
print(f"Fim: {end}")
print(f"Check-out: {checkout}")

print(f"Tempo diurno: {tempo_diurno}")
print(f"Tempo noturno: {tempo_noturno}")

################################################################################
##### Realizar loop no dataframe e alocar 'F' para feriado e 'VF' para vesperas
# Garante que as colunas existem
# Corrigir o import e garantir que feriados seja um DataFrame
# Corrigir o import e garantir que feriados seja um DataFrame
from datetime import datetime

# Verificar o estado da variável feriados
print(f"Tipo de feriados: {type(feriados)}")
print(f"Conteúdo: {feriados}")

# Recarregar se necessário
feriados = carregar_feriados()
print(f"Feriados recarregados: {type(feriados)}")

# Garantir que as colunas existem
for col in ['Feriado', 'Vespera']:
    if col not in df.columns:
        df[col] = ''

# Certifica que as colunas de data estão em datetime
for col in ['Checkin', 'Start', 'End', 'Checkout']:
    if df[col].dtype == 'object':
        df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)

# Verificar se feriados é um DataFrame válido
if isinstance(feriados, pd.DataFrame) and not feriados.empty:
    # Pré-calcula os conjuntos de datas de feriado e vespera para eficiência
    datas_feriado = set(feriados['date'].dt.date)
    datas_vespera = set((feriados['date'] - pd.Timedelta(days=1)).dt.date)
    
    print(f"✅ Feriados carregados: {len(datas_feriado)} datas")
    print(f"✅ Vésperas carregadas: {len(datas_vespera)} datas")
else:
    # Se não há feriados, criar conjuntos vazios
    datas_feriado = set()
    datas_vespera = set()
    print("⚠️ Nenhum feriado carregado - usando conjuntos vazios")

print(f"🔄 Processando {len(df)} registros para classificar feriados e vésperas...")

# Criar colunas para dias da semana individuais
colunas_dias = ['Checkin_Dia_Semana', 'Start_Dia_Semana', 'End_Dia_Semana', 'Checkout_Dia_Semana']
for col in colunas_dias:
    if col not in df.columns:
        df[col] = None

# Processar cada linha do DataFrame
for i, row in df.iterrows():
    eh_feriado = False
    eh_vespera = False
    
    # Verificar cada coluna de data
    for col in ['Checkin', 'Start', 'End', 'Checkout']:
        data = row[col]
        if pd.notnull(data):
            data_date = data.date()
            if data_date in datas_feriado:
                eh_feriado = True
            if data_date in datas_vespera:
                eh_vespera = True
    
    # Atribuir valores booleanos
    df.at[i, 'Feriado'] = eh_feriado
    df.at[i, 'Vespera'] = eh_vespera
    
    # Colocar o dia da semana no formato numérico em colunas separadas
    for col_dia in ['Checkin', 'Start', 'End', 'Checkout']:
        valor = row[col_dia]
        coluna_dia_semana = f"{col_dia}_Dia_Semana"
        
        if pd.notnull(valor):
            df.at[i, coluna_dia_semana] = valor.dayofweek
        else:
            df.at[i, coluna_dia_semana] = None

print(f"✅ Processamento concluído!")

# Estatísticas
total_feriados = df['Feriado'].sum()
total_vesperas = df['Vespera'].sum()

print(f"\n📊 ESTATÍSTICAS:")
print(f"   • Registros com feriados: {total_feriados}")
print(f"   • Registros com vésperas: {total_vesperas}")
print(f"   • Total de registros processados: {len(df)}")

# Verificar se há registros com feriados ou vésperas para exibir
if total_feriados > 0 or total_vesperas > 0:
    print(f"\n📋 PRIMEIROS 5 REGISTROS COM FERIADOS OU VÉSPERAS:")
    registros_especiais = df[df['Feriado'] | df['Vespera']].head()
    colunas_exibir = ['Checkin', 'Start', 'End', 'Checkout', 'Feriado', 'Vespera'] + colunas_dias
    print(registros_especiais[colunas_exibir].to_string())
else:
    print("\n📋 Nenhum registro com feriados ou vésperas encontrado.")

# Verificar se a variável feriados precisa ser recarregada
print(f"\n🔍 DIAGNÓSTICO DA VARIÁVEL FERIADOS:")
print(f"   • Tipo: {type(feriados)}")
if hasattr(feriados, 'shape'):
   print(f"   • Formato: {feriados.shape}")
elif hasattr(feriados, '__len__'):
   print(f"   • Tamanho: {len(feriados)}")
    
# Se necessário, recarregar feriados
if not isinstance(feriados, pd.DataFrame) or feriados.empty:
    print("\n🔄 Recarregando feriados...")
    feriados = carregar_feriados()
    print(f"✅ Feriados recarregados: {type(feriados)}")

print(f"\n🔧 COLUNAS CRIADAS:")
print(f"   • Feriado (booleano)")
print(f"   • Vespera (booleano)")
for col in colunas_dias:
   print(f"   • {col} (0=Segunda, 1=Terça, ..., 6=Domingo)")# mostrar o Dataframe atualizado com as novas colunas e apenas os que têm feriado ou véspera

################################################################################
def sabado_domingo_vespera(checkin, start, end, checkout):
    """
    Verifica se o check-in ou check-out ocorre em um sábado, domingo ou véspera de feriado.
    
    Args:
        checkin (str): Horário de entrada.
        start (str): Início da atividade.
        end (str): Fim da atividade.
        checkout (str): Horário de saída.

    Returns:
        bool: True se for sábado, domingo ou véspera de feriado, False caso contrário.
    """
    # Converte strings para datetime
    checkin_dt = datetime.strptime(checkin, "%d/%m/%Y %H:%M")
    checkout_dt = datetime.strptime(checkout, "%d/%m/%Y %H:%M")

    # Verifica se é sábado ou domingo
    if checkin_dt.weekday() in [5, 6]:  # 5 = Sábado, 6 = Domingo
        return True

    # Verifica se é véspera de feriado
    for _, row in feriados.iterrows():
        feriado_dt = row['date']
        if feriado_dt - timedelta(days=1) == checkin_dt.date():
            return True

    return False

################################################################################
def verificar_horario_especial(checkin, start, end, checkout, feriados_df):
    """
    Verifica se qualquer dos horários (Checkin, Start, End, Checkout) se enquadra em:
    - Sábado após 21:00
    - Domingo (qualquer horário)
    - Véspera de feriado após 21:00
    - Feriado (qualquer horário)
    
    Args:
        checkin (datetime): Horário de entrada
        start (datetime): Início da atividade
        end (datetime): Fim da atividade
        checkout (datetime): Horário de saída
        feriados_df (DataFrame): DataFrame com feriados
        
    Returns:
        dict: Informações detalhadas sobre horários especiais encontrados
    """
    
    def eh_feriado(data_verificar, feriados_df):
        #Verifica se a data é feriado"""
        if feriados_df.empty:
            return False
        
        if isinstance(feriados, pd.DataFrame) and not feriados.empty:
            feriados['date'] = pd.to_datetime(feriados['date'], errors='coerce', dayfirst=True)
            datas_feriado = set(feriados['date'].dt.date)
            datas_vespera = set((feriados['date'] - pd.Timedelta(days=1)).dt.date)
        else:
            datas_feriado = set()
            datas_vespera = set()
        
        data_str = data_verificar.date()
        feriados_dates = feriados_df['date'].dt.date
        return data_str in feriados_dates.values
    
    def eh_vespera_feriado(data_verificar, feriados_df):
        #Verifica se a data é véspera de feriado"""
        if feriados_df.empty:
            return False
    
        if isinstance(feriados, pd.DataFrame) and not feriados.empty:
            feriados['date'] = pd.to_datetime(feriados['date'], errors='coerce', dayfirst=True)
            datas_feriado = set(feriados['date'].dt.date)
            datas_vespera = set((feriados['date'] - pd.Timedelta(days=1)).dt.date)
        else:
            datas_feriado = set()
            datas_vespera = set()

        data_amanha = data_verificar.date() + timedelta(days=1)
        feriados_dates = feriados_df['date'].dt.date
        
        return data_amanha in feriados_dates.values
    
    def analisar_horario(dt, nome_horario):
        #Analisa um horário específico"""
        if pd.isna(dt):
            return None
            
        dia_semana = dt.weekday()  # 0=Segunda, 1=Terça, ..., 5=Sábado, 6=Domingo
        hora = dt.hour
        
        resultado = {
            'horario': nome_horario,
            'datetime': dt,
            'dia_semana': dia_semana,
            'hora': hora,
            'eh_especial': False,
            'motivos': []
        }
        
        # 1. DOMINGO (qualquer horário)
        if dia_semana == 6:  # Domingo
            resultado['eh_especial'] = True
            resultado['motivos'].append('Domingo')
        
        # 2. SÁBADO APÓS 21:00
        elif dia_semana == 5 and hora >= 21:  # Sábado após 21:00
            resultado['eh_especial'] = True
            resultado['motivos'].append('Sábado após 21:00')
        
        # 3. FERIADO (qualquer horário)
        elif eh_feriado(dt, feriados_df):
            resultado['eh_especial'] = True
            resultado['motivos'].append('Feriado')
        
        # 4. VÉSPERA DE FERIADO APÓS 21:00
        elif eh_vespera_feriado(dt, feriados_df) and hora >= 21:
            resultado['eh_especial'] = True
            resultado['motivos'].append('Véspera de feriado após 21:00')
        
        return resultado
    
    # Analisar todos os horários
    horarios_analisados = []
    
    for nome, dt in [('Checkin', checkin), ('Start', start), ('End', end), ('Checkout', checkout)]:
        analise = analisar_horario(dt, nome)
        if analise:
            horarios_analisados.append(analise)
    
    # Resumo geral
    tem_horario_especial = any(h['eh_especial'] for h in horarios_analisados)
    motivos_encontrados = []
    for h in horarios_analisados:
        if h['eh_especial']:
            motivos_encontrados.extend(h['motivos'])
    
    motivos_unicos = list(set(motivos_encontrados))
    
    return {
        'tem_horario_especial': tem_horario_especial,
        'motivos_especiais': motivos_unicos,
        'detalhes_por_horario': horarios_analisados,
        'total_horarios_especiais': sum(1 for h in horarios_analisados if h['eh_especial'])
    }

def aplicar_classificacao_especial_ao_dataframe(df, feriados_df):
    """
    Aplica classificação de horários especiais ao DataFrame completo
    """
    
    print("🔍 APLICANDO CLASSIFICAÇÃO DE HORÁRIOS ESPECIAIS...")
    print("=" * 60)
    
    # Criar novas colunas
    colunas_novas = [
        'Tem_Horario_Especial',
        'Motivos_Especiais',
        'Checkin_Especial',
        'Start_Especial', 
        'End_Especial',
        'Checkout_Especial',
        'Total_Horarios_Especiais'
    ]
    
    for coluna in colunas_novas:
        if coluna not in df.columns:
            if 'Especial' in coluna and coluna != 'Motivos_Especiais':
                df[coluna] = False
            elif coluna == 'Total_Horarios_Especiais':
                df[coluna] = 0
            else:
                df[coluna] = ''
    
    print(f"🔄 Processando {len(df)} registros...")
    
    # Contadores para estatísticas
    total_com_especial = 0
    motivos_stats = {}
    
    # Aplicar análise linha por linha
    for index, row in df.iterrows():
        try:
            # Verificar horários especiais
            resultado = verificar_horario_especial(
                row['Checkin'], 
                row['Start'], 
                row['End'], 
                row['Checkout'],
                feriados_df
            )
            
            # Atribuir resultados ao DataFrame
            df.at[index, 'Tem_Horario_Especial'] = resultado['tem_horario_especial']
            df.at[index, 'Motivos_Especiais'] = ', '.join(resultado['motivos_especiais'])
            df.at[index, 'Total_Horarios_Especiais'] = resultado['total_horarios_especiais']
            
            # Marcar horários específicos como especiais
            for detalhe in resultado['detalhes_por_horario']:
                coluna_especial = f"{detalhe['horario']}_Especial"
                if coluna_especial in df.columns:
                    df.at[index, coluna_especial] = detalhe['eh_especial']
            
            # Estatísticas
            if resultado['tem_horario_especial']:
                total_com_especial += 1
                for motivo in resultado['motivos_especiais']:
                    motivos_stats[motivo] = motivos_stats.get(motivo, 0) + 1
            
        except Exception as e:
            print(f"❌ Erro no registro {index}: {e}")
            continue
    
    print(f"✅ Análise concluída!")
    print(f"📊 Registros com horários especiais: {total_com_especial}/{len(df)} ({100*total_com_especial/len(df):.1f}%)")
    
    print("\n📋 ESTATÍSTICAS POR MOTIVO:")
    for motivo, count in motivos_stats.items():
       print(f"   • {motivo}: {count} registros")
    
    return df

################################################################################
# Teste da função corrigida com vários cenários
print("🧪 TESTE DA VERIFICAÇÃO DE HORÁRIOS ESPECIAIS")
print("=" * 70)

# Carregar feriados para teste
feriados_teste = carregar_feriados()

# Cenário 1: Domingo
print("\n📋 CENÁRIO 1: DOMINGO")
checkin_domingo = datetime.strptime("2023-10-01 10:00", "%Y-%m-%d %H:%M")  # Domingo 10:00
start_domingo = datetime.strptime("2023-10-01 11:00", "%Y-%m-%d %H:%M")
end_domingo = datetime.strptime("2023-10-01 15:00", "%Y-%m-%d %H:%M")
checkout_domingo = datetime.strptime("2023-10-01 16:00", "%Y-%m-%d %H:%M")

resultado1 = verificar_horario_especial(checkin_domingo, start_domingo, end_domingo, checkout_domingo, feriados_teste)
print(f"✅ Tem horário especial: {resultado1['tem_horario_especial']}")
print(f"✅ Motivos: {resultado1['motivos_especiais']}")

# Cenário 2: Sábado após 21:00
print("\n📋 CENÁRIO 2: SÁBADO APÓS 21:00")
checkin_sab = datetime.strptime("2023-09-30 22:00", "%Y-%m-%d %H:%M")  # Sábado 22:00
start_sab = datetime.strptime("2023-09-30 23:00", "%Y-%m-%d %H:%M")
end_sab = datetime.strptime("2023-10-01 01:00", "%Y-%m-%d %H:%M")
checkout_sab = datetime.strptime("2023-10-01 02:00", "%Y-%m-%d %H:%M")

resultado2 = verificar_horario_especial(checkin_sab, start_sab, end_sab, checkout_sab, feriados_teste)
print(f"✅ Tem horário especial: {resultado2['tem_horario_especial']}")
print(f"✅ Motivos: {resultado2['motivos_especiais']}")

# Cenário 3: Dia normal (sem especiais)
print("\n📋 CENÁRIO 3: DIA NORMAL")
checkin_normal = datetime.strptime("2023-10-03 08:00", "%Y-%m-%d %H:%M")  # Terça-feira 08:00
start_normal = datetime.strptime("2023-10-03 09:00", "%Y-%m-%d %H:%M")
end_normal = datetime.strptime("2023-10-03 17:00", "%Y-%m-%d %H:%M")
checkout_normal = datetime.strptime("2023-10-03 18:00", "%Y-%m-%d %H:%M")

resultado3 = verificar_horario_especial(checkin_normal, start_normal, end_normal, checkout_normal, feriados_teste)
print(f"✅ Tem horário especial: {resultado3['tem_horario_especial']}")
print(f"✅ Motivos: {resultado3['motivos_especiais']}")

# Cenário 4: Véspera de feriado após 21:00 (se houver feriados carregados)
if not feriados_teste.empty:
    print("\n📋 CENÁRIO 4: TESTE COM FERIADOS CARREGADOS")
    primeiro_feriado = feriados_teste.iloc[0]['date']
    vespera = primeiro_feriado - timedelta(days=1)
    
    checkin_vespera = vespera.replace(hour=22, minute=0)  # 22:00 da véspera
    start_vespera = vespera.replace(hour=23, minute=0)
    end_vespera = primeiro_feriado.replace(hour=1, minute=0)
    checkout_vespera = primeiro_feriado.replace(hour=2, minute=0)
    
    print(f"Feriado: {primeiro_feriado.date()}")
    print(f"Véspera: {vespera.date()} 22:00")
    
    resultado4 = verificar_horario_especial(checkin_vespera, start_vespera, end_vespera, checkout_vespera, feriados_teste)
    print(f"✅ Tem horário especial: {resultado4['tem_horario_especial']}")
    print(f"✅ Motivos: {resultado4['motivos_especiais']}")

print("\n🎯 TESTE CONCLUÍDO!")

################################################################################
# Aplicar classificação especial ao DataFrame real
print("🚀 APLICANDO CLASSIFICAÇÃO ESPECIAL AO DATAFRAME COMPLETO")
print("=" * 70)

# Verificar se as colunas de data existem e converter se necessário
colunas_necessarias = ['Checkin', 'Start', 'End', 'Checkout']
for coluna in colunas_necessarias:
    if coluna in df.columns:
        if df[coluna].dtype == 'object':
            print(f"🔄 Convertendo coluna '{coluna}' para datetime...")
            df[coluna] = pd.to_datetime(df[coluna], errors='coerce', dayfirst=True)

# Aplicar classificação especial
df_com_especiais = aplicar_classificacao_especial_ao_dataframe(df.copy(), feriados)

# Mostrar alguns exemplos
print("\n📋 PRIMEIROS 5 REGISTROS COM CLASSIFICAÇÃO ESPECIAL:")
colunas_exibir = ['Checkin', 'Start', 'End', 'Checkout', 'Tem_Horario_Especial', 'Motivos_Especiais', 'Total_Horarios_Especiais']
#print(df_com_especiais[colunas_exibir].head())

# Análise detalhada dos registros especiais
registros_especiais = df_com_especiais[df_com_especiais['Tem_Horario_Especial'] == True]
if len(registros_especiais) > 0:
   print(f"\n🔍 ENCONTRADOS {len(registros_especiais)} REGISTROS COM HORÁRIOS ESPECIAIS:")
   print("\n📊 PRIMEIROS 3 REGISTROS ESPECIAIS:")
    #print(registros_especiais[colunas_exibir].head(3))

################################################################################
import pandas as pd
import numpy as np
import re
from datetime import datetime, time

def converter_qualquer_formato_para_hhmm(valor):
    """
    Detecta automaticamente o formato do valor e converte para HH:MM
    
    Formatos suportados:
    - Texto: "08:30", "8:30", "08:30:45" 
    - Decimal: 8.5 (horas), 1.25 (horas)
    - Inteiro: 90 (minutos se < 24), 3600 (segundos se >= 100)
    - Datetime/time objects
    - Timestamps
    """
    if pd.isna(valor) or valor == "" or valor == 0:
        return "00:00"
    
    try:
        valor_original = valor
        
        # 1. Se já é string no formato HH:MM
        if isinstance(valor, str):
            valor = valor.strip()
            
            # Formato HH:MM ou H:MM
            if re.match(r'^\d{1,2}:\d{2}$', valor):
                horas, minutos = map(int, valor.split(':'))
                return f"{horas:02d}:{minutos:02d}"
            
            # Formato HH:MM:SS (ignorar segundos)
            if re.match(r'^\d{1,2}:\d{2}:\d{2}$', valor):
                horas, minutos, segundos = map(int, valor.split(':'))
                return f"{horas:02d}:{minutos:02d}"
            
            # Tentar converter string numérica para float
            try:
                valor = float(valor)
            except ValueError:
                return "00:00"
        
        # 2. Se é datetime ou time object
        if isinstance(valor, (datetime, time)):
            if isinstance(valor, datetime):
                return f"{valor.hour:02d}:{valor.minute:02d}"
            else:
                return f"{valor.hour:02d}:{valor.minute:02d}"
        
        # 3. Se é timestamp (assumir que é timestamp do pandas)
        if hasattr(valor, 'hour') and hasattr(valor, 'minute'):
            return f"{valor.hour:02d}:{valor.minute:02d}"
        
        # 4. Se é numérico, detectar o formato baseado no valor
        if isinstance(valor, (int, float, np.integer, np.floating)):
            valor = float(valor)
            
            # Se é muito grande, provavelmente são segundos
            if valor >= 3600:  # >= 1 hora em segundos
                horas = int(valor // 3600)
                minutos = int((valor % 3600) // 60)
                return f"{horas:02d}:{minutos:02d}"
            
            # Se está entre 60 e 3599, provavelmente são minutos
            elif valor >= 60:
                horas = int(valor // 60)
                minutos = int(valor % 60)
                return f"{horas:02d}:{minutos:02d}"
            
            # Se é menor que 60, pode ser horas decimais ou minutos
            # Analisar se tem decimais para decidir
            elif valor != int(valor):  # Tem decimais - provavelmente horas
                horas = int(valor)
                minutos = int((valor - horas) * 60)
                return f"{horas:02d}:{minutos:02d}"
            
            # Se é inteiro pequeno, assumir que são horas
            else:
                horas = int(valor)
                minutos = 0
                return f"{horas:02d}:{minutos:02d}"
        
        return "00:00"
        
    except Exception as e:
        print(f"Erro ao converter valor '{valor_original}': {e}")
        return "00:00"

def converter_para_tempo(df, colunas=None, ultimas_n=None, inplace=False):
    """
    Função principal - detecta automaticamente o formato e converte para HH:MM
    
    Parâmetros:
    - df: DataFrame a ser formatado
    - colunas: lista de colunas específicas para formatar (None = auto-detectar)
    - ultimas_n: formatar apenas as últimas N colunas (None = ignorar)
    - inplace: se True, modifica o DataFrame original
    
    Retorna:
    - DataFrame com as colunas formatadas em HH:MM
    """
    
    if not inplace:
        df = df.copy()
    
    # Determinar quais colunas formatar
    if colunas is not None:
        # Colunas específicas informadas
        colunas_para_formatar = [col for col in colunas if col in df.columns]
        colunas_nao_encontradas = [col for col in colunas if col not in df.columns]
        
        if colunas_nao_encontradas:
            print(f"Aviso: Colunas não encontradas: {colunas_nao_encontradas}")
            
    elif ultimas_n is not None:
        # Pegar as últimas N colunas
        colunas_para_formatar = df.columns[-ultimas_n:].tolist()
        
    else:
        # Auto-detectar colunas que podem ser tempo
        colunas_para_formatar = []
        for coluna in df.columns:
            # Verificar se a coluna pode conter dados de tempo
            amostra = df[coluna].dropna().head(5)
            if len(amostra) > 0:
                primeiro_valor = amostra.iloc[0]
                # Se tem valores numéricos ou strings com ':'
                if (isinstance(primeiro_valor, (int, float, np.integer, np.floating)) or 
                    (isinstance(primeiro_valor, str) and (':' in primeiro_valor or primeiro_valor.replace('.','').isdigit()))):
                    colunas_para_formatar.append(coluna)
        
        print(f"Colunas detectadas automaticamente: {colunas_para_formatar}")
    
    print(f"Formatando {len(colunas_para_formatar)} colunas para HH:MM")
    
    # Aplicar formatação
    for coluna in colunas_para_formatar:
        if coluna in df.columns:
            print(f"Processando: {coluna}")
            
            # Mostrar alguns exemplos antes da conversão
            valores_exemplo = df[coluna].dropna().head(3).tolist()
            print(f"  Antes: {valores_exemplo}")
            
            # Aplicar conversão
            df[coluna] = df[coluna].apply(converter_qualquer_formato_para_hhmm)
            
            # Mostrar resultado
            valores_depois = df[coluna].head(3).tolist()
            print(f"  Depois: {valores_depois}")
            print()
    
    return df

def detectar_formato_coluna(df, coluna):
    """
    Analisa uma coluna e detecta seu formato de tempo
    Útil para debug e verificação
    """
    if coluna not in df.columns:
        return "Coluna não encontrada"
    
    valores_nao_nulos = df[coluna].dropna()
    if len(valores_nao_nulos) == 0:
        return "Coluna vazia"
    
    amostra = valores_nao_nulos.head(10).tolist()
    
    # Detectar formato predominante
    formato_detectado = "Desconhecido"
    
    if all(isinstance(v, str) for v in amostra):
        if any(':' in str(v) for v in amostra):
            formato_detectado = 'Texto HH:MM'
        else:
            formato_detectado = 'Texto numérico'
    elif all(isinstance(v, (int, float, np.integer, np.floating)) for v in amostra):
        valores_num = [float(v) for v in amostra]
        if all(v >= 3600 for v in valores_num):
            formato_detectado = 'Segundos totais'
        elif all(v >= 60 for v in valores_num):
            formato_detectado = 'Minutos totais'
        elif any(v != int(v) for v in valores_num):
            formato_detectado = 'Horas decimais'
        else:
            formato_detectado = 'Horas inteiras'
    
    return {
        'total_valores': len(valores_nao_nulos),
        'exemplos': amostra[:5],
        'formato_detectado': formato_detectado
    }

# Exemplo de uso
def exemplo_completo():
    print("=== EXEMPLO COMPLETO ===\n")
    
    # Criar DataFrame com DIFERENTES formatos misturados
    df = pd.DataFrame({
        'Funcionario': ['João', 'Maria', 'Pedro', 'Ana'],
        'Horas_Decimais': [8.5, 7.75, 8.0, 6.25],         # 8.5 → 08:30
        'Texto_Tempo': ['08:30', '7:45', '08:00', '6:15'], # já formatado
        'Minutos_Total': [510, 465, 480, 375],             # 510 → 08:30
        'Segundos_Total': [30600, 27900, 28800, 22500],    # 30600 → 08:30
        'Com_Segundos': ['08:30:15', '7:45:30', '08:00:00', '6:15:45'],
        'Horas_Inteiras': [8, 7, 8, 6]                     # 8 → 08:00
    })
    
    print("DataFrame ORIGINAL (formatos misturados):")
    print(df)
    print("\n" + "="*80 + "\n")
    
    # Detectar formatos antes da conversão
    print("DETECÇÃO DE FORMATOS:")
    for coluna in df.columns[1:]:  # Pular a coluna 'Funcionario'
        info = detectar_formato_coluna(df, coluna)
        print(f"{coluna}: {info['formato_detectado']} - Exemplos: {info['exemplos'][:3]}")
    
    print("\n" + "="*50 + "\n")
    
    # Converter automaticamente
    print("CONVERTENDO AUTOMATICAMENTE:")
    df_convertido = converter_para_tempo(df.copy())
    
    print("\nDataFrame CONVERTIDO (tudo em HH:MM):")
    print(df_convertido)
    
    return df_convertido

# Funções de conveniência
def formatar_ultimas_colunas(df, n_colunas, inplace=False):
    """Formatar apenas as últimas N colunas"""
    return converter_para_tempo(df, ultimas_n=n_colunas, inplace=inplace)

def formatar_colunas_especificas(df, lista_colunas, inplace=False):
    """Formatar colunas específicas"""
    return converter_para_tempo(df, colunas=lista_colunas, inplace=inplace)

def formatar_todas_colunas_tempo(df, inplace=False):
    """Auto-detectar e formatar todas as colunas de tempo"""
    return converter_para_tempo(df, inplace=inplace)

if __name__ == "__main__":
    exemplo_completo()

################################################################################
import csv
from datetime import datetime
import os

working_directory = os.getcwd()
csv_path = working_directory + '/log_processamento.csv'

# Inicializa o arquivo CSV com cabeçalho apenas se não existir
if not os.path.exists(csv_path):
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'mensagem'])

def print_log(mensagem):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(mensagem)  # Exibe a mensagem normalmente no output

    # Salva a mensagem no CSV
    with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, mensagem])

################################################################################        
#CALCULA HORAS NA APRESENTAÇÃO
################################################################################
# Filtrar o DataFrame para incluir apenas as linhas onde Activity esteja em tipos_voo Id_Leg é '-I' ou '-IF' e Activity iniciar com 'AD'
import dis
import os

tipos_voo_set = set(tipos_voo)
df_filtrado = df_com_especiais[df_com_especiais['Activity'].isin(tipos_voo_set) & df_com_especiais['Id_Leg'].isin(['-I', '-IF'])].copy()
df_filtrado = df_com_especiais[df_com_especiais['Activity'].str.startswith('AD') & df_com_especiais['Id_Leg'].isin(['-I', '-IF'])].copy()

print("\n📋 REGISTROS FILTRADOS (Id_Leg = '-I' ou '-IF'):")

# 🔧 CORREÇÃO PRINCIPAL: Inicializar com pd.Timedelta(0) ao invés de pd.NaT
for col in [
    'Tempo Apresentacao',
    'Tempo Apresentacao Diurno',
    'Tempo Apresentacao Noturno',
    'Tempo Apresentacao Especial Diurno',
    'Tempo Apresentacao Especial Noturno'
]:
    if col not in df_filtrado.columns:
        df_filtrado[col] = pd.Timedelta(0)  # ✅ CORRETO: timedelta para durações

# Calcular tempo diurno e noturno para cada linha filtrada
for linha in df_filtrado.itertuples():
    checkin = linha.Checkin
    start = linha.Start
    end = linha.Checkin
    checkout = linha.Start

    # Para tempo de apresentação, o período é de checkin até start
    if pd.isnull(checkin) or pd.isnull(start):
        print(f" - Linha {linha.Index} contém valores nulos. Pulando...")
        continue

    tempo_diurno, tempo_noturno = calcular_diurno_noturno(
        checkin.strftime("%d/%m/%Y %H:%M"),
        start.strftime("%d/%m/%Y %H:%M"),
        end.strftime("%d/%m/%Y %H:%M"),
        checkout.strftime("%d/%m/%Y %H:%M")
    )

    # ✅ Agora não haverá warning porque ambos são timedelta
    df_filtrado.at[linha.Index, 'Tempo Apresentacao Diurno'] = tempo_diurno
    df_filtrado.at[linha.Index, 'Tempo Apresentacao Noturno'] = tempo_noturno

    # Avaliar e alocar os períodos diurno e noturno especiais
    if df_filtrado.at[linha.Index, 'Checkin_Especial'] or df_filtrado.at[linha.Index, 'Start_Especial']:
        df_filtrado.at[linha.Index, 'Tempo Apresentacao Especial Diurno'] = tempo_diurno
        df_filtrado.at[linha.Index, 'Tempo Apresentacao Especial Noturno'] = tempo_noturno

# configurar a impressão de todas as linhas do DataFrame
#pd.set_option('print.max_columns', None)

# 🔧 CORREÇÃO: Também inicializar no DataFrame original com timedelta
for col in [
    'Tempo Apresentacao',
    'Tempo Apresentacao Diurno',
    'Tempo Apresentacao Noturno',
    'Tempo Apresentacao Especial Diurno',
    'Tempo Apresentacao Especial Noturno'
]:
    if col not in df.columns:
        df[col] = pd.Timedelta(0)  # ✅ CORRETO: timedelta para durações

# Copiar os valores do DataFrame filtrado para o DataFrame original
colunas_para_copiar = [
    'Tempo Apresentacao'
    'Tempo Apresentacao Diurno',
    'Tempo Apresentacao Noturno',
    'Tempo Apresentacao Especial Diurno',
    'Tempo Apresentacao Especial Noturno'
]

for coluna in colunas_para_copiar:
    if coluna in df_filtrado.columns:
        # Usar .loc para copiar apenas os índices que existem em df_filtrado
        df.loc[df_filtrado.index, coluna] = df_filtrado[coluna]
        print(f" - Coluna '{coluna}' copiada com sucesso!")
    else:
        print(f" - Coluna '{coluna}' não encontrada no df_filtrado")

# Verificar quantos valores foram copiados
print(" - ESTATÍSTICAS DE TRANSFERÊNCIA:")
for coluna in colunas_para_copiar:
    if coluna in df.columns:
        valores_nao_nulos = df[coluna].notna().sum()
        print(f" - {coluna}: {valores_nao_nulos} valores não nulos")

#####
# chamar a função para criar o nome do arquivo
working_directory = WORKING_DIRECTORY
input_file = INPUT_FILE

print("DEBUG - Diretório de trabalho:", working_directory)
print("DEBUG - Arquivo de entrada:", input_file)

resultado = montar_caminho_arquivo(
    working_directory, 
    input_file, 
    'APRESENTACAO'
)
caminho_arquivo_gravar = resultado

# Salvar o DataFrame atualizado com separador de vírgula explícito
df_filtrado[['Activity', 'Id_Leg', 'Checkin', 'Start', 'Dep', 'Arr', 'End', 'Checkout',
            'Tempo Apresentacao', 'Tempo Apresentacao Diurno', 'Tempo Apresentacao Noturno',
            'Tempo Apresentacao Especial Diurno', 'Tempo Apresentacao Especial Noturno']].to_csv(
    f"{caminho_arquivo_gravar}",  # Adiciona .csv diretamente
    index=False,
    encoding='utf-8')
print(f" - DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

################################################################################        
#CALCULA HORAS APÓS O CORTE DOS MOTORES
################################################################################
# criar um DataFrame filtrado a partir do df_com_especiais onde a esteja contido na coluna 'Activity' algum valor de tipos_voo_set e Id_Leg é '-F' ou '-IF' 
tipos_voo_set = set(tipos_voo)

# Build a regex pattern to match any of the flight types at the start of the string
import re
pattern = r'^(' + '|'.join(map(re.escape, tipos_voo_set)) + ')'

df_filtrado_f = df_com_especiais[
    df_com_especiais['Activity'].str.contains(pattern, regex=True) &
    df_com_especiais['Id_Leg'].isin(['-F', '-IF'])
].copy()

# Calcular tempo diurno e noturno para cada linha filtrada
for linha in df_filtrado_f.itertuples():
    checkin = linha.End
    start = linha.Checkout
    end = linha.End
    checkout = linha.Checkout

    # Para tempo de apresentação, o período é de checkin até start
    if pd.isnull(linha.Checkin) or pd.isnull(linha.Start) or pd.isnull(linha.End) or pd.isnull(linha.Checkout):
        print(" - Linha {linha.Index} contém valores nulos. Pulando...")
        continue

    tempo_diurno, tempo_noturno = calcular_diurno_noturno(
        checkin.strftime("%d/%m/%Y %H:%M"),
        start.strftime("%d/%m/%Y %H:%M"),
        end.strftime("%d/%m/%Y %H:%M"),
        checkout.strftime("%d/%m/%Y %H:%M")
    )
    df_filtrado_f.at[linha.Index, 'Tempo Apos Corte'] = checkout - end
    df_filtrado_f.at[linha.Index, 'Tempo Apos Corte Diurno'] = tempo_diurno
    df_filtrado_f.at[linha.Index, 'Tempo Apos Corte Noturno'] = tempo_noturno

    # Avaliar e alocar os períodos diuno e noturno especiais, se Checkout_especial for True ou End_Especial for True, 
    # alocar os valores de Tempo Apos Corte Diurno e Tempo Apos Corte Noturno nos Tempo Apos Corte Especial Diurno e Tempo Apos Corte Especial Noturno
    if df_filtrado_f.at[linha.Index, 'Checkout_Especial'] or df_filtrado_f.at[linha.Index, 'End_Especial']:
        df_filtrado_f.at[linha.Index, 'Tempo Apos Corte Especial Diurno'] = tempo_diurno
        df_filtrado_f.at[linha.Index, 'Tempo Apos Corte Especial Noturno'] = tempo_noturno
    else:
        df_filtrado_f.at[linha.Index, 'Tempo Apos Corte Especial Diurno'] = pd.Timedelta(0)
        df_filtrado_f.at[linha.Index, 'Tempo Apos Corte Especial Noturno'] = pd.Timedelta(0)

# Garantir que as colunas existem no DataFrame original
for col in [
    'Tempo Apos Corte',
    'Tempo Apos Corte Diurno',
    'Tempo Apos Corte Noturno',
    'Tempo Apos Corte Especial Diurno',
    'Tempo Apos Corte Especial Noturno'
]:
    if col not in df.columns:
        #df[col] = pd.NaT
        df[col] = pd.Timedelta(0)

# Copiar os valores do DataFrame filtrado para o DataFrame original
colunas_para_copiar = [
    'Tempo Apos Corte',
    'Tempo Apos Corte Diurno',
    'Tempo Apos Corte Noturno',
    'Tempo Apos Corte Especial Diurno',
    'Tempo Apos Corte Especial Noturno'
]
for coluna in colunas_para_copiar:
    if coluna in df_filtrado_f.columns:
        df.loc[df_filtrado_f.index, coluna] = df_filtrado_f[coluna]
        __builtins__.print(f"✅ Coluna '{coluna}' copiada com sucesso!")
    else:
        __builtins__.print(f"⚠️ Coluna '{coluna}' não encontrada no df_filtrado_f")

# Exibir o DataFrame atualizado com as novas colunas
print("\n📋 DataFrame Filtrado com Tempo Apos Corte Diurno e Noturno")

# chamar a função para criar o nome do arquivo
resultado = montar_caminho_arquivo(
    WORKING_DIRECTORY, 
    INPUT_FILE, 
    'APOS_CORTE')

caminho_arquivo_gravar = resultado

df_filtrado_f[['Activity', 'Id_Leg', 'Checkin', 'Start', 'Dep', 'Arr', 'End', 'Checkout',
    'Tempo Apos Corte', 'Tempo Apos Corte Diurno', 'Tempo Apos Corte Noturno',
    'Tempo Apos Corte Especial Diurno', 'Tempo Apos Corte Especial Noturno']].to_csv(
    f"{caminho_arquivo_gravar}", index=False, encoding='utf-8')
__builtins__.print(f"✅ DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

################################################################################
# CALCULAR TEMPO SOLO ENTRE ETAPAS
################################################################################
import re

# Filtrar registros por etapas de voo
df_filtrado_g = df_com_especiais[df_com_especiais['Activity'].str.startswith('AD')].copy()
df_filtrado_g = df_filtrado_g[df_filtrado_g['Id_Leg'].isin(['-M', '-I', '-F'])].copy()

# 🔧 CORREÇÃO: Inicializar com pd.Timedelta(0) ao invés de pd.NaT
for col in ['Tempo Solo Diurno', 'Tempo Solo Noturno', 'Tempo Solo Especial Diurno', 'Tempo Solo Especial Noturno']:
    if col not in df_filtrado_g.columns:
        df_filtrado_g[col] = pd.Timedelta(0)  # ✅ CORRETO: timedelta para durações

# Resetar o índice para facilitar acesso posicional
df_filtrado_g = df_filtrado_g.reset_index(drop=False)  # mantém o índice original em 'index'

print(f"🔄 Processando {len(df_filtrado_g)} registros de voo...")

# Calcular tempo diurno e noturno para cada linha filtrada, exceto a última
for i in range(len(df_filtrado_g) - 1):
    linha_atual = df_filtrado_g.iloc[i]
    linha_proxima = df_filtrado_g.iloc[i + 1]

    # Para tempo solo: do fim da etapa atual até o início da próxima
    checkin = linha_atual['End']
    start = linha_proxima['Start']
    end = linha_atual['End']
    checkout = linha_proxima['Start']

    # Verificar se há valores nulos
    if pd.isnull(checkin) or pd.isnull(start):
        print(f"⚠️ Linha {linha_atual['index']} contém valores nulos. Pulando...")
        continue
        
    # Se Id_leg for igual a '-F' não calcular o tempo diurno e noturno
    if linha_atual['Id_Leg'] == '-F':
        continue     
        
    try:
        tempo_diurno, tempo_noturno = calcular_diurno_noturno(
            checkin.strftime("%d/%m/%Y %H:%M"),
            start.strftime("%d/%m/%Y %H:%M"),
            end.strftime("%d/%m/%Y %H:%M"),
            checkout.strftime("%d/%m/%Y %H:%M")
        )

        # ✅ Agora não haverá warning porque ambos são timedelta
        df_filtrado_g.at[i, 'Tempo Solo Diurno'] = tempo_diurno
        df_filtrado_g.at[i, 'Tempo Solo Noturno'] = tempo_noturno

        # Verificar se é período especial - usar o índice original para acessar df_com_especiais
        indice_original = linha_atual['index']
        
        # Verificar se o fim da etapa atual ou início da próxima são especiais
        fim_especial = df_com_especiais.at[indice_original, 'End_Especial'] if 'End_Especial' in df_com_especiais.columns else False
        indice_proximo = linha_proxima['index']
        inicio_especial = df_com_especiais.at[indice_proximo, 'Start_Especial'] if 'Start_Especial' in df_com_especiais.columns else False
        
        if fim_especial or inicio_especial:
            df_filtrado_g.at[i, 'Tempo Solo Especial Diurno'] = tempo_diurno
            df_filtrado_g.at[i, 'Tempo Solo Especial Noturno'] = tempo_noturno
            
    except Exception as e:
        print(f"❌ Erro ao processar linha {linha_atual['index']}: {e}")
        continue

print(f"✅ Processamento concluído!")

# 🔧 CORREÇÃO: Também aplicar no DataFrame original
for col in [
    'Tempo Solo Diurno',
    'Tempo Solo Noturno',
    'Tempo Solo Especial Diurno',
    'Tempo Solo Especial Noturno'
]:
    if col not in df.columns:
        df[col] = pd.Timedelta(0)  # ✅ CORRETO: timedelta para durações

# Copiar os valores do DataFrame filtrado para o DataFrame original
colunas_para_copiar = [
    'Tempo Solo Diurno',
    'Tempo Solo Noturno',
    'Tempo Solo Especial Diurno',
    'Tempo Solo Especial Noturno'
]

print("🔄 Transferindo dados calculados para o DataFrame original...")

for coluna in colunas_para_copiar:
    if coluna in df_filtrado_g.columns:
        # Usar os índices originais para transferir os dados
        for i, row in df_filtrado_g.iterrows():
            if pd.notna(row[coluna]) and row[coluna] != pd.Timedelta(0):  # ✅ Verificar se não é zero
                indice_original = row['index']
                df.at[indice_original, coluna] = row[coluna]
        
        valores_copiados = (df[coluna] != pd.Timedelta(0)).sum()  # ✅ Contar valores não-zero
        print(f"✅ Coluna '{coluna}': {valores_copiados} valores copiados")
    else:
        print(f"⚠️ Coluna '{coluna}' não encontrada no df_filtrado_g")

# Verificar resultados
print(f"\n📊 ESTATÍSTICAS FINAIS:")
for coluna in colunas_para_copiar:
    if coluna in df.columns:
        valores_nao_nulos = (df[coluna] != pd.Timedelta(0)).sum()  # ✅ Contar valores não-zero
        print(f"   • {coluna}: {valores_nao_nulos} valores não nulos")

#####
# chamar a função para criar o nome do arquivo
resultado = montar_caminho_arquivo(
    WORKING_DIRECTORY, 
    INPUT_FILE, 
    'TEMPO_SOLO')

caminho_arquivo_gravar = resultado

df_filtrado_g[['Activity', 'Id_Leg', 'Checkin', 'Dep', 'Arr', 'Start', 'End', 'Checkout',
    'Tempo Solo Diurno', 'Tempo Solo Noturno',
    'Tempo Solo Especial Diurno', 'Tempo Solo Especial Noturno']].to_csv(
    f"{caminho_arquivo_gravar}", index=False, encoding='utf-8')
print(f"✅ DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

print(df_filtrado_g.head(3))

################################################################################
# CALCULAR JORNADAS
################################################################################
import pandas as pd
#from IPython.print import print

# criar DataFrame com valores do arquivo Siglas Sabre 1.xlsx
def cria_df_siglas_sabre():
    # Supondo que você já tenha seu DataFrame carregado
    df_siglas_sabre = pd.read_excel(r'G:\SPECTRUM_SYSTEM\Aeronautas\Documentos_Comuns\Arquivos_Diversos\Siglas Sabre 1.xlsx')  # ou qualquer fonte

    # excluir a coluna Unnamed: 0  se existir
    if 'Unnamed: 0' in df_siglas_sabre.columns:
        df_siglas_sabre = df_siglas_sabre.drop(columns=['Unnamed: 0', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7'], errors='ignore')
    
    # Exibir todas as linhas do DataFrame filtrado
    #pd.set_option('print.max_rows', None)  # Exibir todas as linhas
    #pd.set_option('print.max_columns', None)  # Exibir todas as colunas
    #print(df_siglas_sabre)
    return df_siglas_sabre
cria_df_siglas_sabre()

def adiciona_colunas_sabre(df_siglas_sabre, df_com_especiais):
    """
    Adiciona colunas PGTO e JORNADA baseadas nas siglas válidas e suas configurações
    """
    # Extrair lista de siglas válidas com suas configurações
    siglas_config = df_siglas_sabre[['SIGLA', 'PGTO', 'JORNADA']].dropna(subset=['SIGLA'])
    
    # Criar dicionários de mapeamento para lookup eficiente
    pgto_mapping = dict(zip(siglas_config['SIGLA'], siglas_config['PGTO']))
    jornada_mapping = dict(zip(siglas_config['SIGLA'], siglas_config['JORNADA']))
    
    def verificar_pgto(activity):
        """Verifica se a atividade tem direito a pagamento"""
        if not isinstance(activity, str):
            return False
        
        for sigla, pgto_valor in pgto_mapping.items():
            if sigla in activity:
                return pgto_valor == 'S'  # True se PGTO = 'S', False caso contrário
        return False
    
    def verificar_jornada(activity):
        """Verifica se a atividade conta para jornada"""
        if not isinstance(activity, str):
            return False
        
        for sigla, jornada_valor in jornada_mapping.items():
            if sigla in activity:
                return jornada_valor == 'S'  # True se JORNADA = 'S', False caso contrário
        return False
    
    # Aplicar as funções às colunas do DataFrame
    df_com_especiais['PGTO'] = df_com_especiais['Activity'].apply(verificar_pgto)
    df_com_especiais['JORNADA'] = df_com_especiais['Activity'].apply(verificar_jornada)
    
    # Estatísticas para verificação
    total_pgto = df_com_especiais['PGTO'].sum()
    total_jornada = df_com_especiais['JORNADA'].sum()
    
    print(f"✅ Colunas PGTO e JORNADA criadas com base nas configurações:")
    print(f"   • Registros com PGTO = True: {total_pgto}")
    print(f"   • Registros com JORNADA = True: {total_jornada}")
    print(f"   • Total de siglas configuradas: {len(siglas_config)}")
    
    return df_com_especiais

################################################################################
adiciona_colunas_sabre(cria_df_siglas_sabre(), df_com_especiais)

# Filtrar registros por etapas de reserva
#print(df_com_especiais.head(50))
df_filtrado_h = df_com_especiais[df_com_especiais['JORNADA']].copy()
df_filtrado_h = df_filtrado_h[df_filtrado_h['Id_Leg'].isin(['-IF', '-F'])].copy()
#print(df_filtrado_h)

################################################################################
# Filtrar registros 
df_filtrado_h = df_com_especiais[df_com_especiais['JORNADA']].copy()
df_filtrado_h = df_filtrado_h[df_filtrado_h['Id_Leg'].isin(['-IF', '-F'])].copy()

# 🔧 CORREÇÃO: Inicializar com pd.Timedelta(0) ao invés de pd.NaT
for col in ['Tempo Jornada Diurno', 'Tempo Jornada Noturno', 'Tempo Jornada Especial Diurno', 'Tempo Jornada Especial Noturno']:
    if col not in df_filtrado_h.columns:
        df_filtrado_h[col] = pd.Timedelta(0)  # ✅ CORRETO: timedelta para durações

# Resetar o índice para facilitar acesso posicional
df_filtrado_h = df_filtrado_h.reset_index(drop=False)  # mantém o índice original em 'index'

print(f"🔄 Processando {len(df_filtrado_h)} registros de voo...")

# Calcular tempo diurno e noturno para cada linha filtrada, exceto a última
for i in range(len(df_filtrado_h) - 1):
    linha_atual = df_filtrado_h.iloc[i]
    linha_proxima = df_filtrado_h.iloc[i + 1]

    # Para tempo solo: do fim da etapa atual até o início da próxima
    checkin = linha_atual['Checkin']
    start = linha_atual['Start']
    end = linha_atual['End']
    checkout = linha_atual['Checkout']

    # Verificar se há valores nulos
    if pd.isnull(checkin) or pd.isnull(start):
        print(f"⚠️ Linha {linha_atual['index']} contém valores nulos. Pulando...")
        continue
        
    try:
        tempo_diurno, tempo_noturno = calcular_diurno_noturno(
            checkin.strftime("%d/%m/%Y %H:%M"),
            start.strftime("%d/%m/%Y %H:%M"),
            end.strftime("%d/%m/%Y %H:%M"),
            checkout.strftime("%d/%m/%Y %H:%M")
        )

        # ✅ Agora não haverá warning porque ambos são timedelta
        df_filtrado_h.at[i, 'Tempo Jornada Diurno'] = tempo_diurno
        df_filtrado_h.at[i, 'Tempo Jornada Noturno'] = tempo_noturno

        # Verificar se é período especial - usar o índice original para acessar df_com_especiais
        indice_original = linha_atual['index']
        
        # Verificar se o fim da etapa atual ou início da próxima são especiais
        fim_especial = df_com_especiais.at[indice_original, 'Checkout_Especial'] if 'Checkout_Especial' in df_com_especiais.columns else False
        # 🔧 CORREÇÃO: Corrigir a referência da linha_proxima
        if i + 1 < len(df_filtrado_h):  # Verificar se não é o último registro
            indice_proximo = linha_proxima['index']
            inicio_especial = df_com_especiais.at[indice_proximo, 'Checkin_Especial'] if 'Checkin_Especial' in df_com_especiais.columns else False
        else:
            inicio_especial = False
        
        if fim_especial or inicio_especial:
            df_filtrado_h.at[i, 'Tempo Jornada Especial Diurno'] = tempo_diurno
            df_filtrado_h.at[i, 'Tempo Jornada Especial Noturno'] = tempo_noturno
            
    except Exception as e:
        print(f"❌ Erro ao processar linha {linha_atual['index']}: {e}")
        continue

print(f"✅ Processamento concluído!")

# 🔧 CORREÇÃO: Garantir que as colunas existem no DataFrame original com timedelta
for col in [
    'Tempo Jornada Diurno',
    'Tempo Jornada Noturno',
    'Tempo Jornada Especial Diurno',
    'Tempo Jornada Especial Noturno'
]:
    if col not in df.columns:
        df[col] = pd.Timedelta(0)  # ✅ CORRETO: timedelta para durações

# Copiar os valores do DataFrame filtrado para o DataFrame original
colunas_para_copiar = [
    'Tempo Jornada Diurno',
    'Tempo Jornada Noturno',
    'Tempo Jornada Especial Diurno',
    'Tempo Jornada Especial Noturno'
]

print("🔄 Transferindo dados calculados para o DataFrame original...")

for coluna in colunas_para_copiar:
    if coluna in df_filtrado_h.columns:
        # Usar os índices originais para transferir os dados
        for i, row in df_filtrado_h.iterrows():
            if pd.notna(row[coluna]) and row[coluna] != pd.Timedelta(0):  # ✅ Verificar se não é zero
                indice_original = row['index']
                df.at[indice_original, coluna] = row[coluna]
        
        valores_copiados = (df[coluna] != pd.Timedelta(0)).sum()  # ✅ Contar valores não-zero
        print(f"✅ Coluna '{coluna}': {valores_copiados} valores copiados")
    else:
        print(f"⚠️ Coluna '{coluna}' não encontrada no df_filtrado_h")

# Verificar resultados
print(f"\n📊 ESTATÍSTICAS FINAIS:")
for coluna in colunas_para_copiar:
    if coluna in df.columns:
        valores_nao_nulos = (df[coluna] != pd.Timedelta(0)).sum()  # ✅ Contar valores não-zero
        print(f"   • {coluna}: {valores_nao_nulos} valores não nulos")

#############
# chamar a função para criar o nome do arquivo
resultado = montar_caminho_arquivo(
    WORKING_DIRECTORY, 
    INPUT_FILE, 
    'JORNADA')

caminho_arquivo_gravar = resultado

#caminho_arquivo_gravar = working_directory + '/Horas_Jornada.csv'
df_filtrado_h[['Activity', 'Id_Leg', 'Checkin', 'Start', 'End', 'Checkout',
    'Tempo Jornada Diurno', 'Tempo Jornada Noturno',
    'Tempo Jornada Especial Diurno', 'Tempo Jornada Especial Noturno']].to_csv(
    f"{caminho_arquivo_gravar}", index=False, encoding='utf-8')

print(f"✅ DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

################################################################################
# CALCULAR REPOUSO
################################################################################
# Versão mais robusta com tratamento de erros melhorado
import traceback

lista_folgas =['ABA', 'DME', 'DMF','DMI','DMS','DOB','DSP','F','FR','FAL','FAN','FCL','FER','FG','FJ','FJC','FP','FR','FSP','FT','INE','INF','INS','LGC','LGE', 
'LHR','LM','LOP','LP','LSV','LUT']               

# Filtrar registros por etapas de 
df_filtrado_i = df_com_especiais[df_com_especiais['Id_Leg'].isin(['-IF', '-F'])].copy()

# Garantir que as colunas necessárias existem com tipo correto
for col in ['Tempo Repouso Diurno', 'Tempo Repouso Noturno', 'Tempo Repouso Especial Diurno', 'Tempo Repouso Especial Noturno']:
    if col not in df_filtrado_i.columns:
        df_filtrado_i[col] = pd.Timedelta(0)  # ✅ Inicializa com zero# Resetar o índice para facilitar acesso posicional
df_filtrado_i = df_filtrado_i.reset_index(drop=False)

print(f"🔄 Processando {len(df_filtrado_i)} registros de repouso...")

# Contadores para estatísticas
registros_processados = 0
registros_com_erro = 0
registros_pulados = 0

# Calcular tempo diurno e noturno para cada linha filtrada, exceto a última
for i in range(len(df_filtrado_i) - 1):
    
    try:
        linha_anterior = df_filtrado_i.iloc[i - 1] if i > 0 else None
        linha_atual = df_filtrado_i.iloc[i]
        linha_proxima = df_filtrado_i.iloc[i + 1]

        # 🔧 CORREÇÃO: Verificar folgas com operador lógico correto e tratamento de None
        if (linha_anterior is not None and 
            linha_atual['Activity'] in lista_folgas and 
            linha_anterior['Activity'] in lista_folgas):
            print(f"⚠️ Registro {i} com Activity '{linha_atual['Activity']}' e anterior '{linha_anterior['Activity']}' - pulando (ambas são folgas)")
            registros_pulados += 1
            continue

        # Para tempo de repouso: do fim da etapa atual até o início da próxima
        checkin = linha_atual['Checkout']
        start = linha_proxima['Checkin']
        end = linha_atual['Checkout']
        checkout = linha_proxima['Checkin']

        # Verificar se há valores nulos
        if pd.isnull(checkin) or pd.isnull(start):
            registros_pulados += 1
            continue

        # Verificar se são objetos datetime válidos
        if not hasattr(checkin, 'strftime') or not hasattr(checkout, 'strftime'):
            print(f"⚠️ Valores não são datetime no registro {i} - pulando")
            registros_pulados += 1
            continue

        # 🛑 CONDIÇÃO DE PARADA ESPECÍFICA
        if (pd.notna(linha_atual['End']) and pd.notna(linha_atual['Checkout'])):
            end_atual = linha_atual['End']
            checkout_atual = linha_atual['Checkout']
            
            if (end_atual.strftime("%d/%m/%Y %H:%M") == "05/11/2017 16:45" and 
                checkout_atual.strftime("%d/%m/%Y %H:%M") == "05/11/2017 17:16"):
                print(f"\n🛑 PARADA SOLICITADA no registro {i}!")
                print(f"   • End: {end_atual}")
                print(f"   • Checkout: {checkout_atual}")
                print(f"   • Registros processados até agora: {registros_processados}")
                break

        # Conversão para strings (formato esperado pela função calcular_diurno_noturno)
        checkin_str = checkin.strftime("%d/%m/%Y %H:%M")
        start_str = start.strftime("%d/%m/%Y %H:%M")
        end_str = end.strftime("%d/%m/%Y %H:%M")
        checkout_str = checkout.strftime("%d/%m/%Y %H:%M")

        # Calcular tempo diurno e noturno básico
        tempo_diurno, tempo_noturno = calcular_diurno_noturno(
            checkin_str, start_str, end_str, checkout_str
        )

        # Atribuir valores básicos
        df_filtrado_i.at[i, 'Tempo Repouso Diurno'] = tempo_diurno
        df_filtrado_i.at[i, 'Tempo Repouso Noturno'] = tempo_noturno

        # Preparar feriados
        feriados_list = []
        if isinstance(feriados, pd.DataFrame) and not feriados.empty:
            feriados_list = feriados['date'].dt.strftime('%Y-%m-%d').tolist()

        # Classificar horas especiais (usar objetos datetime originais)
        resultado = classificar_horas_especiais(checkin, checkout, feriados_list)

        # Atribuir valores especiais
        df_filtrado_i.at[i, 'Tempo Repouso Especial Diurno'] = resultado['hora_especial_diurna']
        df_filtrado_i.at[i, 'Tempo Repouso Especial Noturno'] = resultado['hora_especial_noturna']

        registros_processados += 1
        
        # Log a cada 10 registros
        if registros_processados % 10 == 0:
            print(f"✅ Processados {registros_processados} registros...")

    except Exception as e:
        registros_com_erro += 1
        print(f"❌ Erro no registro {i}: {e}")
        if registros_com_erro <= 5:  # Mostrar apenas os primeiros 5 erros
            traceback.print_exc()
        continue

print(f"\n📊 ESTATÍSTICAS DE PROCESSAMENTO:")
print(f"   • Registros processados: {registros_processados}")
print(f"   • Registros com erro: {registros_com_erro}")
print(f"   • Registros pulados: {registros_pulados}")
print(f"   • Total: {registros_processados + registros_com_erro + registros_pulados}")

#############
# chamar a função para criar o nome do arquivo
resultado = montar_caminho_arquivo(
    WORKING_DIRECTORY, 
    INPUT_FILE, 
    'REPOUSO')

caminho_arquivo_gravar = resultado

df_filtrado_i[['Activity', 'Id_Leg', 'Checkin', 'Dep', 'Arr', 'Start', 'End', 'Checkout',
    'Tempo Repouso Diurno', 'Tempo Repouso Noturno',
    'Tempo Repouso Especial Diurno', 'Tempo Repouso Especial Noturno']].to_csv(
    f"{caminho_arquivo_gravar}", index=False, encoding='utf-8')

print(f"✅ DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

################################################################################
# CALCULAR REPOUSO EXTRA
################################################################################
# 🛠️ FILTRO ULTRA-PRECISO PARA REPOUSO EXTRA - VERSÃO CORRIGIDA
def filtrar_repouso_extra_preciso(df):
    """
    Filtra DataFrame para registros com repouso extra REALMENTE diferente de zero
    Usa apenas o método mais confiável: total_seconds() > 0
    """
    
    # Verificar se a coluna existe
    if 'Repouso Extra' not in df.columns:
        print("❌ Coluna 'Repouso Extra' não encontrada!")
        return df.iloc[0:0].copy()
    
    print(f"🔍 ANÁLISE DETALHADA DA COLUNA 'Repouso Extra':")
    print(f"   • Total de registros: {len(df)}")
    print(f"   • Tipo de dados: {df['Repouso Extra'].dtype}")
    print(f"   • Valores únicos: {df['Repouso Extra'].nunique()}")
    
    # Mostrar TODOS os valores únicos
    valores_unicos = df['Repouso Extra'].unique()
    print(f"\n📋 TODOS OS VALORES ÚNICOS ENCONTRADOS:")
    for i, valor in enumerate(valores_unicos):
        if hasattr(valor, 'total_seconds'):
            segundos = valor.total_seconds()
            print(f"   {i+1}. {valor} → {segundos} segundos")
        else:
            print(f"   {i+1}. {valor} (não é timedelta)")
    
    # Função mais precisa para verificar se é realmente zero
    def eh_realmente_zero(valor):
        """Verifica se um valor é realmente zero"""
        if pd.isna(valor):
            return True  # Considerar NaN como zero
        
        if hasattr(valor, 'total_seconds'):
            return valor.total_seconds() == 0
        
        # Fallback para outros tipos
        if str(valor) == '0 days 00:00:00':
            return True
        
        return False
    
    # Aplicar filtro ultra-preciso
    print(f"\n🔍 APLICANDO FILTRO ULTRA-PRECISO:")
    
    # Criar máscara: registros onde repouso extra NÃO é zero
    mask = ~df['Repouso Extra'].apply(eh_realmente_zero)
    
    # Estatísticas detalhadas
    registros_zero = df['Repouso Extra'].apply(eh_realmente_zero).sum()
    registros_nao_zero = mask.sum()
    
    print(f"   • Registros com repouso extra = ZERO: {registros_zero}")
    print(f"   • Registros com repouso extra ≠ ZERO: {registros_nao_zero}")
    
    # Verificar cada registro individualmente
    print(f"\n📋 VERIFICAÇÃO INDIVIDUAL DOS PRIMEIROS 10 REGISTROS:")
    for i in range(min(10, len(df))):
        valor = df.iloc[i]['Repouso Extra']
        eh_zero = eh_realmente_zero(valor)
        incluir = not eh_zero
        
        if hasattr(valor, 'total_seconds'):
            segundos = valor.total_seconds()
            print(f"   {i}: {valor} → {segundos}s → Zero: {eh_zero} → Incluir: {incluir}")
        else:
            print(f"   {i}: {valor} → Zero: {eh_zero} → Incluir: {incluir}")
    
    # Filtrar o DataFrame
    resultado = df[mask].copy()
    
    print(f"\n📊 RESULTADO DO FILTRO:")
    print(f"   • Registros originais: {len(df)}")
    print(f"   • Registros filtrados: {len(resultado)}")
    print(f"   • Registros removidos: {len(df) - len(resultado)}")
    
    if len(resultado) > 0:
        print(f"\n✅ FILTRO APLICADO COM SUCESSO!")
        print(f"📋 REGISTROS FILTRADOS (com repouso extra > 0):")
        
        # Mostrar os registros filtrados
        for i, (idx, row) in enumerate(resultado.iterrows()):
            valor = row['Repouso Extra']
            if hasattr(valor, 'total_seconds'):
                segundos = valor.total_seconds()
                print(f"   {i+1}. Índice {idx}: {valor} ({segundos} segundos)")
            else:
                print(f"   {i+1}. Índice {idx}: {valor}")
        
        return resultado
    else:
        print("⚠️ NENHUM REGISTRO ENCONTRADO COM REPOUSO EXTRA > 0!")
        print("   • Todos os registros têm repouso extra igual a zero")
        return df.iloc[0:0].copy()

# 🚀 APLICAR FILTRO ULTRA-PRECISO
print("🚀 APLICANDO FILTRO ULTRA-PRECISO PARA REPOUSO EXTRA:")
print("=" * 70)

# Aplicar o filtro corrigido
df_filtrado_j = filtrar_repouso_extra_preciso(df)

# Verificar resultado
if len(df_filtrado_j) > 0:
    print(f"\n🎯 SUCESSO! Encontrados {len(df_filtrado_j)} registros com repouso extra REAL.")
    
    # Mostrar os dados filtrados
    print(f"\n📋 DADOS FILTRADOS:")
    colunas_mostrar = ['Id_Leg', 'Repouso Extra']
    if 'Activity' in df_filtrado_j.columns:
        colunas_mostrar.insert(0, 'Activity')
    if 'Checkin' in df_filtrado_j.columns:
        colunas_mostrar.append('Checkin')
    if 'Checkout' in df_filtrado_j.columns:
        colunas_mostrar.append('Checkout')
    
    #print(df_filtrado_j[colunas_mostrar])
    
    # Continuar com o processamento apenas se houver dados
    print(f"\n🔄 INICIANDO PROCESSAMENTO DOS {len(df_filtrado_j)} REGISTROS FILTRADOS...")
    
    # Garantir que as colunas necessárias existem
    # Ou se preferir inicializar com zero:
    for col in ['Tempo Repouso Extra Diurno', 'Tempo Repouso Extra Noturno', 'Tempo Repouso Extra Especial Diurno', 'Tempo Repouso Extra Especial Noturno']:
        if col not in df_filtrado_j.columns:
            df_filtrado_j[col] = pd.Timedelta(0)  # ✅ ALTERNATIVA: inicializar com zero

    # Resetar o índice para facilitar acesso posicional
    df_filtrado_j = df_filtrado_j.reset_index(drop=False)

    print(f"🔄 Processando {len(df_filtrado_j)} registros de repouso extra...")

    # Contadores para estatísticas
    registros_processados = 0
    registros_com_erro = 0
    registros_pulados = 0

    # Calcular tempo diurno e noturno para cada linha filtrada, exceto a última
    for i in range(len(df_filtrado_j) - 1):
        
        try:
            linha_atual = df_filtrado_j.iloc[i]
            linha_proxima = df_filtrado_j.iloc[i + 1]

            # 🔧 CORREÇÃO: Calcular horário de repouso extra corretamente
            checkout_atual = linha_atual['Checkout']
            repouso_extra_duracao = linha_atual['Repouso Extra']
            
            # 🔍 DEBUG: Verificar tipos
            print(f"🔍 Registro {i} - Tipos:")
            print(f"   • checkout_atual: {type(checkout_atual)} = {checkout_atual}")
            print(f"   • repouso_extra_duracao: {type(repouso_extra_duracao)} = {repouso_extra_duracao}")
            
            # Converter repouso_extra_duracao para timedelta se necessário
            if isinstance(repouso_extra_duracao, str):
                print(f"   • Convertendo string '{repouso_extra_duracao}' para timedelta...")
                repouso_extra_duracao = pd.to_timedelta(repouso_extra_duracao)
            elif not hasattr(repouso_extra_duracao, 'total_seconds'):
                print(f"   • Tentando converter {type(repouso_extra_duracao)} para timedelta...")
                repouso_extra_duracao = pd.to_timedelta(repouso_extra_duracao)
            
            print(f"   • repouso_extra_duracao após conversão: {type(repouso_extra_duracao)} = {repouso_extra_duracao}")
            
            # Calcular o início do repouso extra (12 horas após checkout)
            inicio_repouso_extra = checkout_atual + pd.Timedelta(hours=12)
            
            # Calcular o fim do repouso extra (início + duração)
            fim_repouso_extra = inicio_repouso_extra + repouso_extra_duracao
            
            print(f"   • Início Repouso Extra: {inicio_repouso_extra}")
            print(f"   • Fim Repouso Extra: {fim_repouso_extra}")

            # Para cálculo de tempo diurno/noturno, usar o período do repouso extra
            checkin = inicio_repouso_extra
            checkout = fim_repouso_extra
            
            # Verificar se são objetos datetime válidos
            if not hasattr(checkin, 'strftime') or not hasattr(checkout, 'strftime'):
                print(f"⚠️ Valores não são datetime no registro {i} - pulando")
                registros_pulados += 1
                continue

            # Conversão para strings (formato esperado pela função calcular_diurno_noturno)
            checkin_str = checkin.strftime("%d/%m/%Y %H:%M")
            start_str = checkin.strftime("%d/%m/%Y %H:%M")  # Mesmo valor que checkin
            end_str = checkout.strftime("%d/%m/%Y %H:%M")   # Mesmo valor que checkout
            checkout_str = checkout.strftime("%d/%m/%Y %H:%M")

            # Calcular tempo diurno e noturno básico
            tempo_diurno, tempo_noturno = calcular_diurno_noturno(
                checkin_str, start_str, end_str, checkout_str
            )

            # Atribuir valores básicos
            df_filtrado_j.at[i, 'Tempo Repouso Extra Diurno'] = tempo_diurno
            df_filtrado_j.at[i, 'Tempo Repouso Extra Noturno'] = tempo_noturno

            # Preparar feriados
            feriados_list = []
            if isinstance(feriados, pd.DataFrame) and not feriados.empty:
                feriados_list = feriados['date'].dt.strftime('%Y-%m-%d').tolist()

            # Classificar horas especiais (usar objetos datetime originais)
            resultado = classificar_horas_especiais(checkin, checkout, feriados_list)

            # Atribuir valores especiais
            df_filtrado_j.at[i, 'Tempo Repouso Extra Especial Diurno'] = resultado['hora_especial_diurna']
            df_filtrado_j.at[i, 'Tempo Repouso Extra Especial Noturno'] = resultado['hora_especial_noturna']

            registros_processados += 1
            
            print(f"✅ Registro {i} processado com sucesso!")
            print(f"   • Tempo Diurno: {tempo_diurno}")
            print(f"   • Tempo Noturno: {tempo_noturno}")
            print(f"   • Especial Diurno: {resultado['hora_especial_diurna']}")
            print(f"   • Especial Noturno: {resultado['hora_especial_noturna']}")
            print("-" * 50)

        except Exception as e:
            registros_com_erro += 1
            print(f"❌ Erro no registro {i}: {e}")
            if registros_com_erro <= 3:  # Mostrar apenas os primeiros 3 erros
                import traceback
                traceback.print_exc()
            continue

    print(f"\n📊 ESTATÍSTICAS DE PROCESSAMENTO:")
    print(f"   • Registros processados: {registros_processados}")
    print(f"   • Registros com erro: {registros_com_erro}")
    print(f"   • Registros pulados: {registros_pulados}")
    print(f"   • Total: {registros_processados + registros_com_erro + registros_pulados}")

    # Exibir resultados se houver dados processados
    if len(df_filtrado_j) > 0:
        colunas_exibir = ['Checkout', 'Repouso Extra', 'Tempo Repouso Extra Diurno', 'Tempo Repouso Extra Noturno', 'Tempo Repouso Extra Especial Diurno', 'Tempo Repouso Extra Especial Noturno']
        # Filtrar apenas colunas que existem
        colunas_existentes = [col for col in colunas_exibir if col in df_filtrado_j.columns]
        
        print(f"\n📋 RESULTADOS PROCESSADOS:")
        #print(df_filtrado_j[colunas_existentes])

        # suprimir as linhas onde a coluna Activity esteja contida na lista de folgas
        df_filtrado_j = df_filtrado_j[~df_filtrado_j['Activity'].isin(lista_folgas)].copy()

    #############
    # chamar a função para criar o nome do arquivo
    resultado = montar_caminho_arquivo(
        WORKING_DIRECTORY, 
        INPUT_FILE, 
        'REPOUSO_EXTRA')

    caminho_arquivo_gravar = resultado

    if not df_filtrado_j.empty:        
        colunas_salvar = ['Activity', 'Id_Leg', 'Checkin', 'Start', 'Dep', 'Arr', 'End', 'Checkout', 'Repouso Extra',
            'Tempo Repouso Extra Diurno', 'Tempo Repouso Extra Noturno',
            'Tempo Repouso Extra Especial Diurno', 'Tempo Repouso Extra Especial Noturno']
        
        # Filtrar apenas colunas que existem
        colunas_salvar_existentes = [col for col in colunas_salvar if col in df_filtrado_j.columns]
        
        df_filtrado_j[colunas_salvar_existentes].to_csv(
    f"{caminho_arquivo_gravar}", index=False, encoding='utf-8')
        
        print(f"✅ DataFrame filtrado salvo em: {caminho_arquivo_gravar}")
    else:
        print("⚠️ Nenhum dado para exibir após o processamento")

else:
    print("❌ NENHUM REGISTRO ENCONTRADO COM REPOUSO EXTRA > 0!")
    print("   • Todos os registros no DataFrame têm repouso extra igual a zero")
    print("   • Processo de cálculo de repouso extra será pulado")

################################################################################
# CALCULAR RESERVA
################################################################################
# Versão mais robusta com tratamento de erros melhorado
import traceback

reservas = carregar_tipos_reserva()

df_filtrado_k = df[df['Activity'].isin(reservas)].copy()

# 🔧 CORREÇÃO: Garantir que as colunas necessárias existem com tipo correto
for col in ['Tempo Reserva Diurno', 'Tempo Reserva Noturno', 'Tempo Reserva Especial Diurno', 'Tempo Reserva Especial Noturno']:
    if col not in df_filtrado_k.columns:
        df_filtrado_k[col] = pd.Timedelta(0)  # ✅ CORRETO: tipo timedelta

# Resetar o índice para facilitar acesso posicional
df_filtrado_k = df_filtrado_k.reset_index(drop=False)

print(f"🔄 Processando {len(df_filtrado_k)} registros de Reserva...")

# Contadores para estatísticas
registros_processados = 0
registros_com_erro = 0
registros_pulados = 0

# Calcular tempo diurno e noturno para cada linha filtrada
for i in range(len(df_filtrado_k)):
    
    try:
        linha_atual = df_filtrado_k.iloc[i]

        # Para tempo de RESERVA: do checkin ao checkout da própria atividade
        checkin = linha_atual['Checkin']
        start = linha_atual['Start']
        end = linha_atual['End']
        checkout = linha_atual['Checkout']

        # Verificar se há valores nulos
        if pd.isnull(checkin) or pd.isnull(checkout):
            registros_pulados += 1
            continue

        # Verificar se são objetos datetime válidos
        if not hasattr(checkin, 'strftime') or not hasattr(checkout, 'strftime'):
            print(f"⚠️ Valores não são datetime no registro {i} - pulando")
            registros_pulados += 1
            continue

        # 🛑 CONDIÇÃO DE PARADA ESPECÍFICA
        if (pd.notna(linha_atual['End']) and pd.notna(linha_atual['Checkout'])):
            end_atual = linha_atual['End']
            checkout_atual = linha_atual['Checkout']
            
            if (end_atual.strftime("%d/%m/%Y %H:%M") == "05/11/2017 16:45" and 
                checkout_atual.strftime("%d/%m/%Y %H:%M") == "05/11/2017 17:16"):
                print(f"\n🛑 PARADA SOLICITADA no registro {i}!")
                print(f"   • End: {end_atual}")
                print(f"   • Checkout: {checkout_atual}")
                print(f"   • Registros processados até agora: {registros_processados}")
                break

        # Conversão para strings (formato esperado pela função calcular_diurno_noturno)
        checkin_str = checkin.strftime("%d/%m/%Y %H:%M")
        start_str = start.strftime("%d/%m/%Y %H:%M")
        end_str = end.strftime("%d/%m/%Y %H:%M")
        checkout_str = checkout.strftime("%d/%m/%Y %H:%M")

        # Calcular tempo diurno e noturno básico
        tempo_diurno, tempo_noturno = calcular_diurno_noturno(
            checkin_str, start_str, end_str, checkout_str
        )

        # 🔧 CORREÇÃO: Atribuir valores às colunas CORRETAS de RESERVA
        df_filtrado_k.at[i, 'Tempo Reserva Diurno'] = tempo_diurno
        df_filtrado_k.at[i, 'Tempo Reserva Noturno'] = tempo_noturno

        # Preparar feriados
        feriados_list = []
        if isinstance(feriados, pd.DataFrame) and not feriados.empty:
            feriados_list = feriados['date'].dt.strftime('%Y-%m-%d').tolist()

        # Classificar horas especiais (usar objetos datetime originais)
        resultado = classificar_horas_especiais(checkin, checkout, feriados_list)

        # 🔧 CORREÇÃO: Atribuir valores especiais às colunas CORRETAS de RESERVA
        df_filtrado_k.at[i, 'Tempo Reserva Especial Diurno'] = resultado['hora_especial_diurna']
        df_filtrado_k.at[i, 'Tempo Reserva Especial Noturno'] = resultado['hora_especial_noturna']

        registros_processados += 1
        
        # Log a cada 10 registros
        if registros_processados % 10 == 0:
            print(f"✅ Processados {registros_processados} registros...")

    except Exception as e:
        registros_com_erro += 1
        print(f"❌ Erro no registro {i}: {e}")
        if registros_com_erro <= 5:  # Mostrar apenas os primeiros 5 erros
            traceback.print_exc()
        continue

print(f"\n📊 ESTATÍSTICAS DE PROCESSAMENTO:")
print(f"   • Registros processados: {registros_processados}")
print(f"   • Registros com erro: {registros_com_erro}")
print(f"   • Registros pulados: {registros_pulados}")
print(f"   • Total: {registros_processados + registros_com_erro + registros_pulados}")

# Garantir que as colunas existem no DataFrame original
for col in [
    'Tempo Reserva Diurno',
    'Tempo Reserva Noturno',
    'Tempo Reserva Especial Diurno',
    'Tempo Reserva Especial Noturno'
]:
    if col not in df.columns:
        df[col] = pd.Timedelta(0) # ✅ CORRETO: substituir pd.NaT

# Copiar os valores do DataFrame filtrado para o DataFrame original
colunas_para_copiar = [
    'Tempo Reserva Diurno',
    'Tempo Reserva Noturno',
    'Tempo Reserva Especial Diurno',
    'Tempo Reserva Especial Noturno'
]

print("🔄 Transferindo dados calculados para o DataFrame original...")

for coluna in colunas_para_copiar:
    if coluna in df_filtrado_k.columns:
        # Usar os índices originais para transferir os dados
        for i, row in df_filtrado_k.iterrows():
            if pd.notna(row[coluna]):
                indice_original = row['index']
                df.at[indice_original, coluna] = row[coluna]
        
        valores_copiados = df[coluna].notna().sum()
        print(f"✅ Coluna '{coluna}': {valores_copiados} valores copiados")
    else:
        print(f"⚠️ Coluna '{coluna}' não encontrada no df_filtrado_k")

# Verificar resultados
print(f"\n📊 ESTATÍSTICAS FINAIS:")
for coluna in colunas_para_copiar:
    if coluna in df.columns:
        valores_nao_nulos = df[coluna].notna().sum()
        print(f"   • {coluna}: {valores_nao_nulos} valores não nulos")

#############
# chamar a função para criar o nome do arquivo
resultado = montar_caminho_arquivo(
    WORKING_DIRECTORY, 
    INPUT_FILE, 
    'RESERVA')  

caminho_arquivo_gravar = resultado

df_filtrado_k[['Activity', 'Id_Leg', 'Checkin', 'Start', 'End', 'Checkout',
    'Tempo Reserva Diurno', 'Tempo Reserva Noturno',
    'Tempo Reserva Especial Diurno', 'Tempo Reserva Especial Noturno']].to_csv(
    f"{caminho_arquivo_gravar}", index=False, encoding='utf-8')

print(f"✅ DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

################################################################################
# CALCULAR PLANTAO
################################################################################
# Versão mais robusta com tratamento de erros melhorado
import traceback

plantoes = carregar_tipos_plantao()

df_filtrado_l = df[df['Activity'].isin(plantoes)].copy()

# 🔧 CORREÇÃO PRINCIPAL: Usar pd.Timedelta(0) ao invés de pd.Series vazio
for col in ['Tempo Plantao Diurno', 'Tempo Plantao Noturno', 'Tempo Plantao Especial Diurno', 'Tempo Plantao Especial Noturno']:
    if col not in df_filtrado_l.columns:
        df_filtrado_l[col] = pd.Timedelta(0)  # ✅ CORRETO: inicializa com zero

# Resetar o índice para facilitar acesso posicional
df_filtrado_l = df_filtrado_l.reset_index(drop=False)

print(f"🔄 Processando {len(df_filtrado_l)} registros de Plantao...")

# Contadores para estatísticas
registros_processados = 0
registros_com_erro = 0
registros_pulados = 0

# Calcular tempo diurno e noturno para cada linha filtrada
for i in range(len(df_filtrado_l)):
    try:
        linha_atual = df_filtrado_l.iloc[i]

        # Para tempo de PLANTAO: do checkin ao checkout da própria atividade
        checkin = linha_atual['Checkin']
        start = linha_atual['Start']
        end = linha_atual['End']
        checkout = linha_atual['Checkout']

        # Verificar se há valores nulos
        if pd.isnull(checkin) or pd.isnull(checkout):
            print(f"⚠️ Registro {i}: valores nulos encontrados - pulando")
            registros_pulados += 1
            continue

        # Verificar se são objetos datetime válidos
        if not hasattr(checkin, 'strftime') or not hasattr(checkout, 'strftime'):
            print(f"⚠️ Registro {i}: valores não são datetime - pulando")
            registros_pulados += 1
            continue

        # Conversão para strings (formato esperado pela função calcular_diurno_noturno)
        checkin_str = checkin.strftime("%d/%m/%Y %H:%M")
        start_str = start.strftime("%d/%m/%Y %H:%M")
        end_str = end.strftime("%d/%m/%Y %H:%M")
        checkout_str = checkout.strftime("%d/%m/%Y %H:%M")

        # Calcular tempo diurno e noturno básico
        tempo_diurno, tempo_noturno = calcular_diurno_noturno(
            checkin_str, start_str, end_str, checkout_str
        )

        # Atribuir valores às colunas de PLANTAO
        df_filtrado_l.at[i, 'Tempo Plantao Diurno'] = tempo_diurno
        df_filtrado_l.at[i, 'Tempo Plantao Noturno'] = tempo_noturno

        # Preparar feriados
        feriados_list = []
        if isinstance(feriados, pd.DataFrame) and not feriados.empty:
            feriados_list = feriados['date'].dt.strftime('%Y-%m-%d').tolist()

        # Classificar horas especiais (usar objetos datetime originais)
        resultado = classificar_horas_especiais(checkin, checkout, feriados_list)

        # Atribuir valores especiais às colunas de PLANTAO
        df_filtrado_l.at[i, 'Tempo Plantao Especial Diurno'] = resultado['hora_especial_diurna']
        df_filtrado_l.at[i, 'Tempo Plantao Especial Noturno'] = resultado['hora_especial_noturna']

        registros_processados += 1
        
        # Log a cada 10 registros
        if registros_processados % 10 == 0:
            print(f"✅ Processados {registros_processados} registros...")

    except Exception as e:
        registros_com_erro += 1
        print(f"❌ Erro no registro {i}: {e}")
        if registros_com_erro <= 5:
            traceback.print_exc()
        continue

print(f"\n📊 ESTATÍSTICAS DE PROCESSAMENTO:")
print(f"   • Registros processados: {registros_processados}")
print(f"   • Registros com erro: {registros_com_erro}")
print(f"   • Registros pulados: {registros_pulados}")

# 🔧 CORREÇÃO: Garantir que as colunas existem no DataFrame original com tipo correto
for col in [
    'Tempo Plantao Diurno',
    'Tempo Plantao Noturno',
    'Tempo Plantao Especial Diurno',
    'Tempo Plantao Especial Noturno'
]:
    if col not in df.columns:
        df[col] = pd.Timedelta(0)  # ✅ CORRETO: inicializar com zero

# Copiar os valores do DataFrame filtrado para o DataFrame original
colunas_para_copiar = [
    'Tempo Plantao Diurno',
    'Tempo Plantao Noturno',
    'Tempo Plantao Especial Diurno',
    'Tempo Plantao Especial Noturno'
]

print("🔄 Transferindo dados calculados para o DataFrame original...")

for coluna in colunas_para_copiar:
    if coluna in df_filtrado_l.columns:
        # Usar os índices originais para transferir os dados
        for i, row in df_filtrado_l.iterrows():
            if pd.notna(row[coluna]) and row[coluna] != pd.Timedelta(0):
                indice_original = row['index']
                df.at[indice_original, coluna] = row[coluna]
        
        valores_copiados = (df[coluna] != pd.Timedelta(0)).sum()
        print(f"✅ Coluna '{coluna}': {valores_copiados} valores copiados")
    else:
        print(f"⚠️ Coluna '{coluna}' não encontrada no df_filtrado_l")

print(f"\n📊 ESTATÍSTICAS FINAIS:")
for coluna in colunas_para_copiar:
    if coluna in df.columns:
        valores_nao_nulos = (df[coluna] != pd.Timedelta(0)).sum()
        print(f"   • {coluna}: {valores_nao_nulos} valores não nulos")

#############
# chamar a função para criar o nome do arquivo
resultado = montar_caminho_arquivo(
    WORKING_DIRECTORY, 
    INPUT_FILE, 
    'PLANTAO')    

caminho_arquivo_gravar = resultado

df_filtrado_l[['Activity', 'Id_Leg', 'Checkin', 'Start', 'End', 'Checkout',
    'Tempo Plantao Diurno', 'Tempo Plantao Noturno',
    'Tempo Plantao Especial Diurno', 'Tempo Plantao Especial Noturno']].to_csv(
    f"{caminho_arquivo_gravar}", index=False, encoding='utf-8')

print(f"✅ DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

################################################################################
# CALCULAR TREINAMENTO
################################################################################
# Versão mais robusta com tratamento de erros melhorado
import traceback

treinamentos = carregar_tipos_treinamentos()

# 🔍 DIAGNÓSTICO COMPLETO - TREINAMENTO vs PLANTÃO
print("=" * 80)
print("🔍 DIAGNÓSTICO: COMPARAÇÃO PLANTÃO vs TREINAMENTO")
print("=" * 80)

# 1. Verificar as funções de carregamento
print("\n1️⃣ VERIFICANDO FUNÇÕES DE CARREGAMENTO:")
plantoes = carregar_tipos_plantao()
treinamentos = carregar_tipos_treinamentos()

print(f"   • Plantões carregados: {len(plantoes)} itens")
print(f"   • Primeiros 5 plantões: {plantoes[:5]}")
print(f"   • Treinamentos carregados: {len(treinamentos)} itens") 
print(f"   • Primeiros 5 treinamentos: {treinamentos[:5]}")

# 2. Verificar quantos registros cada filtro captura
print("\n2️⃣ VERIFICANDO FILTROS:")
df_plantao_test = df[df['Activity'].isin(plantoes)].copy()
df_treinamento_test = df[df['Activity'].isin(treinamentos)].copy()

print(f"   • Registros de PLANTÃO encontrados: {len(df_plantao_test)}")
print(f"   • Registros de TREINAMENTO encontrados: {len(df_treinamento_test)}")

# 3. Mostrar exemplos de Activities capturadas
if len(df_plantao_test) > 0:
    print(f"   • Exemplos Activities PLANTÃO: {df_plantao_test['Activity'].unique()[:5].tolist()}")
if len(df_treinamento_test) > 0:
    print(f"   • Exemplos Activities TREINAMENTO: {df_treinamento_test['Activity'].unique()[:5].tolist()}")

# 4. Verificar se há Activities em comum
activities_comuns = set(df_plantao_test['Activity'].unique()) & set(df_treinamento_test['Activity'].unique())
print(f"   • Activities em comum: {len(activities_comuns)} - {list(activities_comuns)[:3]}")

print("\n" + "=" * 80)

# ✅ CORREÇÃO APLICADA: Usar df ao invés de df_com_especiais
df_filtrado_m = df[df['Activity'].isin(treinamentos)].copy()

# 🔧 CORREÇÃO PRINCIPAL: Usar pd.Timedelta(0) ao invés de pd.Series vazio
for col in ['Tempo Treinamento Diurno', 'Tempo Treinamento Noturno', 'Tempo Treinamento Especial Diurno', 'Tempo Treinamento Especial Noturno']:
    if col not in df_filtrado_m.columns:
        df_filtrado_m[col] = pd.Timedelta(0)  # ✅ CORRETO: inicializa com zero

# Resetar o índice para facilitar acesso posicional
df_filtrado_m = df_filtrado_m.reset_index(drop=False)

print(f"🔄 Processando {len(df_filtrado_m)} registros de Treinamento...")

# Contadores para estatísticas
registros_processados = 0
registros_com_erro = 0
registros_pulados = 0

# Calcular tempo diurno e noturno para cada linha filtrada
for i in range(len(df_filtrado_m)):
    try:
        linha_atual = df_filtrado_m.iloc[i]

        # Para tempo de TREINAMENTO: do checkin ao checkout da própria atividade
        checkin = linha_atual['Checkin']
        start = linha_atual['Start']
        end = linha_atual['End']
        checkout = linha_atual['Checkout']

        # Verificar se há valores nulos
        if pd.isnull(checkin) or pd.isnull(checkout):
            print(f"⚠️ Registro {i}: valores nulos encontrados - pulando")
            registros_pulados += 1
            continue

        # Verificar se são objetos datetime válidos
        if not hasattr(checkin, 'strftime') or not hasattr(checkout, 'strftime'):
            print(f"⚠️ Registro {i}: valores não são datetime - pulando")
            registros_pulados += 1
            continue

        # Conversão para strings (formato esperado pela função calcular_diurno_noturno)
        checkin_str = checkin.strftime("%d/%m/%Y %H:%M")
        start_str = start.strftime("%d/%m/%Y %H:%M")
        end_str = end.strftime("%d/%m/%Y %H:%M")
        checkout_str = checkout.strftime("%d/%m/%Y %H:%M")

        # Calcular tempo diurno e noturno básico
        tempo_diurno, tempo_noturno = calcular_diurno_noturno(
            checkin_str, start_str, end_str, checkout_str
        )

        # Atribuir valores às colunas de TREINAMENTO (NOMES CORRIGIDOS)
        df_filtrado_m.at[i, 'Tempo Treinamento Diurno'] = tempo_diurno
        df_filtrado_m.at[i, 'Tempo Treinamento Noturno'] = tempo_noturno

        # Preparar feriados
        feriados_list = []
        if isinstance(feriados, pd.DataFrame) and not feriados.empty:
            feriados_list = feriados['date'].dt.strftime('%Y-%m-%d').tolist()

        # Classificar horas especiais (usar objetos datetime originais)
        resultado = classificar_horas_especiais(checkin, checkout, feriados_list)

        # Atribuir valores especiais às colunas de TREINAMENTO (NOMES CORRIGIDOS)
        df_filtrado_m.at[i, 'Tempo Treinamento Especial Diurno'] = resultado['hora_especial_diurna']
        df_filtrado_m.at[i, 'Tempo Treinamento Especial Noturno'] = resultado['hora_especial_noturna']

        registros_processados += 1
        
        # Log a cada 10 registros
        if registros_processados % 10 == 0:
            print(f"✅ Processados {registros_processados} registros...")

    except Exception as e:
        registros_com_erro += 1
        print(f"❌ Erro no registro {i}: {e}")
        if registros_com_erro <= 5:
            traceback.print_exc()
        continue

print(f"\n📊 ESTATÍSTICAS DE PROCESSAMENTO:")
print(f"   • Registros processados: {registros_processados}")
print(f"   • Registros com erro: {registros_com_erro}")
print(f"   • Registros pulados: {registros_pulados}")

# 🔧 CORREÇÃO: Garantir que as colunas existem no DataFrame original com tipo correto (NOMES CORRIGIDOS)
for col in [
    'Tempo Treinamento Diurno',
    'Tempo Treinamento Noturno',
    'Tempo Treinamento Especial Diurno',
    'Tempo Treinamento Especial Noturno'
]:
    if col not in df.columns:
        df[col] = pd.Timedelta(0)  # ✅ CORRETO: inicializar com zero

# Copiar os valores do DataFrame filtrado para o DataFrame original
colunas_para_copiar = [
    'Tempo Treinamento Diurno',
    'Tempo Treinamento Noturno',
    'Tempo Treinamento Especial Diurno',
    'Tempo Treinamento Especial Noturno'
]

print("🔄 Transferindo dados calculados para o DataFrame original...")

for coluna in colunas_para_copiar:
    if coluna in df_filtrado_m.columns:
        # Usar os índices originais para transferir os dados
        for i, row in df_filtrado_m.iterrows():
            if pd.notna(row[coluna]) and row[coluna] != pd.Timedelta(0):
                indice_original = row['index']
                df.at[indice_original, coluna] = row[coluna]
        
        valores_copiados = (df[coluna] != pd.Timedelta(0)).sum()
        print(f"✅ Coluna '{coluna}': {valores_copiados} valores copiados")
    else:
        print(f"⚠️ Coluna '{coluna}' não encontrada no df_filtrado_m")

print(f"\n📊 ESTATÍSTICAS FINAIS:")
for coluna in colunas_para_copiar:
    if coluna in df.columns:
        valores_nao_nulos = (df[coluna] != pd.Timedelta(0)).sum()
        print(f"   • {coluna}: {valores_nao_nulos} valores não nulos")

# verificar colunas do df que estejam como 0 e substituir por 0 days 00:00:00
for col in [
    'Tempo Treinamento Diurno',
    'Tempo Treinamento Noturno',
    'Tempo Treinamento Especial Diurno',
    'Tempo Treinamento Especial Noturno'
]:
    if col in df.columns:
        df[col] = df[col].replace(0, pd.Timedelta('0 days 00:00:00'))
# 🔧 CORREÇÃO CRÍTICA: Usar nomes de colunas corretos e configurar CSV adequadamente


############
# chamar a função para criar o nome do arquivo
resultado = montar_caminho_arquivo(
    WORKING_DIRECTORY, 
    INPUT_FILE, 
    'TREINAMENTO')    

caminho_arquivo_gravar = resultado

# 🔧 CORREÇÃO CRÍTICA: Usar nomes de colunas corretos e configurar CSV adequadamente
df_filtrado_m[['Activity', 'Id_Leg', 'Checkin', 'Start', 'End', 'Checkout',
    'Tempo Treinamento Diurno', 'Tempo Treinamento Noturno',
    'Tempo Treinamento Especial Diurno', 'Tempo Treinamento Especial Noturno']].to_csv(
    f"{caminho_arquivo_gravar}", 
    index=False, 
    encoding='utf-8',
    sep=',')  # Garantir vírgula como separador
    #quotechar='"',  # Usar aspas duplas para strings
    #quoting=1)  # Quotar apenas quando necessário

print(f"✅ DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

################################################################################
# Definir a lista de colunas que devem ser convertidas para timedelta
colunas = [
    'Tempo Apresentacao Diurno',
    'Tempo Apresentacao Noturno',
    'Tempo Apresentacao Especial Diurno',
    'Tempo Apresentacao Especial Noturno',
    'Tempo Apos Corte Diurno',
    'Tempo Apos Corte Noturno',
    'Tempo Apos Corte Especial Diurno',
    'Tempo Apos Corte Especial Noturno',
    'Tempo Solo Diurno',
    'Tempo Solo Noturno',
    'Tempo Solo Especial Diurno',
    'Tempo Solo Especial Noturno',
    'Tempo Jornada Diurno',
    'Tempo Jornada Noturno',
    'Tempo Jornada Especial Diurno',
    'Tempo Jornada Especial Noturno',
    'Tempo Repouso Diurno',
    'Tempo Repouso Noturno',
    'Tempo Repouso Especial Diurno',
    'Tempo Repouso Especial Noturno',
    'Tempo Repouso Extra Diurno',
    'Tempo Repouso Extra Noturno',
    'Tempo Repouso Extra Especial Diurno',
    'Tempo Repouso Extra Especial Noturno',
    'Tempo Reserva Diurno',
    'Tempo Reserva Noturno',
    'Tempo Reserva Especial Diurno',
    'Tempo Reserva Especial Noturno',
    'Tempo Plantao Diurno',
    'Tempo Plantao Noturno',
    'Tempo Plantao Especial Diurno',
    'Tempo Plantao Especial Noturno',
    'Tempo Treinamento Diurno',
    'Tempo Treinamento Noturno',
    'Tempo Treinamento Especial Diurno',
    'Tempo Treinamento Especial Noturno'
]

df.info()
print(df.head(2))

df_resultado = df.copy()
    
for col in colunas:
    if col in df_resultado.columns:
        try:
            # Como os dados já estão no formato correto, só precisamos converter o dtype
            df_resultado[col] = pd.to_timedelta(df_resultado[col])
            print(f"✅ Coluna '{col}' convertida para timedelta64")
            
        except Exception as e:
            print(f"❌ Erro ao converter coluna '{col}': {e}")
    else:
        print(f"⚠️ Coluna '{col}' não encontrada no DataFrame")

df_resultado['Activity'] = df_resultado['Activity'].astype('category')
df_resultado['Id_Leg'] = df_resultado['Id_Leg'].astype('category')
df_resultado['Dep'] = df_resultado['Dep'].astype('category')
df_resultado['Arr'] = df_resultado['Arr'].astype('category')
df_resultado['AcVer'] = df_resultado['AcVer'].astype('category')
df_resultado['DD'] = df_resultado['DD'].astype('category')
df_resultado['CAT'] = df_resultado['CAT'].astype('category')
df_resultado['Crew'] = df_resultado['Crew'].astype('category')
df_resultado['Internacional'] = df_resultado['Internacional'].astype('category')

df = df_resultado.copy()

################################################################################
import pandas as pd
from sqlalchemy import create_engine
import numpy as np

def otimizar_colunas_object(df):
    """
    Otimiza as colunas object restantes para o menor tamanho possível
    """
    print("=== OTIMIZAÇÃO DAS COLUNAS OBJECT ===\n")
    
    # Colunas object identificadas no seu DataFrame
    colunas_object = ['Start_date', 'End_date', 'Feriado', 'Vespera', 
                      'Checkin_Dia_Semana', 'Start_Dia_Semana', 
                      'End_Dia_Semana', 'Checkout_Dia_Semana']
    
    memoria_original = df.memory_usage(deep=True).sum()
    
    for col in colunas_object:
        if col in df.columns:
            print(f"--- {col} ---")
            print(f"Valores únicos: {df[col].nunique()}")
            print(f"Total valores: {len(df[col])}")
            
            original_memory = df[col].memory_usage(deep=True)
            unique_ratio = df[col].nunique() / len(df[col])
            
            # Mostrar alguns exemplos
            print(f"Exemplos: {df[col].dropna().unique()[:3].tolist()}")
            
            if unique_ratio < 0.5:  # Muitos valores repetidos
                df[col] = df[col].astype('category')
                new_memory = df[col].memory_usage(deep=True)
                reducao = ((original_memory - new_memory) / original_memory) * 100
                print(f"✅ Convertido para category - Redução: {reducao:.1f}%")
            else:  # Muitos valores únicos
                df[col] = df[col].astype('string')
                new_memory = df[col].memory_usage(deep=True)
                reducao = ((original_memory - new_memory) / original_memory) * 100
                print(f"✅ Convertido para string - Redução: {reducao:.1f}%")
            
            print()
    
    memoria_nova = df.memory_usage(deep=True).sum()
    reducao_total = ((memoria_original - memoria_nova) / memoria_original) * 100
    
    print(f"RESUMO FINAL:")
    print(f"Memória original: {memoria_original/1024/1024:.2f} MB")
    print(f"Memória otimizada: {memoria_nova/1024/1024:.2f} MB")
    print(f"Redução total: {reducao_total:.1f}%")
    
    return df

def preparar_para_sql_server(df):
    """
    Prepara o DataFrame para importação no SQL Server
    """
    print("\n=== PREPARAÇÃO PARA SQL SERVER ===\n")
    
    df_sql = df.copy()
    
    # Converter timedelta para string (SQL Server não tem timedelta nativo)
    colunas_timedelta = df_sql.select_dtypes(include=['timedelta64[ns]']).columns
    print(f"Convertendo {len(colunas_timedelta)} colunas timedelta para string...")
    
    for col in colunas_timedelta:
        # Converter para formato HH:MM:SS
        df_sql[col] = df_sql[col].dt.total_seconds().apply(
            lambda x: f"{int(x//3600):02d}:{int((x%3600)//60):02d}:{int(x%60):02d}" 
            if pd.notna(x) else None
        )
        print(f"  ✅ {col}: timedelta → string (HH:MM:SS)")
    
    # Converter category para string para SQL Server
    colunas_category = df_sql.select_dtypes(include=['category']).columns
    print(f"\nConvertendo {len(colunas_category)} colunas category para string...")
    
    for col in colunas_category:
        df_sql[col] = df_sql[col].astype('string')
        print(f"  ✅ {col}: category → string")
    
    # Verificar tipos finais
    print(f"\n=== TIPOS FINAIS PARA SQL SERVER ===")
    print(df_sql.dtypes.value_counts())
    
    return df_sql

def criar_tabela_sql_server(df, nome_tabela, connection_string):
    """
    Cria a tabela no SQL Server com os tipos apropriados
    """
    # Mapear tipos pandas para SQL Server
    type_mapping = {
        'datetime64[ns]': 'DATETIME2',
        'string': 'NVARCHAR(255)',
        'object': 'NVARCHAR(255)',
        'int64': 'BIGINT',
        'float64': 'FLOAT',
        'bool': 'BIT'
    }
    
    # Gerar CREATE TABLE statement
    create_statement = f"CREATE TABLE {nome_tabela} (\n"
    
    for col, dtype in df.dtypes.items():
        col_name = col.replace(' ', '_').replace('-', '_')  # Limpar nomes de colunas
        sql_type = type_mapping.get(str(dtype), 'NVARCHAR(255)')
        
        # Ajustar tamanhos específicos baseado no conteúdo
        if sql_type == 'NVARCHAR(255)' and col in df.columns:
            max_len = df[col].astype(str).str.len().max()
            if pd.notna(max_len):
                sql_type = f'NVARCHAR({min(max(int(max_len * 1.2), 50), 4000)})'
        
        nullable = "NULL" if df[col].isna().any() else "NOT NULL"
        create_statement += f"    [{col_name}] {sql_type} {nullable},\n"
    
    create_statement = create_statement.rstrip(',\n') + "\n);"
    
    return create_statement

def importar_para_sql_server(df, nome_tabela, connection_string, 
                           chunk_size=1000, if_exists='replace'):
    """
    Importa o DataFrame para SQL Server
    """
    print(f"\n=== IMPORTANDO PARA SQL SERVER ===")
    print(f"Tabela: {nome_tabela}")
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns)}")
    
    try:
        # Criar engine
        engine = create_engine(connection_string)
        
        # Limpar nomes das colunas para SQL Server
        df_import = df.copy()
        df_import.columns = [col.replace(' ', '_').replace('-', '_') 
                           for col in df_import.columns]
        
        # Importar dados
        df_import.to_sql(
            name=nome_tabela,
            con=engine,
            if_exists=if_exists,  # 'replace', 'append', 'fail'
            index=False,
            chunksize=chunk_size,
            method='multi'  # Mais rápido para grandes volumes
        )
        
        print(f"✅ Importação concluída com sucesso!")
        print(f"   Método: {if_exists}")
        print(f"   Chunk size: {chunk_size:,}")
        
        # Verificar importação
        with engine.connect() as conn:
            result = conn.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            count = result.scalar()
            print(f"   Registros na tabela: {count:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {str(e)}")
        return False

def pipeline_completo(df, nome_tabela, connection_string):
    """
    Pipeline completo: otimização + preparação + importação
    """
    print("🚀 INICIANDO PIPELINE COMPLETO\n")
    
    # Passo 1: Otimizar colunas object
    df_otimizado = otimizar_colunas_object(df)
    
    # Passo 2: Preparar para SQL Server  
    df_sql = preparar_para_sql_server(df_otimizado)
    
    # Passo 3: Gerar CREATE TABLE (opcional)
    create_statement = criar_tabela_sql_server(df_sql, nome_tabela, connection_string)
    print(f"\n=== CREATE TABLE STATEMENT ===")
    print(create_statement[:500] + "..." if len(create_statement) > 500 else create_statement)
    
    # Passo 4: Importar
    sucesso = importar_para_sql_server(df_sql, nome_tabela, connection_string)
    
    if sucesso:
        print("\n🎉 PIPELINE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ PIPELINE FALHOU NA IMPORTAÇÃO")
    
    return df_sql, create_statement

# ===== EXEMPLO DE USO =====

# 1. String de conexão SQL Server
"""
connection_string = (
    "mssql+pyodbc://usuario:senha@servidor/database"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&TrustServerCertificate=yes"
)
"""

# 2. Executar pipeline completo
# df_final, create_sql = pipeline_completo(df, 'tabela_voos', connection_string)

# 3. Ou executar por partes:
df_otimizado = otimizar_colunas_object(df)
# df_sql = preparar_para_sql_server(df_otimizado)
# importar_para_sql_server(df_sql, 'tabela_voos', connection_string)

working_directory = os.getcwd()
caminho_arquivo_gravar = working_directory + '/Arquivo_para_SQL'
df_otimizado.to_csv(caminho_arquivo_gravar, index=False, encoding='utf-8')
print(f"✅ DataFrame atualizado salvo em: {caminho_arquivo_gravar}")

print(df_otimizado.head(100))
