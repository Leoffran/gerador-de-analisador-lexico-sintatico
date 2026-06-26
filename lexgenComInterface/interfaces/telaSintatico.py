from tkinter import *
from tkinter import ttk
import tkinter as tk


class TelaSintatico(ttk.Frame):
    def __init__(self, master, controlador):
        super().__init__(master)

        self.controlador = controlador

        Label(self, text="Gramática", font=("Arial",14,"bold")).pack()

        self.editor = Text(self, width=60, height=20)

        self.editor.pack()

        Button(self, text="Gerar Tabela").pack()
