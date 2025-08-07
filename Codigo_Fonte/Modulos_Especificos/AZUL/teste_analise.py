import os
import re

arquivo_manual = 'dados_escala_manual.txt'
if os.path.exists(arquivo_manual):
    with open(arquivo_manual, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    print(f'Processando arquivo: {arquivo_manual}')
    print('=== ANÁLISE DOS DADOS ===')
    
    # Procurar padrões
    datas = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b', conteudo)
    horarios = re.findall(r'\b\d{1,2}:\d{2}\b', conteudo)
    aeroportos = re.findall(r'\b[A-Z]{3}\b', conteudo)
    voos = re.findall(r'\bAD\d{3,4}\b', conteudo)
    equipamentos = re.findall(r'\b(A\d{3}|E\d{3})\b', conteudo)
    
    print(f'Datas encontradas: {len(set(datas))} - {list(set(datas))}')
    print(f'Horários encontrados: {len(horarios)} - {horarios[:5]}...')
    print(f'Aeroportos encontrados: {len(set(aeroportos))} - {list(set(aeroportos))}')
    print(f'Voos encontrados: {len(set(voos))} - {list(set(voos))}')
    print(f'Equipamentos encontrados: {len(set(equipamentos))} - {list(set(equipamentos))}')
    
    print('\n=== CONTEÚDO COMPLETO ===')
    print(conteudo)
    
    print('\n✅ Análise concluída!')
else:
    print(f'Arquivo {arquivo_manual} não encontrado.')
