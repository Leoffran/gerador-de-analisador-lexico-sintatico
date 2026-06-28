import sys
import os

# Adiciona o diretório sintatico/ ao path para importação dos módulos
_sintatico_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'sintatico')
)
if _sintatico_dir not in sys.path:
    sys.path.insert(0, _sintatico_dir)

from analisador import parsear_er, ler_definicoes
from aho import construir_afd
from minimizacao import minimizar
from uniao import uniao
from determinizacao import determinizar
from lexer import lexer

from gramatica import ler_gramatica_texto
from first_follow import first, follow
from closure import colecao_canonica
from tabela_slr import construir_tabela_slr
from parser import parsear
from tabela_simbolos import TabelaSimbolos


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
        self._tabela_simbolos = None

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

    def gerar_sintatico(self, texto_gramatica, palavras_reservadas=None):
        """Compila a gramática e constrói a tabela SLR.

        texto_gramatica    — string com as produções (formato ::=)
        palavras_reservadas — lista de strings ou None

        Retorna lista de conflitos (vazia se a gramática é SLR(1)).
        Levanta Exception em caso de erro de parsing da gramática.
        """
        producoes, nao_terminais, terminais, inicial = ler_gramatica_texto(texto_gramatica)

        first_sets = first(producoes, nao_terminais)
        follow_sets = follow(producoes, nao_terminais, first_sets, inicial)

        colecao, goto_map, prods_aug, inicial_aug = colecao_canonica(producoes, inicial)

        tabela_acao, tabela_goto_t, conflitos, prods_orig = construir_tabela_slr(
            colecao, goto_map, follow_sets, prods_aug, inicial_aug
        )

        self.gramatica = (producoes, nao_terminais, terminais, inicial)
        self.first = first_sets
        self.follow = follow_sets
        self.itens_lr = colecao
        self.tabela_slr = (tabela_acao, tabela_goto_t, prods_orig)
        self._tabela_simbolos = TabelaSimbolos(palavras_reservadas)

        return conflitos

    def analisar_sintatico(self, codigo):
        """Executa léxico + tabela de símbolos + parser SLR sobre o código.

        Retorna string formatada com tokens e passos de análise.
        """
        if self.afd is None:
            raise Exception("Primeiro gere o analisador léxico.")
        if self.tabela_slr is None:
            raise Exception("Primeiro gere o analisador sintático.")

        tokens_brutos = lexer(self.afd, codigo)

        linhas_exibicao = []
        tokens_parser = []

        for lexema, padrao in tokens_brutos:
            if padrao == 'id':
                _, ref = self._tabela_simbolos.buscar_ou_inserir(lexema)
                if ref == 'PR':
                    # palavra reservada: exibe como PR, parser recebe o próprio lexema
                    linhas_exibicao.append(f"<{lexema}, PR>")
                    tokens_parser.append((lexema, lexema))
                else:
                    # identificador novo: exibe com linha da tabela, parser recebe 'id'
                    linhas_exibicao.append(f"<id, {ref}>")
                    tokens_parser.append((lexema, 'id'))
            else:
                linhas_exibicao.append(f"<{lexema}, {padrao}>")
                tokens_parser.append((lexema, padrao))

        tabela_acao, tabela_goto_t, prods_orig = self.tabela_slr
        passos, erro = parsear(tokens_parser, tabela_acao, tabela_goto_t, prods_orig)

        saida = "=== Tokens ===\n"
        saida += "\n".join(linhas_exibicao)
        saida += "\n\n=== Análise Sintática ===\n"
        saida += "\n".join(passos)
        if erro:
            saida += "\n" + erro
        return saida
