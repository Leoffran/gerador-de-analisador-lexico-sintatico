from tkinter import *
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import os

_TESTES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'testes'))


class TelaSintatico(ttk.Frame):
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self._criar_interface()

    def _criar_interface(self):
        Label(self, text="Gramática", font=("Arial", 14, "bold")).pack(pady=(10, 0))

        barra = ttk.Frame(self)
        barra.pack(pady=(0, 5))
        Button(barra, text="Carregar .g", command=self._carregar_arquivo).pack(side="left", padx=5)
        Button(barra, text="Gerar Tabela", command=self._gerar).pack(side="left", padx=5)

        self.editor = Text(self, width=60, height=12)
        self.editor.pack(padx=10, pady=(0, 5))

        Label(self, text="Palavras Reservadas (uma por linha)").pack(anchor="w", padx=10)
        self.editor_pr = Text(self, width=60, height=4)
        self.editor_pr.pack(padx=10, pady=(0, 5))

        self._frame_resultado = None

    def _carregar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Abrir arquivo de gramática",
            initialdir=_TESTES_DIR,
            filetypes=[("Gramática", "*.g *.txt"), ("Todos os arquivos", "*.*")]
        )
        if not caminho:
            return
        try:
            with open(caminho) as f:
                conteudo = f.read()
            gramatica, keywords = self._parsear_arquivo(conteudo)
            self.editor.delete("1.0", "end")
            self.editor.insert("end", gramatica)
            self.editor_pr.delete("1.0", "end")
            self.editor_pr.insert("end", keywords)
        except Exception as e:
            messagebox.showerror("Erro ao carregar", str(e))

    def _parsear_arquivo(self, conteudo):
        """Separa o arquivo em duas seções: [grammar] e [keywords].

        O arquivo .g pode ter duas seções marcadas por cabeçalhos:
          [keywords]    — palavras reservadas, uma por linha
          [grammar]     — produções no formato <NT> ::= ...

        Se não houver seções, tudo é tratado como gramática.
        """
        if '[grammar]' not in conteudo:
            # arquivo simples sem seções: tudo é gramática
            return conteudo.strip(), ''

        secao_keywords = ''
        secao_grammar  = ''
        secao_atual    = None

        for linha in conteudo.splitlines():
            stripped = linha.strip()
            if stripped == '[keywords]':
                secao_atual = 'keywords'
            elif stripped == '[grammar]':
                secao_atual = 'grammar'
            elif secao_atual == 'keywords':
                secao_keywords += linha + '\n'
            elif secao_atual == 'grammar':
                secao_grammar  += linha + '\n'

        return secao_grammar.strip(), secao_keywords.strip()

    def _gerar(self):
        texto = self.editor.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Aviso", "Digite uma gramática.")
            return

        # coleta palavras reservadas do editor secundário
        texto_pr = self.editor_pr.get("1.0", "end").strip()
        palavras_reservadas = [p.strip() for p in texto_pr.splitlines() if p.strip()]

        try:
            conflitos = self.controlador.gerar_sintatico(texto, palavras_reservadas)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        self._mostrar_resultado(conflitos)

    def _mostrar_resultado(self, conflitos):
        # destrói o resultado anterior antes de exibir o novo
        if self._frame_resultado:
            self._frame_resultado.destroy()

        self._frame_resultado = ttk.Frame(self)
        self._frame_resultado.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ttk.Separator(self._frame_resultado, orient="horizontal").pack(fill="x", pady=5)

        if not conflitos:
            Label(
                self._frame_resultado,
                text="Gramática SLR(1) — tabela gerada com sucesso.",
                fg="green"
            ).pack()
        else:
            Label(
                self._frame_resultado,
                text=f"Gramática com {len(conflitos)} conflito(s):",
                fg="red"
            ).pack()
            txt = Text(self._frame_resultado, height=4, state="normal")
            txt.insert("end", "\n".join(conflitos))
            txt.config(state="disabled")
            txt.pack(fill="x", pady=(0, 5))

        # exibe FIRST/FOLLOW antes da tabela SLR
        self._renderizar_first_follow(self._frame_resultado)
        self._renderizar_tabela_slr(self._frame_resultado)

    def _renderizar_first_follow(self, parent):
        _, nao_terminais, _, _ = self.controlador.gramatica
        first_sets  = self.controlador.first
        follow_sets = self.controlador.follow
        nts = sorted(nao_terminais)

        Label(parent, text="FIRST e FOLLOW", font=("Arial", 9, "bold"), anchor="w").pack(anchor="w", pady=(6, 0))

        # altura proporcional ao número de não-terminais (2 blocos: FIRST e FOLLOW)
        txt = Text(parent, height=len(nts) * 2 + 1, font=("Courier", 9), state="normal")
        for nt in nts:
            first_str = ', '.join(sorted(first_sets[nt]))
            txt.insert("end", f"FIRST ({nt}) = {{ {first_str} }}\n")
        txt.insert("end", "\n")
        for nt in nts:
            follow_str = ', '.join(sorted(follow_sets[nt]))
            txt.insert("end", f"FOLLOW({nt}) = {{ {follow_str} }}\n")
        txt.config(state="disabled")
        txt.pack(fill="x", pady=(0, 6))

    def _renderizar_tabela_slr(self, parent):
        tabela_acao, tabela_goto, prods = self.controlador.tabela_slr
        _, nao_terminais, terminais, _ = self.controlador.gramatica
        n_estados = len(self.controlador.itens_lr)

        # colunas da tabela: terminais (ação) à esquerda, não-terminais (desvio) à direita
        terminais_ord = sorted(terminais) + ['$']
        nts_ord       = sorted(nao_terminais)
        colunas   = ["Estado"] + terminais_ord + nts_ord
        cabecalhos = ["Estado"] + [f"{t}" for t in terminais_ord] + [f"{nt}" for nt in nts_ord]

        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)

        # legenda numerando as produções para facilitar a leitura das ações "r0", "r1", ...
        legenda = "Produções:  " + "   ".join(
            f"r{i}: {e} ::= {' '.join(d) if d else 'ε'}"
            for i, (e, d) in enumerate(prods)
        )
        Label(frame, text=legenda, font=("Courier", 8), anchor="w", justify="left",
              wraplength=700).pack(anchor="w", padx=4, pady=(4, 2))

        # cabeçalho duplo: "ação" sobre os terminais, "desvio" sobre os não-terminais
        n_term = len(terminais_ord)
        sep_frame = ttk.Frame(frame)
        sep_frame.pack(fill="x")
        Label(sep_frame, text="").grid(row=0, column=0, padx=2)
        Label(sep_frame, text="ação",   font=("Arial", 9, "bold")).grid(
            row=0, column=1, columnspan=n_term)
        Label(sep_frame, text="desvio", font=("Arial", 9, "bold")).grid(
            row=0, column=1 + n_term, columnspan=len(nts_ord))

        tree = ttk.Treeview(frame, columns=colunas, show="headings", height=min(n_estados + 1, 14))
        for col, cab in zip(colunas, cabecalhos):
            tree.heading(col, text=cab)
            tree.column(col, width=70, anchor="center", minwidth=50)
        tree.column("Estado", width=60)

        sb_h = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        sb_v = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        tree.configure(xscrollcommand=sb_h.set, yscrollcommand=sb_v.set)
        sb_v.pack(side="right", fill="y")
        sb_h.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        def fmt_acao(v):
            # converte as tuplas internas para a notação clássica do livro
            # ('shift', 3)   →  "s3"
            # ('reduce', 1)  →  "r1"
            # ('accept',)    →  "acc"
            if v is None:           return ""
            if v[0] == 'shift':     return f"s{v[1]}"
            if v[0] == 'reduce':    return f"r{v[1]}"
            if v[0] == 'accept':    return "acc"
            return str(v)

        for i in range(n_estados):
            linha = [str(i)]
            for t in terminais_ord:
                linha.append(fmt_acao(tabela_acao.get((i, t))))
            for nt in nts_ord:
                v = tabela_goto.get((i, nt))
                linha.append(str(v) if v is not None else "")
            tree.insert("", "end", values=linha)
