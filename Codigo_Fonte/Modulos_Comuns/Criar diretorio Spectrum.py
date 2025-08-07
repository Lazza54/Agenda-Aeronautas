import os

# Dados base
empresas = ["AZUL", "GOL", "LATAM"]
usuarios_por_empresa = {
    "AZUL": ["Joao_Silva", "Maria_Lima"],
    "GOL": ["Carlos_Sousa", "Ana_Costa"],
    "LATAM": ["Bruno_Ferreira", "Larissa_Alves"]
}

# Diretório principal na unidade RAID G:
base_dir = "G:/SPECTRUM_SYSTEM"

# Diretórios comuns
documentos_comuns = ["Legislacao_Aeronautica", "CLT", "CCT"]
codigo_modulos = ["Modulos_Comuns", "Documentacao_Tecnica"]
logs_sistema = ["Auditorias", "Erros", "Processos"]

def criar_diretorios(caminho):
    os.makedirs(caminho, exist_ok=True)

# Criação base
criar_diretorios(base_dir)

# Documentos Comuns
doc_comuns_path = os.path.join(base_dir, "Documentos_Comuns")
for doc in documentos_comuns:
    criar_diretorios(os.path.join(doc_comuns_path, doc))

# Normas e ACT por empresa
normas_path = os.path.join(doc_comuns_path, "Normas_Empresas")
for empresa in empresas:
    criar_diretorios(os.path.join(normas_path, empresa, "Normas"))
    criar_diretorios(os.path.join(normas_path, empresa, "ACT"))

# Aeronautas
aeronautas_path = os.path.join(base_dir, "Aeronautas")
for empresa in empresas:
    emp_path = os.path.join(aeronautas_path, empresa)
    criar_diretorios(emp_path)
    for usuario in usuarios_por_empresa.get(empresa, []):
        usuario_path = os.path.join(emp_path, usuario)
        criar_diretorios(os.path.join(usuario_path, "Escalas_Planejadas"))
        criar_diretorios(os.path.join(usuario_path, "Escalas_Executadas"))
        criar_diretorios(os.path.join(usuario_path, "Auditoria_Calculos"))

# Código Fonte
codigo_path = os.path.join(base_dir, "Codigo_Fonte")
for modulo in codigo_modulos:
    criar_diretorios(os.path.join(codigo_path, modulo))

# Módulos específicos por empresa
mod_especificos = os.path.join(codigo_path, "Modulos_Especificos")
for empresa in empresas:
    criar_diretorios(os.path.join(mod_especificos, empresa))

# Logs do Sistema
logs_path = os.path.join(base_dir, "Logs_Sistema")
for log in logs_sistema:
    criar_diretorios(os.path.join(logs_path, log))

print("✅ Estrutura criada com sucesso na unidade G:")
print("Verifique a unidade G: para confirmar a criação dos diretórios.")
# Fim do script