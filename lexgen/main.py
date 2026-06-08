from analisador import parsear_er
from aho import construir_afd

testes = [
    ("a",        "a"),
    ("a|b",      "a_ou_b"),
    ("a*",       "fecho"),
    ("a(a|b)*",  "id"),
    ("(a|b)*abb","abb"),
]

for er, nome in testes:
    print(f"\nER: {er}")
    ast = parsear_er(er)
    afd = construir_afd(ast, nome)
    print(f"estados:   {afd.estados}")
    print(f"alfabeto:  {afd.alfabeto}")
    print(f"inicial:   {afd.start}")
    print(f"aceitacao: {afd.aceitacao}")
    print(f"transicoes:")
    for (estado, simbolo), destino in afd.transicoes.items():
        print(f"  {set(estado)} --{simbolo}--> {set(destino)}")