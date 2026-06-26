# main.py
from analisador import parsear_er, ler_definicoes
from aho import construir_afd
from minimizacao import minimizar
from uniao import uniao
from determinizacao import determinizar
from lexer import lexer, salvar_tokens

# lê as definições do arquivo
defs = ler_definicoes('testes/exemplo1.er')

# monta um AFD para cada definição
afds = []
for nome, er in defs:
    ast = parsear_er(er)
    afd = minimizar(construir_afd(ast, nome))
    afds.append(afd)

# une e determiniza
afnd = uniao(*afds)
afd  = determinizar(afnd)

# lê o texto fonte inteiro
texto  = open('testes/exemplo1.txt').read()

# tokeniza
tokens = lexer(afd, texto)

# imprime na tela
for lexema, padrao in tokens:
    print(f"<{lexema}, {padrao}>")

# salva no arquivo
salvar_tokens(tokens)