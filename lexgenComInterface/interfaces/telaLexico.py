from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk


class TelaLexico(ttk.Frame):
    def __init__(self, master, controlador):
        super().__init__(master)

        self.controlador = controlador

        Label(self, text="Definições Regulares", font=("Arial",14,"bold")).pack()

        self.editor = Text(self, width=60, height=20)

        self.editor.pack(padx=10,pady=10)

        Button(self,text="Gerar", command=self.gerar).pack()
    
    def gerar(self):
        self.controlador.expressoes.clear()

        linhas = self.editor.get("1.0", "end").splitlines()

        for linha in linhas:
            if ":" not in linha:
                continue

            nome, er = linha.split(":", 1)

            self.controlador.adicionar_er(nome.strip(), er.strip())

        self.controlador.gerar_lexico()
        
        messagebox.showinfo("Sucesso", "Analisador léxico gerado.")