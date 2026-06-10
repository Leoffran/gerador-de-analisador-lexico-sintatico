# main.py
from analisador import parsear_er, ler_definicoes
from aho import construir_afd
from minimizacao import minimizar
from uniao import uniao
from determinizacao import determinizar
from lexer import lexer

# monta o AFD final
afd1 = minimizar(construir_afd(parsear_er("[a-zA-Z]([a-zA-Z]|[0-9])*"), "id"))
afd2 = minimizar(construir_afd(parsear_er("[1-9]([0-9])*|0"), "num"))

afnd = uniao(afd1, afd2)
afd  = determinizar(afnd)

# testa
testes = [
    "a1 0 teste2 21 alpha123 3444 a43teste",
    "abc@",
    "abc@@",
    "0 1 2 3",
    "abc 123 @@@",
]

for texto in testes:
    print(f"\ntexto: '{texto}'")
    tokens = lexer(afd, texto)
    for lexema, padrao in tokens:
        print(f"  <{lexema}, {padrao}>")