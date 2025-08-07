from datetime import datetime, timedelta

def classificar_horas_trabalhadas(checkin, checkout, feriados=None):
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
        feriados (list): Lista de datas de feriados no formato 'YYYY-MM-DD'
    
    Returns:
        dict: Horas classificadas por categoria
    """
    
    # Converter strings para datetime
    dt_checkin = datetime.strptime(checkin, '%Y-%m-%d %H:%M:%S')
    dt_checkout = datetime.strptime(checkout, '%Y-%m-%d %H:%M:%S')
    
    # Lista de feriados (se não fornecida, usar lista vazia)
    if feriados is None:
        feriados = []
    
    # Converter feriados para objetos date
    feriados_dates = [datetime.strptime(f, '%Y-%m-%d').date() for f in feriados]
    
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
    atual = dt_checkin
    
    while atual < dt_checkout:
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
        proximos_marcos.append(dt_checkout)
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
            'inicio': atual.strftime('%Y-%m-%d %H:%M:%S'),
            'fim': proxima.strftime('%Y-%m-%d %H:%M:%S'),
            'duracao': formatar_timedelta(duracao),
            'categoria': categoria,
            'motivo_especial': motivo_especial if is_especial else None
        })
        
        # Avançar para próximo período
        atual = proxima
    
    return resultado

def formatar_timedelta(td):
    """
    Converte timedelta para formato HH:MM
    """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

def exibir_classificacao(resultado):
    """
    Exibe a classificação das horas de forma organizada
    """
    print("=" * 60)
    print("CLASSIFICAÇÃO DE HORAS TRABALHADAS")
    print("=" * 60)
    
    print(f"\n📊 RESUMO POR CATEGORIA:")
    print(f"   Hora Diurna Normal: {formatar_timedelta(resultado['hora_diurna_normal'])}")
    print(f"   Hora Noturna Normal: {formatar_timedelta(resultado['hora_noturna_normal'])}")
    print(f"   Hora Especial Diurna: {formatar_timedelta(resultado['hora_especial_diurna'])}")
    print(f"   Hora Especial Noturna: {formatar_timedelta(resultado['hora_especial_noturna'])}")
    
    total = (resultado['hora_diurna_normal'] + 
             resultado['hora_noturna_normal'] + 
             resultado['hora_especial_diurna'] + 
             resultado['hora_especial_noturna'])
    print(f"   TOTAL: {formatar_timedelta(total)}")

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo com o caso apresentado
    checkin = "2017-11-05 17:16:00"
    checkout = "2017-11-06 07:35:00"
    
    # Lista de feriados (exemplo)
    feriados = ["2017-11-15", "2017-12-25"]
    
    resultado = classificar_horas_trabalhadas(checkin, checkout, feriados)
    exibir_classificacao(resultado)
