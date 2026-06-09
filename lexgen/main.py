# main.py
from analisador import parsear_er
from aho import construir_afd
from minimizacao import minimizar
from uniao import uniao
from determinizacao import determinizar

afd1 = minimizar(construir_afd(parsear_er("[a-zA-Z]([a-zA-Z]|[0-9])*"), "id"))
afd2 = minimizar(construir_afd(parsear_er("[1-9]([0-9])*|0"), "num"))

afnd = uniao(afd1, afd2)
afd  = determinizar(afnd)

print(f"estados:   {afd.estados}")
print(f"inicial:   {afd.start}")
print(f"aceitacao: {afd.aceitacao}")
print(f"transicoes:")
for (estado, simbolo), destino in afd.transicoes.items():
    print(f"  {estado} --{simbolo}--> {destino}")