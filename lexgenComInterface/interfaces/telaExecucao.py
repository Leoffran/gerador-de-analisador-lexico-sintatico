import tkinter as tk
from tkinter import ttk, messagebox


class TelaExecucao(ttk.Frame):
    def __init__(self, master, controlador):
        super().__init__(master)

        self.controlador = controlador

        self.criar_interface()

    def criar_interface(self):

        # ============================
        # Barra de botões
        # ============================

        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=10, pady=10)

        ttk.Button(barra, text="Análise Léxica", command=self.executar_lexico).pack(side="left")

        ttk.Button(barra, text="Análise Sintática", command=self.executar_sintatico).pack(side="left", padx=5)

        ttk.Button(barra, text="Limpar", command=self.limpar).pack(side="right")

        # ============================
        # Código Fonte
        # ============================

        ttk.Label(self, text="Código Fonte").pack(anchor="w", padx=10)

        self.editor = tk.Text(self, height=15)

        self.editor.pack(fill="both", expand=True, padx=10)

        # ============================
        # Notebook de resultados
        # ============================

        ttk.Label(self,text="Resultado").pack(anchor="w", padx=10, pady=(10, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ----------------------------------
        # Aba Tokens
        # ----------------------------------

        frame_tokens = ttk.Frame(self.notebook)

        self.notebook.add(frame_tokens, text="Tokens")

        self.txt_tokens = tk.Text(frame_tokens, state="disabled")

        self.txt_tokens.pack(fill="both", expand=True)

        # ----------------------------------
        # Aba Parsing
        # ----------------------------------

        frame_parsing = ttk.Frame(self.notebook)

        self.notebook.add(frame_parsing, text="Parsing / Erros")

        self.txt_parsing = tk.Text(frame_parsing, state="disabled")

        self.txt_parsing.pack(fill="both", expand=True)

    def executar_lexico(self):
        codigo = self.editor.get("1.0", tk.END).strip()

        if codigo == "":
            messagebox.showwarning("Aviso", "Digite um código.")
            return

        try:
            tokens = self.controlador.analisar_texto(codigo)

            resultado = ""

            for lexema, token in tokens:
                resultado += f"<{lexema}, {token}>\n"

            self.escrever(self.txt_tokens, resultado)

            self.notebook.select(0)

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def executar_sintatico(self):
        self.escrever(
            self.txt_parsing,
            "Analisador sintático ainda não implementado."
        )
        self.notebook.select(1)
        #Depois basta trocar por:
        #resultado = self.controlador.analisar_sintatico(codigo)
        #self.escrever(self.txt_parsing, resultado)
    
    # metodo auxiliar para limpar o editor e os resultados
    def escrever(self, widget, texto):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, texto)
        widget.config(state="disabled")

    # metodo auxiliar para limpar o editor e os resultados
    def limpar(self):
        self.editor.delete("1.0", tk.END)
        self.escrever(self.txt_tokens, "")
        self.escrever(self.txt_parsing, "")