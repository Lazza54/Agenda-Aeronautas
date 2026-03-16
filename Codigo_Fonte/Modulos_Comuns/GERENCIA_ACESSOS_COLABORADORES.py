"""
GERENCIA_ACESSOS_COLABORADORES.py
----------------------------------
Módulo para geração e envio de links com autorização de acesso
a colaboradores do sistema Agenda-Aeronautas.

Funcionalidades:
  - Gerar token seguro para um colaborador
  - Salvar os dados do colaborador no arquivo colaboradores.json
  - Enviar o link por e-mail (via SMTP configurável)
  - Verificar se um token é válido e não expirado
  - Listar colaboradores ativos
  - Revogar acesso de um colaborador
  - Interface gráfica (tkinter) para uso interativo
"""

import json
import os
import secrets
import hashlib
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    import tkinter as tk
    from tkinter import messagebox
    _TKINTER_DISPONIVEL = True
except ModuleNotFoundError:  # pragma: no cover
    _TKINTER_DISPONIVEL = False

# ---------------------------------------------------------------------------
# Caminhos padrão
# ---------------------------------------------------------------------------

# Localiza o diretório de armazenamento de logs/colaboradores a partir deste arquivo
_DIRETORIO_COLABORADORES = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Logs_Sistema", "Processos")
)
ARQUIVO_COLABORADORES = os.path.join(_DIRETORIO_COLABORADORES, "colaboradores.json")

# Níveis de acesso disponíveis
NIVEIS_ACESSO = ["leitura", "escrita", "admin"]

# Validade padrão do link (em dias)
VALIDADE_PADRAO_DIAS = 7


# ---------------------------------------------------------------------------
# Funções internas de persistência
# ---------------------------------------------------------------------------

def _carregar_colaboradores() -> dict:
    """Carrega o arquivo colaboradores.json; retorna dict vazio se não existir."""
    if os.path.exists(ARQUIVO_COLABORADORES):
        with open(ARQUIVO_COLABORADORES, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _salvar_colaboradores(dados: dict) -> None:
    """Persiste o dicionário de colaboradores no arquivo JSON."""
    os.makedirs(os.path.dirname(ARQUIVO_COLABORADORES), exist_ok=True)
    with open(ARQUIVO_COLABORADORES, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


# ---------------------------------------------------------------------------
# Funções principais
# ---------------------------------------------------------------------------

def gerar_token_acesso() -> str:
    """
    Gera um token criptograficamente seguro de 32 bytes (64 caracteres hex).
    Este token é enviado ao colaborador e nunca armazenado em texto claro.
    """
    return secrets.token_hex(32)


def _hash_token(token: str) -> str:
    """Retorna o hash SHA-256 do token para armazenamento seguro."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def criar_link_colaborador(
    email: str,
    nivel_acesso: str = "leitura",
    validade_dias: int = VALIDADE_PADRAO_DIAS,
) -> str:
    """
    Gera um link de acesso com autorização para o colaborador informado.

    Parâmetros
    ----------
    email : str
        E-mail do colaborador que receberá o acesso.
    nivel_acesso : str
        Nível de acesso: 'leitura', 'escrita' ou 'admin'.
    validade_dias : int
        Quantidade de dias até o link expirar (padrão: 7).

    Retorna
    -------
    str
        Link com o token de acesso embutido.
    """
    if nivel_acesso not in NIVEIS_ACESSO:
        raise ValueError(
            f"Nível de acesso inválido: '{nivel_acesso}'. "
            f"Escolha entre: {NIVEIS_ACESSO}"
        )

    token = gerar_token_acesso()
    token_hash = _hash_token(token)
    expiracao = (datetime.now() + timedelta(days=validade_dias)).isoformat()

    colaboradores = _carregar_colaboradores()
    colaboradores[token_hash] = {
        "email": email,
        "nivel_acesso": nivel_acesso,
        "criado_em": datetime.now().isoformat(),
        "expira_em": expiracao,
        "ativo": True,
    }
    _salvar_colaboradores(colaboradores)

    link = f"agenda-aeronautas://acesso?token={token}"
    print(f"✅ Link gerado para {email}: {link}")
    print(f"   Nível de acesso : {nivel_acesso}")
    print(f"   Válido até      : {expiracao}")
    return link


def verificar_token(token: str) -> tuple[bool, dict | None]:
    """
    Verifica se um token de acesso é válido e não expirado.

    Retorna
    -------
    tuple[bool, dict | None]
        (True, dados_do_colaborador) se o token for válido,
        (False, None) caso contrário.
    """
    token_hash = _hash_token(token)
    colaboradores = _carregar_colaboradores()

    if token_hash not in colaboradores:
        return False, None

    dados = colaboradores[token_hash]

    if not dados.get("ativo", False):
        return False, None

    expiracao = datetime.fromisoformat(dados["expira_em"])
    if datetime.now() > expiracao:
        return False, None

    return True, dados


def listar_colaboradores_ativos() -> list[dict]:
    """
    Retorna uma lista com os dados dos colaboradores que possuem acesso ativo
    (independentemente de já ter expirado ou não).
    """
    colaboradores = _carregar_colaboradores()
    ativos = []
    for dados in colaboradores.values():
        if dados.get("ativo", False):
            expiracao = datetime.fromisoformat(dados["expira_em"])
            ativos.append(
                {
                    "email": dados["email"],
                    "nivel_acesso": dados["nivel_acesso"],
                    "criado_em": dados["criado_em"],
                    "expira_em": dados["expira_em"],
                    "expirado": datetime.now() > expiracao,
                }
            )
    return ativos


def revogar_acesso(email: str) -> int:
    """
    Revoga todos os tokens ativos de um colaborador identificado pelo e-mail.

    Retorna
    -------
    int
        Número de tokens revogados.
    """
    colaboradores = _carregar_colaboradores()
    revogados = 0
    for dados in colaboradores.values():
        if dados["email"] == email and dados.get("ativo", False):
            dados["ativo"] = False
            revogados += 1

    if revogados:
        _salvar_colaboradores(colaboradores)
        print(f"🚫 {revogados} token(s) revogado(s) para: {email}")
    else:
        print(f"⚠️  Nenhum token ativo encontrado para: {email}")

    return revogados


# ---------------------------------------------------------------------------
# Envio de e-mail
# ---------------------------------------------------------------------------

def enviar_link_por_email(
    email_destinatario: str,
    link: str,
    smtp_servidor: str,
    smtp_porta: int,
    smtp_usuario: str,
    smtp_senha: str,
    usar_tls: bool = True,
) -> None:
    """
    Envia o link de acesso por e-mail usando SMTP.

    Parâmetros
    ----------
    email_destinatario : str
        E-mail do colaborador que receberá o convite.
    link : str
        Link gerado por `criar_link_colaborador`.
    smtp_servidor : str
        Servidor SMTP (ex: 'smtp.gmail.com').
    smtp_porta : int
        Porta SMTP (ex: 587 para TLS, 465 para SSL).
    smtp_usuario : str
        E-mail/usuário de autenticação no servidor SMTP.
    smtp_senha : str
        Senha ou app-password do remetente.
    usar_tls : bool
        Se True, usa STARTTLS (porta 587); se False, usa SMTP_SSL (porta 465).
    """
    assunto = "Convite de Acesso – Agenda Aeronautas"
    corpo_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>🛫 Agenda Aeronautas – Acesso de Colaborador</h2>
        <p>Você foi convidado(a) para acessar o sistema <strong>Agenda Aeronautas</strong>.</p>
        <p>Clique no link abaixo ou copie-o e cole no aplicativo para ativar o seu acesso:</p>
        <p style="background:#f0f4ff; padding:12px; border-radius:6px; word-break:break-all;">
          <strong>{link}</strong>
        </p>
        <p>Este link é pessoal e intransferível. Não compartilhe com terceiros.</p>
        <p>Em caso de dúvidas, entre em contato com o administrador do sistema.</p>
        <hr/>
        <p style="font-size:11px; color:#888;">
          Este é um e-mail automático. Não responda a esta mensagem.
        </p>
      </body>
    </html>
    """

    mensagem = MIMEMultipart("alternative")
    mensagem["Subject"] = assunto
    mensagem["From"] = smtp_usuario
    mensagem["To"] = email_destinatario
    mensagem.attach(MIMEText(corpo_html, "html", "utf-8"))

    try:
        if usar_tls:
            servidor = smtplib.SMTP(smtp_servidor, smtp_porta)
            servidor.starttls()
        else:
            servidor = smtplib.SMTP_SSL(smtp_servidor, smtp_porta)

        servidor.login(smtp_usuario, smtp_senha)
        servidor.sendmail(smtp_usuario, email_destinatario, mensagem.as_string())
        servidor.quit()
        print(f"📧 E-mail enviado com sucesso para: {email_destinatario}")
    except Exception as erro:
        print(f"❌ Falha ao enviar e-mail para {email_destinatario}: {erro}")
        raise


# ---------------------------------------------------------------------------
# Interface gráfica (tkinter)
# ---------------------------------------------------------------------------

def interface_gerenciar_acessos() -> None:
    """
    Abre uma janela tkinter para gerenciar acessos de colaboradores de forma
    interativa: gerar link, listar ativos e revogar acesso.
    """
    if not _TKINTER_DISPONIVEL:
        raise RuntimeError(
            "O módulo tkinter não está disponível neste ambiente. "
            "Execute o script em um ambiente com interface gráfica."
        )

    root = tk.Tk()
    root.title("Gerenciar Acessos de Colaboradores – Agenda Aeronautas")
    root.geometry("520x420")
    root.resizable(False, False)

    tk.Label(
        root,
        text="🔐 Gerenciar Acessos de Colaboradores",
        font=("Arial", 14, "bold"),
        pady=10,
    ).pack()

    # ---- Gerar novo link ----
    frame_gerar = tk.LabelFrame(root, text="Gerar link de acesso", padx=10, pady=8)
    frame_gerar.pack(fill="x", padx=15, pady=6)

    tk.Label(frame_gerar, text="E-mail do colaborador:").grid(
        row=0, column=0, sticky="w"
    )
    entry_email = tk.Entry(frame_gerar, width=36)
    entry_email.grid(row=0, column=1, padx=6, pady=3)

    tk.Label(frame_gerar, text="Nível de acesso:").grid(row=1, column=0, sticky="w")
    nivel_var = tk.StringVar(value="leitura")
    frame_radio = tk.Frame(frame_gerar)
    frame_radio.grid(row=1, column=1, sticky="w", padx=6)
    for nivel in NIVEIS_ACESSO:
        tk.Radiobutton(frame_radio, text=nivel, variable=nivel_var, value=nivel).pack(
            side="left"
        )

    tk.Label(frame_gerar, text="Validade (dias):").grid(row=2, column=0, sticky="w")
    entry_validade = tk.Entry(frame_gerar, width=10)
    entry_validade.insert(0, str(VALIDADE_PADRAO_DIAS))
    entry_validade.grid(row=2, column=1, sticky="w", padx=6, pady=3)

    link_gerado = tk.StringVar()
    entry_link = tk.Entry(frame_gerar, textvariable=link_gerado, width=56, state="readonly")
    entry_link.grid(row=3, column=0, columnspan=2, padx=6, pady=(6, 2))

    def _gerar():
        email = entry_email.get().strip()
        if not email:
            messagebox.showwarning("Atenção", "Informe o e-mail do colaborador.")
            return
        try:
            validade = int(entry_validade.get())
        except ValueError:
            messagebox.showwarning("Atenção", "Validade deve ser um número inteiro.")
            return
        link = criar_link_colaborador(email, nivel_var.get(), validade)
        link_gerado.set(link)
        root.clipboard_clear()
        root.clipboard_append(link)
        messagebox.showinfo(
            "Link gerado",
            f"Link gerado e copiado para a área de transferência!\n\n{link}",
        )

    tk.Button(frame_gerar, text="Gerar link", command=_gerar, bg="#4CAF50", fg="white", width=14).grid(
        row=4, column=0, columnspan=2, pady=6
    )

    # ---- Revogar acesso ----
    frame_revogar = tk.LabelFrame(root, text="Revogar acesso", padx=10, pady=8)
    frame_revogar.pack(fill="x", padx=15, pady=6)

    tk.Label(frame_revogar, text="E-mail a revogar:").grid(row=0, column=0, sticky="w")
    entry_revogar = tk.Entry(frame_revogar, width=36)
    entry_revogar.grid(row=0, column=1, padx=6, pady=3)

    def _revogar():
        email = entry_revogar.get().strip()
        if not email:
            messagebox.showwarning("Atenção", "Informe o e-mail do colaborador.")
            return
        n = revogar_acesso(email)
        if n:
            messagebox.showinfo("Acesso revogado", f"{n} token(s) revogado(s) para:\n{email}")
        else:
            messagebox.showwarning("Aviso", f"Nenhum token ativo encontrado para:\n{email}")

    tk.Button(frame_revogar, text="Revogar acesso", command=_revogar, bg="#f44336", fg="white", width=14).grid(
        row=1, column=0, columnspan=2, pady=6
    )

    # ---- Listar colaboradores ----
    frame_listar = tk.LabelFrame(root, text="Colaboradores ativos", padx=10, pady=8)
    frame_listar.pack(fill="x", padx=15, pady=6)

    text_lista = tk.Text(frame_listar, height=5, state="disabled", font=("Courier", 9))
    text_lista.pack(fill="x")

    def _listar():
        ativos = listar_colaboradores_ativos()
        text_lista.config(state="normal")
        text_lista.delete("1.0", tk.END)
        if not ativos:
            text_lista.insert(tk.END, "Nenhum colaborador com acesso ativo.")
        else:
            text_lista.insert(tk.END, f"{'E-mail':<35} {'Nível':<10} {'Expira em':<22} {'Expirado'}\n")
            text_lista.insert(tk.END, "-" * 80 + "\n")
            for c in ativos:
                expirado = "⚠️ SIM" if c["expirado"] else "NÃO"
                text_lista.insert(
                    tk.END,
                    f"{c['email']:<35} {c['nivel_acesso']:<10} {c['expira_em'][:19]:<22} {expirado}\n",
                )
        text_lista.config(state="disabled")

    tk.Button(frame_listar, text="Atualizar lista", command=_listar, width=14).pack(pady=4)

    _listar()
    root.mainloop()


# ---------------------------------------------------------------------------
# Execução direta
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    interface_gerenciar_acessos()
