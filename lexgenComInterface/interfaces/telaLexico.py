from tkinter import *
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from analisador import ler_definicoes


class TelaLexico(ttk.Frame):
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self.nb_tabelas = None

        Label(self, text="Definições Regulares", font=("Arial", 14, "bold")).pack(pady=(10, 0))

        self.editor = Text(self, width=60, height=10)
        self.editor.pack(padx=10, pady=5)

        barra = ttk.Frame(self)
        barra.pack(pady=(0, 5))
        Button(barra, text="Carregar .er", command=self.carregar_arquivo).pack(side="left", padx=5)
        Button(barra, text="Gerar", command=self.gerar).pack(side="left", padx=5)

    def carregar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Abrir arquivo de definições regulares",
            filetypes=[("Definições Regulares", "*.er"), ("Todos os arquivos", "*.*")]
        )
        if not caminho:
            return
        try:
            defs = ler_definicoes(caminho)
            self.editor.delete("1.0", "end")
            for nome, er in defs:
                self.editor.insert("end", f"{nome}: {er}\n")
        except Exception as e:
            messagebox.showerror("Erro ao carregar", str(e))

    def gerar(self):
        self.controlador.expressoes.clear()

        linhas = self.editor.get("1.0", "end").splitlines()
        for linha in linhas:
            if ":" not in linha:
                continue
            nome, er = linha.split(":", 1)
            self.controlador.adicionar_er(nome.strip(), er.strip())

        if not self.controlador.expressoes:
            messagebox.showwarning("Aviso", "Nenhuma definição regular encontrada.")
            return

        try:
            self.controlador.gerar_lexico()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        self._atualizar_visualizacao()
        messagebox.showinfo("Sucesso", "Analisador léxico gerado.")

    def _atualizar_visualizacao(self):
        if self.nb_tabelas:
            self.nb_tabelas.destroy()

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=5)
        Label(self, text="Autômatos e Tabela Léxica", font=("Arial", 11, "bold")).pack()

        self.nb_tabelas = ttk.Notebook(self)
        self.nb_tabelas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for nome, afd in self.controlador.afds.items():
            frame = ttk.Frame(self.nb_tabelas)
            self.nb_tabelas.add(frame, text=nome)
            self._renderizar_tabela(frame, afd)

        frame_final = ttk.Frame(self.nb_tabelas)
        self.nb_tabelas.add(frame_final, text="Tabela Léxica Final")
        self._renderizar_tabela(frame_final, self.controlador.afd, mostrar_padrao=True)

    def _renderizar_tabela(self, frame, automato, mostrar_padrao=False):
        simbolos = sorted(automato.alfabeto)
        colunas = ["Estado"] + simbolos + (["Padrão"] if mostrar_padrao else [])

        tree = ttk.Treeview(frame, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=60, anchor="center", minwidth=40)
        tree.column("Estado", width=80, anchor="center")

        sb_v = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        sb_h = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)

        sb_v.pack(side="right", fill="y")
        sb_h.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        for estado in sorted(automato.estados):
            prefixo = ""
            if estado == automato.start:
                prefixo += "→ "
            if estado in automato.aceitacao:
                prefixo += "* "
            nome_estado = f"{prefixo}{estado}"

            celulas = [nome_estado]
            for s in simbolos:
                destino = automato.transicoes.get((estado, s))
                celulas.append(str(destino) if destino is not None else "-")

            if mostrar_padrao:
                celulas.append(automato.aceitacao.get(estado, ""))

            tree.insert("", "end", values=celulas)
