"""
###############################################################################
#                            CALCULOS FINAIS                                 #
#                       SISTEMA DE CÁLCULOS AERONAUTAS AZUL                  #
###############################################################################

Descrição: Script principal para processamento completo de escalas de aeronautas
           com cálculos de horas diurnas, noturnas, especiais e regulamentares

Autor: Ricardo Lazzarini
Data: 27/06/2024
Versão: 2.1 - Integração com tipos_reserva.json
Última atualização: 29/06/2025

Funcionalidades:
- Importação e validação de dados de escala
- Cálculos automáticos de todas as categorias de tempo
- Classificação de atividades (voo, reserva, plantão, treinamento)
- Carregamento automático de tipos de reserva do arquivo JSON
- Tratamento robusto de datas brasileiras
- Interface de usuário aprimorada
- Relatórios de execução detalhados
- Sistema de monitoramento e debug avançado

###############################################################################
"""

# =============================================================================
# 1. IMPORTAÇÃO DE BIBLIOTECAS
# =============================================================================

import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm
import os
import sys
import re
import warnings
import time
import json

# Importar funções de cálculo de repouso
try:
    from funcoes_repouso import calcular_tempos_repouso, calcular_tempos_repouso_extra
    print("✅ Módulo funcoes_repouso carregado com sucesso")
except ImportError:
    print("⚠️ Módulo funcoes_repouso não encontrado - funções de repouso serão definidas localmente")
    
    def calcular_tempos_repouso(df, feriados=None):
        """Função de fallback para cálculo de repouso"""
        print("⚙️ Calculando tempos de repouso (fallback)...")
        # Implementação básica
        if 'Repouso' in df.columns:
            # Garantir que as colunas existam
            if 'Tempo Repouso Diurno' not in df.columns:
                df['Tempo Repouso Diurno'] = pd.Timedelta(0)
            if 'Tempo Repouso Noturno' not in df.columns:
                df['Tempo Repouso Noturno'] = pd.Timedelta(0)
            if 'Tempo Repouso Especial Diurno' not in df.columns:
                df['Tempo Repouso Especial Diurno'] = pd.Timedelta(0)
            if 'Tempo Repouso Especial Noturno' not in df.columns:
                df['Tempo Repouso Especial Noturno'] = pd.Timedelta(0)
                
            df['Tempo Repouso Diurno'] = df['Repouso'].fillna(pd.Timedelta(0))
        return df
    
    def calcular_tempos_repouso_extra(df, feriados=None):
        """Função de fallback para cálculo de repouso extra"""
        print("⚙️ Calculando tempos de repouso extra (fallback)...")
        # Implementação básica
        if 'Repouso Extra' in df.columns:
            # Garantir que as colunas existam
            if 'Tempo Repouso Extra Diurno' not in df.columns:
                df['Tempo Repouso Extra Diurno'] = pd.Timedelta(0)
            if 'Tempo Repouso Extra Noturno' not in df.columns:
                df['Tempo Repouso Extra Noturno'] = pd.Timedelta(0)
            if 'Tempo Repouso Extra Especial Diurno' not in df.columns:
                df['Tempo Repouso Extra Especial Diurno'] = pd.Timedelta(0)
            if 'Tempo Repouso Extra Especial Noturno' not in df.columns:
                df['Tempo Repouso Extra Especial Noturno'] = pd.Timedelta(0)
                
            df['Tempo Repouso Extra Diurno'] = df['Repouso Extra'].fillna(pd.Timedelta(0))
        return df

# Configuração inicial
warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None

# =============================================================================
# SISTEMA DE MONITORAMENTO E LOG AVANÇADO
# =============================================================================

class MonitorExecucao:
    """Classe para monitoramento avançado da execução do script"""
    
    def __init__(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f"log_execucao_{timestamp}.txt"
        self.status_file = f"status_execucao_{timestamp}.json"
        self.pid_file = f"pid_execucao_{timestamp}.txt"
        
        # Registra o PID do processo
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
    def iniciar_monitoramento(self):
        """Inicia o sistema de monitoramento"""
        status = {
            "status": "INICIANDO",
            "inicio": datetime.now().isoformat(),
            "ultimo_heartbeat": datetime.now().isoformat(),
            "etapa_atual": "Iniciando sistema",
            "progresso": 0,
            "pid": os.getpid(),
            "erro": None
        }
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
            
    def atualizar_status(self, etapa, progresso, status="EXECUTANDO"):
        """Atualiza o status da execução"""
        try:
            # Lê status atual
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
            except Exception:
                dados = {}
                
            # Atualiza informações
            dados.update({
                "status": status,
                "ultimo_heartbeat": datetime.now().isoformat(),
                "etapa_atual": etapa,
                "progresso": progresso
            })
            
            # Salva status atualizado
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            
    def finalizar_monitoramento(self, sucesso=True, erro=None):
        """Finaliza o monitoramento"""
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except Exception:
            dados = {}
            
        dados.update({
            "status": "CONCLUIDO" if sucesso else "ERRO",
            "fim": datetime.now().isoformat(),
            "ultimo_heartbeat": datetime.now().isoformat(),
            "progresso": 100 if sucesso else dados.get("progresso", 0),
            "erro": str(erro) if erro else None
        })
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

# Instância global do monitor
monitor = MonitorExecucao()

# =============================================================================
# 2. CONFIGURAÇÃO DA INTERFACE DE USUÁRIO
# =============================================================================

def configurar_interface():
    """Configura a interface gráfica inicial"""
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.focus_force()
    return root

# =============================================================================
# 3. FUNÇÕES DE SELEÇÃO E LEITURA DE ARQUIVOS
# =============================================================================

def selecionar_arquivo(root):
    """
    Interface para seleção de diretório e arquivo de dados
    
    Args:
        root (tk.Tk): Instância da interface Tkinter
    
    Returns:
        tuple: (diretorio, nome_arquivo)
    """
    print("🔍 SELEÇÃO DE ARQUIVOS")
    print("=" * 50)
    
    # Selecionar diretório

    # SELECIONAR O DIRETÓRIO COMPLETO DAS ESCALAS COM TODOS OS CÁLCULOS
    messagebox.showinfo("Seleção diretório", "Selecione o diretório dos dados")
    root.update()

    diretorio = filedialog.askdirectory(title="Selecione o diretório dos dados")
    if not diretorio:
        print("❌ Nenhum diretório selecionado.")
        sys.exit(1)

    # Selecionar arquivo no diretório escolhido
    messagebox.showinfo("Seleção de Arquivo", "Selecione o arquivo '- CALCULOS_EM_TIMEDELTA'")
    root.update()

    arquivo_path = filedialog.askopenfilename(
        initialdir=diretorio, 
        title="Selecione o arquivo - CÁLCULOS EM TIMEDELTA"
    )
    if not arquivo_path:
        print("❌ Nenhum arquivo selecionado.")
        sys.exit(1)

    nome_arquivo = os.path.basename(arquivo_path)
    print(f"📂 Diretório: {diretorio}")
    print(f"📄 Arquivo: {nome_arquivo}")
    
    return diretorio, nome_arquivo

def carregar_dados_principais(caminho_arquivo):
    """
    Carrega o arquivo CSV principal com tratamento robusto de datas
    
    Args:
        caminho_arquivo (str): Caminho completo do arquivo
        
    Returns:
        tuple: (DataFrame, nome_aeronauta)
    """
    try:
        df = pd.read_csv(
            caminho_arquivo, 
            sep=',', 
            encoding='utf-8'
            # Removido parse_dates para fazer conversão manual mais tarde
        )
        
        # Extrair nome do aeronauta do caminho do arquivo
        match = re.search(r'-\s*(.*?)\s*\(', caminho_arquivo)
        nome_aeronauta = match.group(1) if match else "Não identificado"
        
        print(f"👤 Aeronauta: {nome_aeronauta}")
        print(f"📊 Registros carregados: {len(df):,}")
        
        return df, nome_aeronauta
        
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        raise

# =============================================================================
# 4. FUNÇÕES DE CARREGAMENTO DE DADOS AUXILIARES
# =============================================================================

def carregar_feriados():
    """
    Carrega dados de feriados nacionais
    
    Returns:
        pandas.DataFrame: DataFrame com feriados
    """
    try:
        caminho_feriados = r"G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS\feriados.json"
        feriados = pd.read_json(caminho_feriados)
        feriados['date'] = pd.to_datetime(feriados['date'])
        
        print(f"📅 Feriados carregados: {len(feriados)}")
        return feriados
        
    except Exception as e:
        print(f"⚠️ Erro ao carregar feriados: {e}")
        return pd.DataFrame()

def carregar_siglas_sabre():
    """
    Carrega e classifica siglas SABRE por tipo de atividade
    
    Returns:
        tuple: (lista_reservas, lista_plantoes, lista_treinamentos, lista_tipos_voo)
    """
    try:
        caminho_siglas = r"G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS\Siglas Sabre 1.xlsx"
        siglas_sabre = pd.read_excel(caminho_siglas, engine='openpyxl')
        
        # Usar arquivo JSON para reservas
        l_reservas = carregar_tipos_reserva()
        
        # Carregar tipos de voo do arquivo JSON
        l_tipos_voo = carregar_tipos_voo()
        
        l_plantoes = siglas_sabre[
            siglas_sabre['SIGLA'].str.startswith(('P', 'p', 'S', 's'), na=False)
        ]['SIGLA'].tolist()
        
        l_treinamentos = [
            'ALA', 'ANC', 'APT', 'ATR', 'AV', 'AVI', 'AVS', 'AVT', 'CA2', 'CA3',
            'CAA', 'CAE', 'CAP', 'CB2', 'CB3', 'CBA', 'CBE', 'CCL', 'CEA', 'CFI',
            'CI2', 'CI3', 'CIA', 'CIE', 'COL', 'CP2', 'CP3', 'CPA', 'CPE', 'CRM',
            'CPT', 'DGR', 'DH', 'DL', 'DOB', 'EGP', 'ENP', 'EPA', 'EPI', 'FIV',
            'G3', 'GCI', 'GF', 'GS', 'ICM', 'JJ', 'OPT', 'PC1', 'PC2', 'PC3',
            'PIP', 'PIV', 'PP1', 'PP2', 'PSM', 'REI', 'REQ', 'SFX', 'S02', 'S06',
            'S10', 'S14', 'S18', 'S22', 'SIT', 'SLC', 'SCL', 'SLF', 'T20', 'T30',
            'TAI', 'TEM', 'TFX', 'UA', 'UNI', 'V20', 'V30', 'VAE', 'VAT', 'VEB',
            'VFT', 'XEA', 'XQ2', 'XQ3'
        ]
        
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
        caminho_json_comum = r"G:\PROJETOS PYTHON\aeronautas_azul\ARQUIVOS COMUNS\tipos_reserva.json"
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

def carregar_tipos_voo():
    """
    Carrega tipos de voo do arquivo JSON
    
    Returns:
        list: Lista de códigos de atividades de voo
    """
    
    try:
        # Primeiro tenta carregar do diretório local
        caminho_json_local = "tipos_voo.json"
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

# =============================================================================
# 5. FUNÇÕES AUXILIARES PARA TRATAMENTO DE DATAS
# =============================================================================

def converter_datas_robusta(df, colunas_data):
    """
    Converte colunas de data de forma robusta, tentando múltiplos formatos
    
    Args:
        df (pandas.DataFrame): DataFrame com as colunas de data
        colunas_data (list): Lista de nomes das colunas de data
        
    Returns:
        pandas.DataFrame: DataFrame com datas convertidas
    """
    print("📅 Convertendo datas com método robusto...")
    
    for coluna in colunas_data:
        if coluna in df.columns:
            print(f"   Convertendo coluna: {coluna}")
            
            # DEBUG: Mostrar formato original
            sample_values = df[coluna].dropna().head(3).tolist()
            print(f"   DEBUG - Formato original: {sample_values}")
            
            try:
                # Primeira tentativa: sem especificar formato (mais robusta)
                df[coluna] = pd.to_datetime(df[coluna], errors='coerce')
                valores_nat = df[coluna].isna().sum()
                print(f"   ✅ {coluna}: conversão automática ({valores_nat} NaT)")
                
                # Se muitos NaT, tentar formato brasileiro
                if valores_nat > len(df) * 0.1:  # Se mais de 10% são NaT
                    print(f"   ⚠️ Muitos NaT ({valores_nat}), tentando formato brasileiro...")
                    df[coluna] = pd.to_datetime(df[coluna], format='%d/%m/%Y %H:%M', errors='coerce')
                    valores_nat_br = df[coluna].isna().sum()
                    print(f"   Resultado formato BR: {valores_nat_br} NaT")
                    
                    # Se ainda muitos NaT, voltar para automático
                    if valores_nat_br >= valores_nat:
                        df[coluna] = pd.to_datetime(df[coluna], errors='coerce')
                        print("   Mantendo conversão automática")
                
            except Exception as e:
                print(f"   ❌ {coluna}: erro na conversão - {e}")
                # Mantém a coluna original se não conseguir converter
                continue
    
    return df

# =============================================================================
# 6. FUNÇÕES DE PREPARAÇÃO DO DATAFRAME
# =============================================================================

def preparar_dataframe(df, feriados):
    """
    Prepara o DataFrame principal com colunas e conversões necessárias
    
    Args:
        df (pandas.DataFrame): DataFrame principal
        feriados (pandas.DataFrame): DataFrame de feriados
        
    Returns:
        pandas.DataFrame: DataFrame preparado
    """
    print("\n🔧 PREPARAÇÃO DO DATAFRAME")
    print("=" * 50)
    
    # Verificar e limpar colunas duplicadas
    colunas_duplicadas = df.columns[df.columns.duplicated()]
    if len(colunas_duplicadas) > 0:
        print(f"🧹 Removendo {len(colunas_duplicadas)} colunas duplicadas")
        df = df.loc[:, ~df.columns.duplicated()]
    
    # Converter datas principais com método robusto
    colunas_data = ['Checkin', 'Start', 'End', 'Checkout']
    df = converter_datas_robusta(df, colunas_data)
    df['Dia_Semana'] = df['Checkin'].dt.weekday
    
    # IMPORTANTE: Converter coluna Jornada para timedelta
    if 'Jornada' in df.columns:
        try:
            df['Jornada'] = pd.to_timedelta(df['Jornada'], errors='coerce')
            print("✅ Coluna 'Jornada' convertida para timedelta")
        except Exception as e:
            print(f"⚠️ Erro ao converter coluna 'Jornada': {e}")
    
    # Adicionar informação de feriados
    if not feriados.empty:
        df['Feriado'] = df['Checkin'].dt.date.isin(feriados['date'].dt.date)
    else:
        df['Feriado'] = False
    
    # Verificar coluna Tempo Apresentacao
    if 'Tempo Apresentacao' in df.columns:
        try:
            df['Tempo Apresentacao'] = pd.to_timedelta(df['Tempo Apresentacao'], errors='coerce')
            total_horas = df['Tempo Apresentacao'].sum()
            print(f"⏱️ Total horas apresentação: {total_horas}")
        except Exception as e:
            print(f"⚠️ Erro ao converter 'Tempo Apresentacao': {e}")
    else:
        print("⚠️ Coluna 'Tempo Apresentacao' não encontrada")
    
    # Verificar outras colunas timedelta importantes
    # NOTA: 'Tempo Solo' NÃO é convertida aqui para preservar o valor original do CSV
    # A conversão será feita internamente na função calcular_tempos_solo()
    colunas_timedelta = ['Repouso', 'Repouso Extra']
    for coluna in colunas_timedelta:
        if coluna in df.columns:
            try:
                df[coluna] = pd.to_timedelta(df[coluna], errors='coerce')
                print(f"✅ Coluna '{coluna}' convertida para timedelta")
            except Exception as e:
                print(f"⚠️ Erro ao converter '{coluna}': {e}")
    
    # Log específico para a coluna Tempo Solo (preservação)
    if 'Tempo Solo' in df.columns:
        print(f"🔒 Coluna 'Tempo Solo' preservada no formato original: {df['Tempo Solo'].dtype}")
        registros_tempo_solo = df['Tempo Solo'].notna().sum()
        print(f"📊 Registros com Tempo Solo: {registros_tempo_solo}")
    
    print(f"✅ DataFrame preparado: {len(df)} registros, {len(df.columns)} colunas")
    return df

def criar_colunas_calculo(df):
    """
    Cria todas as colunas necessárias para os cálculos
    
    Args:
        df (pandas.DataFrame): DataFrame principal
        
    Returns:
        pandas.DataFrame: DataFrame com novas colunas
    """
    print("\n📊 CRIAÇÃO DE COLUNAS DE CÁLCULO")
    print("=" * 50)
    
    tipos_tempo = [
        'Apresentacao', 'Apos Corte', 'Solo', 'Jornada', 
        'Repouso', 'Repouso Extra', 'Reserva', 'Plantao', 'Treinamento'
    ]
    
    classificacoes = ['Diurno', 'Noturno', 'Especial Diurno', 'Especial Noturno']
    
    # Criar colunas de forma organizada
    colunas_criadas = 0
    for tipo in tipos_tempo:
        for classe in classificacoes:
            nome_coluna = f'Tempo {tipo} {classe}'
            if nome_coluna not in df.columns:
                df[nome_coluna] = pd.Timedelta('0 days 00:00:00')
                colunas_criadas += 1
    
    # Colunas especiais adicionais
    colunas_especiais = [
        'Tempo Apos Corte', 'Tempo Plantao', 'Tempo Treinamento'
    ]
    
    for coluna in colunas_especiais:
        if coluna not in df.columns:
            df[coluna] = pd.Timedelta('0 days 00:00:00')
            colunas_criadas += 1
    
    print(f"✅ {colunas_criadas} novas colunas criadas")
    print(f"📊 Total de colunas: {len(df.columns)}")
    return df

# =============================================================================
# 6. FUNÇÕES DE CÁLCULO ESPECÍFICAS
# =============================================================================

def calcular_tempos_apresentacao(df, feriados=None):
    """
    Calcula os tempos de apresentação por categoria baseado nas regras específicas
    
    Regras Gerais:
    - Se Tempo Apresentacao > 0 e Checkin entre 06:01 e 17:59 → Tempo Apresentacao Diurno
    - Se Tempo Apresentacao > 0 e Checkin entre 18:00 e 06:00 → Tempo Apresentacao Noturno
    - Se Dia_Semana = 5 e Checkin ≥ 18:00 → Tempo Apresentacao Especial Noturno
    - Se Dia_Semana = 6 → Tempo Apresentacao Especial Noturno
    
    Regras Especiais (quando Checkin = Start):
    1. Dia_Semana ≠ 6 e Checkin entre 06:01-17:59 → Tempo Apresentacao Diurno (demais zeradas)
    2. Dia_Semana ≠ 5 e Checkin ≥ 18:00 → Tempo Apresentacao Noturno (demais zeradas)
    3. Dia_Semana = 5 e Checkin ≥ 18:00 → Tempo Apresentacao Especial Noturno (demais zeradas)
    4. Dia_Semana = 6 e Checkin ≥ 06:01 → Tempo Apresentacao Especial Diurno (demais zeradas)
    
    Regra de Véspera de Feriado:
    - Se apresentação ocorrer após 21h em véspera de feriado → aloca TAMBÉM em Especial Noturno (adicional)
    
    Regra de Dia de Feriado:
    - Se apresentação ocorrer em feriado → aloca TAMBÉM em Especial correspondente (adicional)
    - Feriado diurno: mantém Diurno + adiciona Especial Diurno
    - Feriado noturno: mantém Noturno + adiciona Especial Noturno
    
    IMPORTANTE: Valores especiais são ADICIONAIS aos valores base para permitir cálculos de pagamento corretos
    
    Args:
        df (pandas.DataFrame): DataFrame principal
        feriados (pandas.DataFrame): DataFrame com datas de feriados (opcional)
        
    Returns:
        pandas.DataFrame: DataFrame atualizado
    """
    
    def verificar_vespera_feriado(data_checkin, feriados_df):
        """
        Verifica se uma data é véspera de feriado
        
        Args:
            data_checkin (datetime): Data/hora do checkin
            feriados_df (pandas.DataFrame): DataFrame com feriados
            
        Returns:
            bool: True se for véspera de feriado
        """
        if feriados_df is None or feriados_df.empty:
            return False
            
        if pd.isna(data_checkin):
            return False
            
        # Obter data do checkin (sem horário) 
        data_checkin_date = data_checkin.date()
        
        # Verificar se o dia seguinte é feriado
        data_seguinte = data_checkin_date + timedelta(days=1)
        
        # Verificar se alguma data de feriado corresponde ao dia seguinte
        for _, feriado_row in feriados_df.iterrows():
            if feriado_row['date'].date() == data_seguinte:
                return True
                
        return False

    def verificar_dia_feriado(row, feriados_df):
        """
        Verifica se uma linha tem alguma data que é feriado
        Considera as colunas: Checkin, Start, End, Checkout
        
        Args:
            row (pandas.Series): Linha do DataFrame com as datas
            feriados_df (pandas.DataFrame): DataFrame com feriados
            
        Returns:
            bool: True se alguma data for feriado
        """
        if feriados_df is None or feriados_df.empty:
            return False
        
        # Lista de colunas de data para verificar
        colunas_data = ['Checkin', 'Start', 'End', 'Checkout']
        
        # Verificar cada coluna de data
        for coluna in colunas_data:
            if coluna in row.index and pd.notna(row[coluna]):
                try:
                    # Converter para datetime se necessário
                    if isinstance(row[coluna], str):
                        data_verificar = pd.to_datetime(row[coluna])
                    else:
                        data_verificar = row[coluna]
                    
                    # Obter apenas a data (sem horário)
                    data_verificar_date = data_verificar.date()
                    
                    # Verificar se essa data é feriado
                    for _, feriado_row in feriados_df.iterrows():
                        if feriado_row['date'].date() == data_verificar_date:
                            return True
                        
                except Exception:
                    # Se houver erro na conversão, continuar para próxima coluna
                    continue
    
    print("⚙️ Calculando tempos de apresentação...")
    
    # Verificar se feriados foram fornecidos
    if feriados is not None and not feriados.empty:
        print(f"📅 Utilizando {len(feriados)} feriados para verificação de vésperas")
    else:
        print("⚠️ Nenhum feriado fornecido - regra de véspera de feriado será ignorada")
    
    # Verificar se as colunas necessárias existem
    if 'Tempo Apresentacao' not in df.columns:
        print("⚠️ Coluna 'Tempo Apresentacao' não encontrada no dataset")
        return df
    
    if 'Checkin' not in df.columns:
        print("⚠️ Coluna 'Checkin' não encontrada no dataset")
        return df
    
    if 'Start' not in df.columns:
        print("⚠️ Coluna 'Start' não encontrada no dataset")
        return df
    
    # Converter coluna Checkin para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df['Checkin']):
        try:
            df['Checkin'] = pd.to_datetime(df['Checkin'])
            print("✅ Coluna 'Checkin' convertida para datetime")
        except Exception as e:
            print(f"❌ Erro ao converter coluna 'Checkin': {e}")
            return df
    
    # Converter coluna Start para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df['Start']):
        try:
            df['Start'] = pd.to_datetime(df['Start'])
            print("✅ Coluna 'Start' convertida para datetime")
        except Exception as e:
            print(f"❌ Erro ao converter coluna 'Start': {e}")
            return df
    
    # Converter coluna Tempo Apresentacao para timedelta se necessário
    if not pd.api.types.is_timedelta64_dtype(df['Tempo Apresentacao']):
        try:
            df['Tempo Apresentacao'] = pd.to_timedelta(df['Tempo Apresentacao'])
            print("✅ Coluna 'Tempo Apresentacao' convertida para timedelta")
        except Exception as e:
            print(f"❌ Erro ao converter coluna 'Tempo Apresentacao': {e}")
            return df
    
    # Normalizar coluna Dia_Semana
    if 'Dia_Semana' not in df.columns:
        df['Dia_Semana'] = df['Checkin'].dt.weekday
        print("⚠️ Coluna 'Dia_Semana' não encontrada - calculando baseado em Checkin")
    
    # Filtrar registros que possuem apresentação
    registros_com_apresentacao = df[pd.notna(df['Tempo Apresentacao']) & (df['Tempo Apresentacao'] > pd.Timedelta(0)) & pd.notna(df['Checkin'])]
    print(f"📊 Total de registros com apresentação: {len(registros_com_apresentacao)}")
    
    if len(registros_com_apresentacao) == 0:
        print("⚠️ Nenhum registro com apresentação encontrado")
        return df
    
    # DEBUG: Mostrar os primeiros registros para análise
    print("\n🔍 DEBUG - Primeiros registros com apresentação:")
    for i, (index, row) in enumerate(registros_com_apresentacao.head(3).iterrows()):
        checkin_str = row['Checkin'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['Checkin']) else 'N/A'
        print(f"   Registro {i+1}:")
        print(f"      Index: {index}")
        print(f"      Activity: {row.get('Activity', 'N/A')}")
        print(f"      Checkin: {checkin_str}")
        print(f"      Hora: {row['Checkin'].hour if pd.notna(row['Checkin']) else 'N/A'}h:{row['Checkin'].minute if pd.notna(row['Checkin']) else 'N/A'}min")
        print(f"      Tempo Apresentacao: {row['Tempo Apresentacao']}")
        print(f"      Dia_Semana: {row.get('Dia_Semana', 'N/A')}")
    
    contador = 0
    contadores_categoria = {
        'Diurno': 0,
        'Noturno': 0,
        'Especial_Noturno': 0,
        'Especial_Diurno': 0
    }
    
    print(f"\n🔄 Processando {len(registros_com_apresentacao)} registros de apresentação...")
    tempo_inicio_apresentacao = time.time()
    contador_apresentacao = 0
    
    for index, row in tqdm(registros_com_apresentacao.iterrows(), total=len(registros_com_apresentacao), desc="Apresentação"):
        contador_apresentacao += 1
        if contador_apresentacao % 500 == 0:
            progresso_calculo("Processamento de Apresentação", contador_apresentacao, len(registros_com_apresentacao), tempo_inicio_apresentacao)
        tempo_apresentacao = row['Tempo Apresentacao']
        
        if pd.notna(tempo_apresentacao) and tempo_apresentacao > pd.Timedelta(0) and pd.notna(row['Checkin']):
            # Extrair hora e minuto do checkin
            hora_checkin = row['Checkin'].hour
            minuto_checkin = row['Checkin'].minute
            dia_semana = row.get('Dia_Semana', 0)
            
            # Garantir que Dia_Semana seja numérico
            try:
                dia_semana = int(dia_semana) if not pd.isna(dia_semana) else 0
            except (ValueError, TypeError):
                dia_semana = 0
            
            # Verificar se Checkin == Start para aplicar regras especiais
            checkin_igual_start = pd.notna(row['Start']) and row['Checkin'] == row['Start']
            
            # DEBUG: Para os primeiros 5 registros, mostrar classificação detalhada
            if contador < 5:
                print(f"\n🔍 DEBUG Registro {contador + 1} (Index {index}):")
                print(f"   Hora checkin: {hora_checkin}h:{minuto_checkin:02d}min")
                print(f"   Dia_Semana: {dia_semana}")
                print(f"   Tempo apresentação: {tempo_apresentacao}")
                print(f"   Checkin == Start: {checkin_igual_start}")
            
            # Zerar todas as colunas de apresentação para este registro
            df.at[index, 'Tempo Apresentacao Diurno'] = pd.Timedelta('0 days 00:00:00')
            df.at[index, 'Tempo Apresentacao Noturno'] = pd.Timedelta('0 days 00:00:00')
            df.at[index, 'Tempo Apresentacao Especial Noturno'] = pd.Timedelta('0 days 00:00:00')
            df.at[index, 'Tempo Apresentacao Especial Diurno'] = pd.Timedelta('0 days 00:00:00')
            
            # Aplicar regras especiais quando Checkin == Start
            if checkin_igual_start:
                # Regra Especial 1: Dia_Semana ≠ 6 e Checkin entre 06:01-17:59 → Tempo Apresentacao Diurno
                if dia_semana != 6 and ((hora_checkin > 6) or (hora_checkin == 6 and minuto_checkin >= 1)) and hora_checkin < 18:
                    df.at[index, 'Tempo Apresentacao Diurno'] = tempo_apresentacao
                    contadores_categoria['Diurno'] += 1
                    if contador < 5:
                        print("   🎯 Regra Especial 1: Diurno (Dia≠6, 06:01-17:59)")
                
                # Regra Especial 2: Dia_Semana ≠ 5 e Checkin ≥ 18:00 → Tempo Apresentacao Noturno
                elif dia_semana != 5 and hora_checkin >= 18:
                    df.at[index, 'Tempo Apresentacao Noturno'] = tempo_apresentacao
                    contadores_categoria['Noturno'] += 1
                    if contador < 5:
                        print("   🎯 Regra Especial 2: Noturno (Dia≠5, ≥18:00)")
                
                # Regra Especial 3: Dia_Semana = 5 e Checkin ≥ 18:00 → Tempo Apresentacao Especial Noturno
                elif dia_semana == 5 and hora_checkin >= 18:
                    df.at[index, 'Tempo Apresentacao Especial Noturno'] = tempo_apresentacao
                    contadores_categoria['Especial_Noturno'] += 1
                    if contador < 5:
                        print("   🎯 Regra Especial 3: Especial Noturno (Dia=5, ≥18:00)")
                
                # Regra Especial 4: Dia_Semana = 6 e Checkin ≥ 06:01 → Tempo Apresentacao Especial Diurno
                elif dia_semana == 6 and ((hora_checkin > 6) or (hora_checkin == 6 and minuto_checkin >= 1)):
                    df.at[index, 'Tempo Apresentacao Especial Diurno'] = tempo_apresentacao
                    contadores_categoria['Especial_Diurno'] = contadores_categoria.get('Especial_Diurno', 0) + 1
                    if contador < 5:
                        print("   🎯 Regra Especial 4: Especial Diurno (Dia=6, ≥06:01)")
                
                # Caso especial adicional: Domingo 00:00-06:00 → Tempo Apresentacao Especial Noturno
                elif dia_semana == 6 and hora_checkin <= 6:
                    df.at[index, 'Tempo Apresentacao Especial Noturno'] = tempo_apresentacao
                    contadores_categoria['Especial_Noturno'] += 1
                    if contador < 5:
                        print("   🎯 Regra Especial: Especial Noturno (Domingo 00:00-06:00)")
                
                # Fallback para casos não cobertos pelas regras especiais
                else:
                    df.at[index, 'Tempo Apresentacao Diurno'] = tempo_apresentacao
                    contadores_categoria['Diurno'] += 1
                    if contador < 5:
                        print("   🎯 Regra Especial Fallback: Diurno")
            
            else:
                # Aplicar regras gerais quando Checkin ≠ Start
                classificado = False
                
                # Regra Geral CORRIGIDA: Domingo deve respeitar horários
                if dia_semana == 6:
                    # Domingo diurno (06:01-17:59) → Especial Diurno
                    if ((hora_checkin > 6) or (hora_checkin == 6 and minuto_checkin >= 1)) and hora_checkin < 18:
                        df.at[index, 'Tempo Apresentacao Especial Diurno'] = tempo_apresentacao
                        contadores_categoria['Especial_Diurno'] = contadores_categoria.get('Especial_Diurno', 0) + 1
                        classificado = True
                        if contador < 5:
                            print("   🎯 Regra Geral CORRIGIDA: Especial Diurno (domingo 06:01-17:59)")
                    # Domingo noturno (18:00-06:00) → Especial Noturno
                    else:
                        df.at[index, 'Tempo Apresentacao Especial Noturno'] = tempo_apresentacao
                        contadores_categoria['Especial_Noturno'] += 1
                        classificado = True
                        if contador < 5:
                            print("   🎯 Regra Geral CORRIGIDA: Especial Noturno (domingo 18:00-06:00)")
                
                # Regra Geral 2: Se Dia_Semana = 5 (sábado) e Checkin ≥ 18:00 → Tempo Apresentacao Especial Noturno
                elif dia_semana == 5 and hora_checkin >= 18:
                    df.at[index, 'Tempo Apresentacao Especial Noturno'] = tempo_apresentacao
                    contadores_categoria['Especial_Noturno'] += 1
                    classificado = True
                    if contador < 5:
                        print("   🎯 Regra Geral: Especial Noturno (sábado ≥18h)")
                
                # Regra Geral 3: Checkin entre 06:01 e 17:59 → Tempo Apresentacao Diurno
                elif (hora_checkin > 6) or (hora_checkin == 6 and minuto_checkin >= 1):
                    if hora_checkin < 18:  # Entre 06:01-17:59
                        df.at[index, 'Tempo Apresentacao Diurno'] = tempo_apresentacao
                        contadores_categoria['Diurno'] += 1
                        classificado = True
                        if contador < 5:
                            print("   🎯 Regra Geral: Diurno (06:01-17:59)")
                
                # Regra Geral 4: Checkin entre 18:00 e 06:00 → Tempo Apresentacao Noturno (se não foi classificado)
                if not classificado:
                    if hora_checkin >= 18 or hora_checkin <= 6:
                        df.at[index, 'Tempo Apresentacao Noturno'] = tempo_apresentacao
                        contadores_categoria['Noturno'] += 1
                        if contador < 5:
                            print("   🎯 Regra Geral: Noturno (18:00-06:00)")
                    else:
                        # Caso não se encaixe em nenhuma regra (fallback para diurno)
                        df.at[index, 'Tempo Apresentacao Diurno'] = tempo_apresentacao
                        contadores_categoria['Diurno'] += 1
                        if contador < 5:
                            print("   🎯 Regra Geral Fallback: Diurno")
            
            # Verificar véspera de feriado após 21h
            # Se apresentação após 21h em véspera de feriado, também alocar em Especial Noturno
            vespera_feriado = verificar_vespera_feriado(row['Checkin'], feriados)
            if vespera_feriado and hora_checkin >= 21:
                # Se já tem tempo noturno normal, também colocar em especial noturno (ADICIONAL)
                if df.at[index, 'Tempo Apresentacao Noturno'] > pd.Timedelta(0):
                    df.at[index, 'Tempo Apresentacao Especial Noturno'] = tempo_apresentacao
                    contadores_categoria['Especial_Noturno'] += 1
                # Se era classificado como diurno mas é após 21h em véspera, mover para noturno + especial noturno
                elif df.at[index, 'Tempo Apresentacao Diurno'] > pd.Timedelta(0) and hora_checkin >= 21:
                    df.at[index, 'Tempo Apresentacao Diurno'] = pd.Timedelta('0 days 00:00:00')
                    df.at[index, 'Tempo Apresentacao Noturno'] = tempo_apresentacao
                    df.at[index, 'Tempo Apresentacao Especial Noturno'] = tempo_apresentacao
                    contadores_categoria['Diurno'] -= 1
                    contadores_categoria['Noturno'] += 1
                    contadores_categoria['Especial_Noturno'] += 1
                    if contador < 5:
                        print("   🎯 Regra Véspera Feriado: Movido para Noturno + Especial Noturno (≥21h véspera)")

            # Verificar dia de feriado
            dia_feriado = verificar_dia_feriado(row, feriados)
            if dia_feriado:
                # Se foi classificado como noturno, ADICIONAR especial noturno (mantém o noturno base)
                if df.at[index, 'Tempo Apresentacao Noturno'] > pd.Timedelta(0):
                    df.at[index, 'Tempo Apresentacao Especial Noturno'] = tempo_apresentacao
                    contadores_categoria['Especial_Noturno'] += 1
                    if contador < 5:
                        print("   🎯 Regra Feriado: Noturno + Especial Noturno ADICIONAL (feriado)")
                # Se foi classificado como diurno, ADICIONAR especial diurno (mantém o diurno base)
                elif df.at[index, 'Tempo Apresentacao Diurno'] > pd.Timedelta(0):
                    df.at[index, 'Tempo Apresentacao Especial Diurno'] = tempo_apresentacao
                    contadores_categoria['Especial_Diurno'] = contadores_categoria.get('Especial_Diurno', 0) + 1
                    if contador < 5:
                        print("   🎯 Regra Feriado: Diurno + Especial Diurno ADICIONAL (feriado)")
    
            contador += 1
    
    print(f"\n✅ {contador} registros de apresentação processados")
    
    # Mostrar contadores por categoria
    print("\n📊 RESUMO POR CATEGORIA:")
    print(f"   Diurno: {contadores_categoria['Diurno']} registros")
    print(f"   Noturno: {contadores_categoria['Noturno']} registros")
    print(f"   Especial Noturno: {contadores_categoria['Especial_Noturno']} registros")
    print(f"   Especial Diurno: {contadores_categoria['Especial_Diurno']} registros")
    
    # Mostrar totais de tempo por categoria
    print("\n⏱️ TOTAIS DE TEMPO:")
    categorias_apresentacao = {
        'Tempo Apresentacao Diurno': df['Tempo Apresentacao Diurno'].sum(),
        'Tempo Apresentacao Noturno': df['Tempo Apresentacao Noturno'].sum(),
        'Tempo Apresentacao Especial Noturno': df['Tempo Apresentacao Especial Noturno'].sum(),
        'Tempo Apresentacao Especial Diurno': df['Tempo Apresentacao Especial Diurno'].sum()
    }
    
    for categoria, total_tempo in categorias_apresentacao.items():
        if total_tempo > pd.Timedelta(0):
            # Conversão robusta para timedelta antes da comparação
            try:
                coluna_categoria = pd.to_timedelta(df[categoria], errors='coerce')
                registros_count = (coluna_categoria > pd.Timedelta(0)).sum()
            except Exception:
                registros_count = 0
            print(f"   {categoria}: {registros_count} registros ({total_tempo})")
    
    # ========================================================================
    # REPLICAÇÃO DE VALORES ESPECIAIS PARA COLUNAS NORMAIS (APRESENTAÇÃO)
    # ========================================================================
    print("\n🔄 Aplicando replicação de valores especiais para colunas normais (Apresentação)...")
    
    # Contadores para controle de replicação
    replicacoes_apresentacao = {
        'especial_diurno_para_diurno': 0,
        'especial_noturno_para_noturno': 0
    }
    
    # Replicar valores de "Tempo Apresentacao Especial Diurno" para "Tempo Apresentacao Diurno"
    mask_especial_diurno_apres = df['Tempo Apresentacao Especial Diurno'] > pd.Timedelta(0)
    if mask_especial_diurno_apres.any():
        for index in df[mask_especial_diurno_apres].index:
            valor_especial = df.at[index, 'Tempo Apresentacao Especial Diurno']
            df.at[index, 'Tempo Apresentacao Diurno'] = valor_especial
            replicacoes_apresentacao['especial_diurno_para_diurno'] += 1

    # Replicar valores de "Tempo Apresentacao Especial Noturno" para "Tempo Apresentacao Noturno"
    mask_especial_noturno_apres = df['Tempo Apresentacao Especial Noturno'] > pd.Timedelta(0)
    if mask_especial_noturno_apres.any():
        for index in df[mask_especial_noturno_apres].index:
            valor_especial = df.at[index, 'Tempo Apresentacao Especial Noturno']
            df.at[index, 'Tempo Apresentacao Noturno'] = valor_especial
            replicacoes_apresentacao['especial_noturno_para_noturno'] += 1
    
    # Relatório de replicação
    total_replicacoes_apres = sum(replicacoes_apresentacao.values())
    if total_replicacoes_apres > 0:
        print(f"✅ {total_replicacoes_apres} valores de apresentação replicados:")
        if replicacoes_apresentacao['especial_diurno_para_diurno'] > 0:
            print(f"   📊 Especial Diurno → Diurno: {replicacoes_apresentacao['especial_diurno_para_diurno']} registros")
        if replicacoes_apresentacao['especial_noturno_para_noturno'] > 0:
            print(f"   📊 Especial Noturno → Noturno: {replicacoes_apresentacao['especial_noturno_para_noturno']} registros")
    else:
        print("ℹ️ Nenhum valor especial de apresentação encontrado para replicação")
    
    # Recalcular totais após replicação para validação
    print("\n⏱️ TOTAIS FINAIS APÓS REPLICAÇÃO (APRESENTAÇÃO):")
    categorias_finais_apres = {
        'Tempo Apresentacao Diurno': df['Tempo Apresentacao Diurno'][df['Tempo Apresentacao Diurno'] > pd.Timedelta(0)].sum(),
        'Tempo Apresentacao Noturno': df['Tempo Apresentacao Noturno'][df['Tempo Apresentacao Noturno'] > pd.Timedelta(0)].sum(),
        'Tempo Apresentacao Especial Diurno': df['Tempo Apresentacao Especial Diurno'][df['Tempo Apresentacao Especial Diurno'] > pd.Timedelta(0)].sum(),
        'Tempo Apresentacao Especial Noturno': df['Tempo Apresentacao Especial Noturno'][df['Tempo Apresentacao Especial Noturno'] > pd.Timedelta(0)].sum()
    }
    
    for categoria, total_tempo in categorias_finais_apres.items():
        if total_tempo > pd.Timedelta(0):
            try:
                coluna_categoria = pd.to_timedelta(df[categoria], errors='coerce')
                registros_count = (coluna_categoria > pd.Timedelta(0)).sum()
            except Exception:
                registros_count = 0
            print(f"   {categoria}: {registros_count} registros ({total_tempo})")
    
    # ========================================================================
    # REPLICAÇÃO DE VALORES ESPECIAIS PARA COLUNAS NORMAIS (APRESENTAÇÃO) - FIM
    # ========================================================================
    
    # ========================================================================
    # REPLICAÇÃO DE VALORES ESPECIAIS PARA COLUNAS NORMAIS (APRESENTAÇÃO) - INÍCIO
    # ========================================================================
    print("\n🔄 Aplicando replicação de valores especiais para colunas normais (Apresentação) - INÍCIO...")
    
    # Contadores para controle de replicação
    replicacoes_apresentacao_inicio = {
        'especial_diurno_para_diurno': 0,
        'especial_noturno_para_noturno': 0
    }
    
    # Replicar valores de "Tempo Apresentacao Especial Diurno" para "Tempo Apresentacao Diurno"
    mask_especial_diurno_apres_inicio = df['Tempo Apresentacao Especial Diurno'] > pd.Timedelta(0)
    if mask_especial_diurno_apres_inicio.any():
        for index in df[mask_especial_diurno_apres_inicio].index:
            valor_especial = df.at[index, 'Tempo Apresentacao Especial Diurno']
            df.at[index, 'Tempo Apresentacao Diurno'] = valor_especial
            replicacoes_apresentacao_inicio['especial_diurno_para_diurno'] += 1
    
    # Replicar valores de "Tempo Apresentacao Especial Noturno" para "Tempo Apresentacao Noturno"
    mask_especial_noturno_apres_inicio = df['Tempo Apresentacao Especial Noturno'] > pd.Timedelta(0)
    if mask_especial_noturno_apres_inicio.any():
        for index in df[mask_especial_noturno_apres_inicio].index:
            valor_especial = df.at[index, 'Tempo Apresentacao Especial Noturno']
            df.at[index, 'Tempo Apresentacao Noturno'] = valor_especial
            replicacoes_apresentacao_inicio['especial_noturno_para_noturno'] += 1
    
    # Relatório de replicação
    total_replicacoes_apres_inicio = sum(replicacoes_apresentacao_inicio.values())
    if total_replicacoes_apres_inicio > 0:
        print(f"✅ {total_replicacoes_apres_inicio} valores de apresentação replicados (INÍCIO):")
        if replicacoes_apresentacao_inicio['especial_diurno_para_diurno'] > 0:
            print(f"   📊 Especial Diurno → Diurno: {replicacoes_apresentacao_inicio['especial_diurno_para_diurno']} registros")
        if replicacoes_apresentacao_inicio['especial_noturno_para_noturno'] > 0:
            print(f"   📊 Especial Noturno → Noturno: {replicacoes_apresentacao_inicio['especial_noturno_para_noturno']} registros")
    else:
        print("ℹ️ Nenhum valor especial de apresentação encontrado para replicação (INÍCIO)")
    
    # Recalcular totais após replicacao para validação
    print("\n⏱️ TOTAIS FINAIS APÓS REPLICAÇÃO (APRESENTAÇÃO) - INÍCIO:")
    categorias_finais_apres_inicio = {
        'Tempo Apresentacao Diurno': df['Tempo Apresentacao Diurno'][df['Tempo Apresentacao Diurno'] > pd.Timedelta(0)].sum(),
        'Tempo Apresentacao Noturno': df['Tempo Apresentacao Noturno'][df['Tempo Apresentacao Noturno'] > pd.Timedelta(0)].sum(),
        'Tempo Apresentacao Especial Diurno': df['Tempo Apresentacao Especial Diurno'][df['Tempo Apresentacao Especial Diurno'] > pd.Timedelta(0)].sum(),
        'Tempo Apresentacao Especial Noturno': df['Tempo Apresentacao Especial Noturno'][df['Tempo Apresentacao Especial Noturno'] > pd.Timedelta(0)].sum()
    }
    
    for categoria, total_tempo in categorias_finais_apres_inicio.items():
        if total_tempo > pd.Timedelta(0):
            try:
                coluna_categoria = pd.to_timedelta(df[categoria], errors='coerce')
                registros_count = (coluna_categoria > pd.Timedelta(0)).sum()
            except Exception:
                registros_count = 0
            print(f"   {categoria}: {registros_count} registros ({total_tempo})")
    
    # ========================================================================
    # REPLICAÇÃO DE VALORES ESPECIAIS PARA COLUNAS NORMAIS (APRESENTAÇÃO) - FIM
    # ========================================================================
    
    return df

# =============================================================================
# 5.5. FUNÇÕES AUXILIARES DE LOG E DIAGNÓSTICO
# =============================================================================

def criar_log_execucao():
    """
    Cria arquivo de log da execução
    
    Returns:
        str: Nome do arquivo de log
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_log = f"log_calculos_{timestamp}.txt"
    
    try:
        with open(nome_log, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("    SISTEMA DE CÁLCULOS FINAIS - AERONAUTAS AZUL\n")
            f.write("=" * 80 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo de Log: {nome_log}\n")
            f.write("=" * 80 + "\n\n")
        
        print(f"📋 Log criado: {nome_log}")
        return nome_log
        
    except Exception as e:
        print(f"⚠️ Erro ao criar log: {e}")
        return None

def log_status(mensagem, arquivo_log):
    """
    Registra status no arquivo de log
    
    Args:
        mensagem (str): Mensagem a ser registrada
        arquivo_log (str): Nome do arquivo de log
    """
    if arquivo_log:
        try:
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            with open(arquivo_log, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {mensagem}\n")
        except Exception as e:
            print(f"⚠️ Erro ao escrever no log: {e}")

def log_diagnostico(etapa, descricao, df):
    """
    Registra informações de diagnóstico
    
    Args:
        etapa (str): Nome da etapa
        descricao (str): Descrição da etapa
        df (pandas.DataFrame): DataFrame para diagnóstico
    """
    try:
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"📊 [{timestamp}] {etapa}: {descricao}")
        print(f"   - Registros: {len(df)}")
        print(f"   - Colunas: {len(df.columns)}")
        
        # Verificar colunas de tempo
        colunas_tempo = [col for col in df.columns if 'Tempo' in col]
        if colunas_tempo:
            print(f"   - Colunas de tempo: {len(colunas_tempo)}")
            
    except Exception as e:
        print(f"⚠️ Erro no diagnóstico: {e}")

def progresso_calculo(nome_etapa, atual, total, tempo_inicio):
    """
    Mostra progresso do cálculo atual
    
    Args:
        nome_etapa (str): Nome da etapa
        atual (int): Registro atual
        total (int): Total de registros
        tempo_inicio (float): Tempo de início
    """
    try:
        tempo_atual = time.time()
        tempo_decorrido = tempo_atual - tempo_inicio
        
        if tempo_decorrido > 0:
            registros_por_segundo = atual / tempo_decorrido
            tempo_estimado = (total - atual) / registros_por_segundo if registros_por_segundo > 0 else 0
            
            porcentagem = (atual / total) * 100
            
            print(f"📊 {nome_etapa}: {atual}/{total} ({porcentagem:.1f}%) - "
                  f"Velocidade: {registros_por_segundo:.1f} reg/s - "
                  f"Tempo estimado: {tempo_estimado:.0f}s")
                  
    except Exception as e:
        print(f"⚠️ Erro no progresso: {e}")

def padronizar_colunas_timedelta(df):
    """
    Padroniza colunas timedelta para formato consistente
    
    Args:
        df (pandas.DataFrame): DataFrame com colunas timedelta
        
    Returns:
        pandas.DataFrame: DataFrame padronizado
    """
    print("🔧 Padronizando colunas timedelta...")
    
    # Identificar colunas de tempo (exceto 'Tempo Solo' que deve ser preservada)
    colunas_tempo = [col for col in df.columns if 'Tempo' in col and col != 'Tempo Solo']
    
    colunas_padronizadas = 0
    for coluna in colunas_tempo:
        if coluna in df.columns:
            try:
                # Converter para timedelta se necessário
                if not pd.api.types.is_timedelta64_dtype(df[coluna]):
                    df[coluna] = pd.to_timedelta(df[coluna], errors='coerce')
                
                # Preencher NaT com zero
                df[coluna] = df[coluna].fillna(pd.Timedelta(0))
                
                colunas_padronizadas += 1
                
            except Exception as e:
                print(f"⚠️ Erro ao padronizar {coluna}: {e}")
    
    print(f"✅ {colunas_padronizadas} colunas timedelta padronizadas")
    return df

# =============================================================================
# 7. FUNÇÃO DE GRAVAÇÃO
# =============================================================================

def gravar_arquivo_final(df, nome_arquivo_original, diretorio):
    """
    Grava o arquivo final com todos os cálculos E pós-processamento para garantir formatação correta
    
    Args:
        df (pandas.DataFrame): DataFrame final
        nome_arquivo_original (str): Nome do arquivo original
        diretorio (str): Diretório de saída
    """
    print("\n💾 GRAVAÇÃO DO ARQUIVO FINAL COM PÓS-PROCESSAMENTO")
    print("=" * 60)
    
    # ETAPA 1: Padronizar formato das colunas antes da gravação
    print("🔧 ETAPA 1: Padronização pré-gravação...")
    df = padronizar_colunas_timedelta(df)
    
    # Gerar nome do arquivo final
    nome_base = os.path.splitext(os.path.basename(nome_arquivo_original))[0]
    
    if ")" in nome_base:
        novo_nome = nome_base.split(")")[0] + ") - CALCULOS_FINAIS_COMPLETOS.csv"
    else:
        novo_nome = nome_base + " - CALCULOS_FINAIS_COMPLETOS.csv"
    
    caminho_completo = os.path.join(diretorio, novo_nome)
    
    try:
        # ETAPA 2: Gravação inicial
        print("💾 ETAPA 2: Gravando arquivo CSV...")
        df.to_csv(
            caminho_completo,
            index=False,
            sep=',',
            encoding='utf-8-sig',
            date_format='%d/%m/%Y %H:%M',
            float_format='%.2f'
        )
        
        if not os.path.exists(caminho_completo):
            print("❌ Erro: Arquivo não foi criado!")
            return False
        
        tamanho_inicial = os.path.getsize(caminho_completo)
        print(f"✅ Arquivo gravado: {tamanho_inicial:,} bytes")
        
        # ETAPA 3: PÓS-PROCESSAMENTO DO ARQUIVO CSV
        print("🔧 ETAPA 3: Pós-processamento do arquivo CSV...")
        
        try:
            # Re-ler o arquivo para verificar e corrigir problemas de formatação
            df_verificacao = pd.read_csv(caminho_completo)
            print(f"📊 Arquivo re-carregado: {len(df_verificacao):,} linhas")
            
            # Identificar colunas de tempo no arquivo final
            colunas_tempo_arquivo = [col for col in df_verificacao.columns if 'Tempo' in col and col != 'Tempo Solo']
            print(f"📋 Colunas de tempo no arquivo: {len(colunas_tempo_arquivo)}")
            
            correcoes_pos_gravacao = 0
            colunas_corrigidas = []
            
            # Verificar e corrigir cada coluna de tempo
            for coluna in colunas_tempo_arquivo:
                if coluna in df_verificacao.columns:
                    # Converter para string para verificar formatação
                    valores_str = df_verificacao[coluna].astype(str).str.strip()
                    
                    # Contar problemas
                    problemas = (valores_str == '0 days').sum()
                    
                    if problemas > 0:
                        print(f"   🚨 {coluna}: {problemas} valores '0 days' detectados")
                        
                        # Corrigir diretamente no DataFrame
                        mask_problemas = (valores_str == '0 days')
                        df_verificacao.loc[mask_problemas, coluna] = '0 days 00:00:00'
                        correcoes_pos_gravacao += problemas
                        colunas_corrigidas.append(coluna)
                        print(f"   ✅ {coluna}: {problemas} valores corrigidos")
                    else:
                        print(f"   ✅ {coluna}: OK")
            
            # ETAPA 4: Re-gravar arquivo se houve correções
            if correcoes_pos_gravacao > 0:
                print(f"\n� ETAPA 4: Re-gravando arquivo com {correcoes_pos_gravacao} correções...")
                
                # Backup do arquivo original
                import shutil
                backup_path = caminho_completo.replace('.csv', '_BACKUP_PRE_CORRECAO.csv')
                shutil.copy2(caminho_completo, backup_path)
                print(f"📋 Backup criado: {os.path.basename(backup_path)}")
                
                # Re-gravar arquivo corrigido
                df_verificacao.to_csv(
                    caminho_completo,
                    index=False,
                    sep=',',
                    encoding='utf-8-sig',
                    date_format='%d/%m/%Y %H:%M',
                    float_format='%.2f'
                )
                
                tamanho_final = os.path.getsize(caminho_completo)
                print(f"✅ Arquivo re-gravado: {tamanho_final:,} bytes")
                
                # ETAPA 5: Verificação final absoluta
                print("� ETAPA 5: Verificação final...")
                df_final = pd.read_csv(caminho_completo)
                
                problemas_finais_total = 0
                for coluna in colunas_tempo_arquivo:
                    if coluna in df_final.columns:
                        valores_finais = df_final[coluna].astype(str).str.strip()
                        problemas_finais = (valores_finais == '0 days').sum()
                        problemas_finais_total += problemas_finais
                        
                        if problemas_finais > 0:
                            print(f"   ❌ {coluna}: {problemas_finais} problemas AINDA RESTANTES")
                        else:
                            print(f"   ✅ {coluna}: TOTALMENTE CORRIGIDA")
                
                if problemas_finais_total == 0:
                    print("   🎉 SUCESSO: Todos os problemas resolvidos!")
                else:
                    print(f"   ⚠️ ATENÇÃO: {problemas_finais_total} problemas ainda persistem")
                
            else:
                print("✅ ETAPA 4: Nenhuma correção pós-grav ação necessária")
                
        except Exception as e:
            print(f"⚠️ Erro durante pós-processamento: {e}")
            print("📋 Arquivo principal foi gravado, mas pós-processamento falhou")
        
        # Relatório final
        tamanho_final = os.path.getsize(caminho_completo)
        print(f"\n📊 RELATÓRIO FINAL:")
        print(f"   📁 Arquivo: {os.path.basename(caminho_completo)}")
        print(f"   📊 Tamanho final: {tamanho_final:,} bytes")
        print(f"   📍 Local: {caminho_completo}")
        
        if 'correcoes_pos_gravacao' in locals() and correcoes_pos_gravacao > 0:
            print(f"   🔧 Correções pós-grav ação: {correcoes_pos_gravacao}")
            print(f"   📋 Colunas corrigidas: {len(colunas_corrigidas)}")
        
        print("=" * 60)
        return True
            
    except Exception as e:
        print(f"❌ Erro ao gravar arquivo: {e}")
        return False

# =============================================================================
# 8. FUNÇÃO PRINCIPAL DE EXECUÇÃO
# =============================================================================

def executar_calculos_completos():
    """
    Função principal que executa todo o processo de cálculos
    """
    print("🚀 SISTEMA DE CÁLCULOS FINAIS - AERONAUTAS AZUL")
    print("=" * 70)
    print("⚡ Iniciando processamento completo...")
    print("🚨🚨🚨 TESTE: INÍCIO DA FUNÇÃO executar_calculos_completos 🚨🚨🚨")
    
    # Inicia sistema de monitoramento
    monitor.iniciar_monitoramento()
    monitor.atualizar_status("Iniciando sistema", 0)
    
    inicio_execucao = datetime.now()
    # 1. Configurar interface
    monitor.atualizar_status("Configurando interface", 5)
    log_file = criar_log_execucao()
    log_status("Configurando interface de usuário...", log_file)
    root = configurar_interface()
    
    # 2. Selecionar e carregar arquivo principal
    monitor.atualizar_status("Selecionando arquivo principal", 10)
    log_status("Selecionando arquivo principal...", log_file)
    diretorio, nome_arquivo = selecionar_arquivo(root)
    
    monitor.atualizar_status("Carregando dados principais", 15)
    log_status("Carregando dados principais...", log_file)
    caminho_completo = os.path.join(diretorio, nome_arquivo)
    df_dados, nome_aeronauta = carregar_dados_principais(caminho_completo)
    
    # 3. Carregar dados auxiliares
    print("\n📋 CARREGAMENTO DE DADOS AUXILIARES")
    print("=" * 50)
    
    monitor.atualizar_status("Carregando feriados", 20)
    log_status("Carregando lista de feriados...", log_file)
    feriados = carregar_feriados()
    
    monitor.atualizar_status("Carregando siglas", 30)
    log_status("Carregando tipos de reserva...", log_file)
    lista_reservas, lista_plantoes, lista_treinamentos, lista_tipos_voo = carregar_siglas_sabre()
    
    # 4. Preparar DataFrame
    monitor.atualizar_status("Preparando estrutura de dados", 35)
    log_status("Preparando estrutura do DataFrame...", log_file)
    log_diagnostico("INICIO_PREPARACAO", "Antes de preparar DataFrame", df_dados)
    df_dados = preparar_dataframe(df_dados, feriados)
    log_diagnostico("APOS_PREPARACAO", "Após preparar DataFrame", df_dados)
    df_dados = criar_colunas_calculo(df_dados)
    log_diagnostico("APOS_CRIAR_COLUNAS", "Após criar colunas de cálculo", df_dados)
    
    # 5. Executar todos os cálculos
    print("\n🔄 EXECUÇÃO DOS CÁLCULOS")
    print("=" * 50)
    
    etapas = [
        ("Cálculo de Tempos de Apresentação", 40, 45),
        ("Cálculo de Tempos de Jornada", 45, 50),
        ("Cálculo de Tempos Após Corte", 50, 55),
        ("Cálculo de Tempos de Repouso", 55, 65),
        ("Cálculo de Tempos de Repouso Extra", 65, 70),
        ("Cálculo de Tempos de Reserva", 70, 75),
        ("Cálculo de Tempos de Plantão", 75, 80),
        ("Cálculo de Tempos de Treinamento", 80, 85),
        ("Cálculo de Tempos em Solo", 85, 100)
    ]
    
    print("🚨🚨🚨 INICIANDO LOOP DE ETAPAS 🚨🚨🚨")
    print(f"Total de etapas: {len(etapas)}")
    for i, (etapa_nome, prog_inicio, prog_fim) in enumerate(etapas):
        print(f"Etapa {i+1}: {etapa_nome}")
    print("🚨🚨🚨 INICIANDO EXECUÇÃO 🚨🚨🚨")
    
    for etapa_nome, prog_inicio, prog_fim in etapas:
        monitor.atualizar_status(etapa_nome, prog_inicio)
        log_status(f"Iniciando {etapa_nome.lower()}...", log_file)
        
        # DEBUG: Verificar qual etapa está sendo executada
        print(f"🔍 DEBUG LOOP: Executando etapa '{etapa_nome}'")
        
        if "Apresentação" in etapa_nome:
            df_dados = calcular_tempos_apresentacao(df_dados, feriados)
        elif "Jornada" in etapa_nome:
            df_dados = calcular_tempos_jornada(df_dados, feriados)
        elif "Após Corte" in etapa_nome:
            print(f"🚨 DEBUG: CONDIÇÃO 'Após Corte' ATIVADA para '{etapa_nome}'")
            log_diagnostico("PRE_APOS_CORTE", "Antes do cálculo após corte", df_dados)
            df_dados = calcular_tempos_apos_corte(df_dados, feriados, lista_tipos_voo)
            log_diagnostico("POS_APOS_CORTE", "Após o cálculo após corte", df_dados)
        elif "Repouso Extra" in etapa_nome:
            df_dados = calcular_tempos_repouso_extra(df_dados, feriados)
        elif "Repouso" in etapa_nome and "Extra" not in etapa_nome:
            df_dados = calcular_tempos_repouso(df_dados, feriados)
        elif "Reserva" in etapa_nome:
            df_dados = calcular_tempos_reserva(df_dados, lista_reservas)
        elif "Plantão" in etapa_nome:
            df_dados = calcular_tempos_plantao(df_dados, lista_plantoes)
        elif "Treinamento" in etapa_nome:
            df_dados = calcular_tempos_treinamento(df_dados, lista_treinamentos)
        elif "Solo" in etapa_nome:
            df_dados = calcular_tempos_solo(df_dados, feriados)
            
        monitor.atualizar_status(f"{etapa_nome} - Concluído", prog_fim)
        log_status(f"{etapa_nome} concluído com sucesso!", log_file)
    
    # 5.5. Aplicar replicação de valores especiais
    monitor.atualizar_status("Aplicando replicacao de valores especiais",    92)
   
   
   
    log_status("Aplicando replicacao de valores especiais...", log_file)
    df_dados = aplicar_replicacao_valores_especiais(df_dados)
    
    # 6. Gravar arquivo final
    monitor.atualizar_status("Gravando arquivo final", 95)
    log_status("Gravando arquivo final...", log_file)
    sucesso_gravacao = gravar_arquivo_final(df_dados, nome_arquivo, diretorio)
    
    # 7. Relatório final
    fim_execucao = datetime.now()
    tempo_total = fim_execucao - inicio_execucao
    
    monitor.atualizar_status("Finalizando processamento", 100)
    monitor.finalizar_monitoramento(sucesso=True)
    
    print("\n🎉 EXECUÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    print(f"👤 Aeronauta: {nome_aeronauta}")
    print(f"📊 Registros processados: {len(df_dados):,}")
    print(f"📋 Colunas finais: {len(df_dados.columns)}")
    print(f"⏱️ Tempo total: {tempo_total}")
    print(f"🕐 Finalizado em: {fim_execucao.strftime('%d/%m/%Y %H:%M:%S')}")
    print("📁 Arquivos de monitoramento:")
    print(f"   - Log: {monitor.log_file}")
    print(f"   - Status: {monitor.status_file}")
    print(f"   - PID: {monitor.pid_file}")
    
    log_status("Processamento concluído com sucesso!", log_file)
    
    if sucesso_gravacao:
        messagebox.showinfo(
            "Sucesso", 
            f"Processamento concluído com sucesso!\n\n"
            f"Aeronauta: {nome_aeronauta}\n"
            f"Registros: {len(df_dados):,}\n"
            f"Tempo: {tempo_total}\n\n"
            f"Arquivos de monitoramento salvos:\n"
            f"- {monitor.status_file}\n"
            f"- {monitor.log_file}"
        )
    else:
        messagebox.showwarning(
            "Aviso", 
            "Processamento concluído, mas houve problemas na gravação do arquivo."
        )

# =============================================================================
# BLOCO DE EXECUÇÃO PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    """
    Bloco principal que executa quando o script é chamado diretamente
    """
    try:
        print("🚀 INICIANDO SISTEMA DE CÁLCULOS FINAIS - AERONAUTAS AZUL")
        print("=" * 70)
        
        # Executar função principal
        executar_calculos_completos()
        
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
        try:
            monitor.atualizar_status("Execução interrompida", 0, "CANCELADO")
            monitor.finalizar_monitoramento(sucesso=False, erro="Interrompido pelo usuário")
        except:
            pass
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        
        # Atualizar status de erro
        try:
            monitor.atualizar_status("Erro na execução", 0, "ERRO")
            monitor.finalizar_monitoramento(sucesso=False, erro=str(e))
        except:
            pass
        
        # Criar log de erro detalhado
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            erro_file = f"erro_execucao_{timestamp}.txt"
            with open(erro_file, 'w', encoding='utf-8') as f:
                f.write("ERRO NA EXECUÇÃO DO SISTEMA DE CÁLCULOS\n")
                f.write("=" * 50 + "\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Erro: {str(e)}\n")
                f.write("\nTraceback completo:\n")
                f.write(traceback.format_exc())
            print(f"📋 Log de erro salvo em: {erro_file}")
        except Exception:
            pass
        
        # Mostrar mensagem de erro para o usuário
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Erro na Execução",
                f"Ocorreu um erro durante a execução:\n\n{str(e)}\n\n"
                f"Verifique o arquivo de log para mais detalhes."
            )
            root.destroy()
        except Exception:
            pass
    
    finally:
        # Limpeza final
        try:
            print("\n🔧 Finalizando sistema...")
        except Exception:
            pass

# =============================================================================
# INFORMAÇÕES DO SCRIPT
# =============================================================================

print("📋 Script carregado com sucesso!")
print("🎯 Para executar, rode: python nome_do_arquivo.py")
print("💡 Aguardando execução automática...")