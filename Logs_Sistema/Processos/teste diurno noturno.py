import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

def calcular_diurno_noturno(inicio_str, fim_str):
    formato = "%H:%M"
    hoje = datetime.today().date()
    try:
        inicio = datetime.combine(hoje, datetime.strptime(inicio_str, formato).time())
        fim = datetime.combine(hoje, datetime.strptime(fim_str, formato).time())
    except ValueError:
        raise ValueError("Formato de hora inválido. Use HH:MM.")

    if fim <= inicio:
        fim += timedelta(days=1)

    def is_noturno(horario):
        hora = horario.time()
        return hora < datetime.strptime("06:00", formato).time() or hora >= datetime.strptime("18:00", formato).time()

    atual = inicio
    diurno = timedelta()
    noturno = timedelta()

    while atual < fim:
        proximo = atual + timedelta(minutes=1)
        if is_noturno(atual):
            noturno += timedelta(minutes=1)
        else:
            diurno += timedelta(minutes=1)
        atual = proximo

    return diurno, noturno

def calcular():
    inicio = entrada_inicio.get()
    fim = entrada_fim.get()
    try:
        diurno, noturno = calcular_diurno_noturno(inicio, fim)
        resultado_diurno.config(text=f"Tempo diurno: {str(diurno)}")
        resultado_noturno.config(text=f"Tempo noturno: {str(noturno)}")
    except ValueError as e:
        messagebox.showerror("Erro", str(e))

# Interface gráfica
janela = tk.Tk()
janela.title("Cálculo de Tempo Diurno e Noturno")

tk.Label(janela, text="Hora de Início (HH:MM):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entrada_inicio = tk.Entry(janela)
entrada_inicio.grid(row=0, column=1, padx=10, pady=5)

tk.Label(janela, text="Hora de Fim (HH:MM):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entrada_fim = tk.Entry(janela)
entrada_fim.grid(row=1, column=1, padx=10, pady=5)

botao_calcular = tk.Button(janela, text="Calcular", command=calcular)
botao_calcular.grid(row=2, column=0, columnspan=2, pady=10)

resultado_diurno = tk.Label(janela, text="Tempo diurno: ")
resultado_diurno.grid(row=3, column=0, columnspan=2)

resultado_noturno = tk.Label(janela, text="Tempo noturno: ")
resultado_noturno.grid(row=4, column=0, columnspan=2)

janela.mainloop()