from analisador import parsear_er, ler_definicoes
from aho import construir_afd
from minimizacao import minimizar
from uniao import uniao
from determinizacao import determinizar
from lexer import lexer

class Controlador:
    def __init__(self):
        self.expressoes = {}

        self.afds = {}

        self.afds_minimizados = {}

        self.afnd = None

        self.afd = None

        self.tokens = []

        self.tabela_lexica = None

        self.gramatica = None

        self.first = None

        self.follow = None

        self.itens_lr = None

        self.tabela_slr = None
    
    def adicionar_er(self, nome, er):
        self.expressoes[nome] = er

    def gerar_lexico(self):
        self.afds = {}

        for nome, er in self.expressoes.items():

            arvore = parsear_er(er)

            afd = construir_afd(arvore, nome)

            afd = minimizar(afd)

            self.afds[nome] = afd

        afnd = uniao(*self.afds.values())

        self.afnd = afnd

        self.afd = determinizar(afnd)

    def analisar_texto(self, texto):
        if self.afd is None:
            raise Exception("Primeiro gere o analisador léxico.")

        return lexer(self.afd, texto)
    
    def analisar_sintatico(self, codigo):
        pass