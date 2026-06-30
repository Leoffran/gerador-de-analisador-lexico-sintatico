import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from interfaces.telaLexico import TelaLexico
from interfaces.telaSintatico import TelaSintatico
from interfaces.telaExecucao import TelaExecucao
from interfaces.controlador import Controlador

class MainInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador Léxico e Sintático")
        self.geometry("800x600")

        # usado para deixar as interfaces independentes, mas ainda assim poderem se comunicar
        self.controlador = Controlador()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        notebook.add(TelaLexico(notebook, self.controlador), text="Projeto Léxico")
        notebook.add(TelaSintatico(notebook, self.controlador), text="Projeto Sintático")
        notebook.add(TelaExecucao(notebook, self.controlador), text="Execução")