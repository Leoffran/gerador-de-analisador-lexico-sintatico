from analisador import parsear_er

testes = [
    "a",
    "a|b",
    "a*",
    "a+",
    "a?",
    "a(a|b)*",
    "(a|b)+",
]

for er in testes:
    print(f"\nER: {er}")
    ast = parsear_er(er)
    print(f"AST: {ast}")