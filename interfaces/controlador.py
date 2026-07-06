import sys
import os

# Adiciona lexico/ e sintatico/ ao path para que os módulos sejam encontrados
_lexico_dir   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lexico'))
_sintatico_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sintatico'))
for _d in (_lexico_dir, _sintatico_dir):
    if _d not in sys.path:
        sys.path.insert(0, _d)

# módulos do léxico
from analisador import parsear_er, ler_definicoes
from aho import construir_afd
from minimizacao import minimizar
from uniao import uniao
from determinizacao import determinizar
from lexer import lexer

# módulos do sintático
from gramatica import ler_gramatica_texto
from first_follow import first, follow
from closure import colecao_canonica
from tabela_slr import construir_tabela_slr
from parser import parsear
from tabela_simbolos import TabelaSimbolos


class Controlador:
    """Ponto central de integração entre interface e algoritmos.

    Guarda o estado de toda a sessão: autômatos gerados, gramática,
    tabela SLR e tabela de símbolos — permitindo que as três abas
    compartilhem os mesmos dados sem se acoplarem diretamente.
    """

    def __init__(self):
        # ---- estado do léxico ----
        self.expressoes = {}          # {nome: er_string} lidos da aba léxica
        self.afds = {}                # {nome: AFD minimizado} — um por padrão
        self.afnd = None              # AFND resultante da união de todos os AFDs
        self.afd  = None              # AFD final determinizado (usado pelo lexer)

        # ---- estado do sintático ----
        self.gramatica   = None       # (producoes, nao_terminais, terminais, inicial)
        self.first       = None       # {símbolo: set} — conjuntos FIRST
        self.follow      = None       # {símbolo: set} — conjuntos FOLLOW
        self.itens_lr    = None       # coleção canônica de itens LR(0)
        self.tabela_slr  = None       # (tabela_acao, tabela_goto, prods_originais)
        self.conflitos   = []         # conflitos shift/reduce ou reduce/reduce da última tabela
        self._tabela_simbolos = None  # TabelaSimbolos da última análise

    def adicionar_er(self, nome, er):
        self.expressoes[nome] = er

    def gerar_lexico(self):
        """Pipeline léxico — ordem obrigatória definida pela teoria:
        parsear_er → construir_afd → minimizar → uniao → determinizar
        """
        self.afds = {}
        for nome, er in self.expressoes.items():
            # converte a ER em AST, depois em AFD, depois minimiza
            arvore = parsear_er(er)
            afd    = construir_afd(arvore, nome)
            afd    = minimizar(afd)
            self.afds[nome] = afd

        # une todos os AFDs individuais em um único AFND via ε-transições
        afnd = uniao(*self.afds.values())
        self.afnd = afnd

        # determiniza o AFND para obter o AFD final que o lexer vai usar
        self.afd = determinizar(afnd)

    def analisar_texto(self, texto):
        """Roda o lexer sobre o texto e retorna lista de (lexema, padrão)."""
        if self.afd is None:
            raise Exception("Primeiro gere o analisador léxico.")
        return lexer(self.afd, texto)

    def gerar_sintatico(self, texto_gramatica, palavras_reservadas=None):
        """Pipeline sintático — ordem obrigatória definida pela teoria:
        ler_gramatica → first/follow → colecao_canonica → construir_tabela_slr

        Retorna lista de conflitos (vazia se a gramática é SLR(1)).
        """
        # lê as produções e infere terminais e não-terminais
        producoes, nao_terminais, terminais, inicial = ler_gramatica_texto(texto_gramatica)

        # calcula FIRST e FOLLOW (necessários para preencher a tabela de redução)
        first_sets  = first(producoes, nao_terminais)
        follow_sets = follow(producoes, nao_terminais, first_sets, inicial)

        # constrói a coleção canônica de itens LR(0) e o mapa de GOTO
        colecao, goto_map, prods_aug, inicial_aug = colecao_canonica(producoes, inicial)

        # preenche ACTION e GOTO; detecta conflitos shift/reduce e reduce/reduce
        tabela_acao, tabela_goto_t, conflitos, prods_orig = construir_tabela_slr(
            colecao, goto_map, follow_sets, prods_aug, inicial_aug
        )

        # persiste tudo no estado da sessão para as abas Sintático e Execução
        self.gramatica  = (producoes, nao_terminais, terminais, inicial)
        self.first      = first_sets
        self.follow     = follow_sets
        self.itens_lr   = colecao
        self.tabela_slr = (tabela_acao, tabela_goto_t, prods_orig)
        self.conflitos  = conflitos
        self._tabela_simbolos = TabelaSimbolos(palavras_reservadas)

        return conflitos

    def analisar_sintatico(self, codigo):
        """Executa léxico + tabela de símbolos + parser SLR sobre o código.

        Integração entre as duas partes do trabalho:
          1. Léxico tokeniza o código
          2. Identificadores são consultados na tabela de símbolos
             — palavras reservadas: exibidas como <for, PR>
             — identificadores novos: exibidos como <id, N> (N = linha da tabela)
          3. Parser SLR consome a sequência de padrões

        Retorna string formatada com tokens e passos de análise.
        """
        if self.afd is None:
            raise Exception("Primeiro gere o analisador léxico.")
        if self.tabela_slr is None:
            raise Exception("Primeiro gere o analisador sintático.")
        if self.conflitos:
            raise Exception(
                "A gramática possui conflitos SLR(1) (veja a aba Projeto Sintático); "
                "corrija a gramática antes de executar o parser."
            )

        tokens_brutos = lexer(self.afd, codigo)

        linhas_exibicao = []  # o que aparece na coluna "Tokens" da interface
        tokens_parser   = []  # o que o parser recebe (usa padrão, não lexema)

        for lexema, padrao in tokens_brutos:
            if padrao == 'id':
                _, ref = self._tabela_simbolos.buscar_ou_inserir(lexema)
                if ref == 'PR':
                    # palavra reservada: o parser usa o próprio lexema como token
                    # ex: "for" → parser recebe 'for', não 'id'
                    linhas_exibicao.append(f"<{lexema}, PR>")
                    tokens_parser.append((lexema, lexema))
                else:
                    # identificador: exibe com número de linha, parser recebe 'id'
                    linhas_exibicao.append(f"<id, {ref}>")
                    tokens_parser.append((lexema, 'id'))
            else:
                # terminais não-id: passam direto (ex: mais, vezes, num)
                linhas_exibicao.append(f"<{lexema}, {padrao}>")
                tokens_parser.append((lexema, padrao))

        tabela_acao, tabela_goto_t, prods_orig = self.tabela_slr
        passos, erro = parsear(tokens_parser, tabela_acao, tabela_goto_t, prods_orig)

        saida  = "=== Tokens ===\n"
        saida += "\n".join(linhas_exibicao)
        saida += "\n\n=== Análise Sintática ===\n"
        saida += "\n".join(passos)
        return saida
