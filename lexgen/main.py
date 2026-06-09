# main.py
from analisador import parsear_er
from aho import construir_afd
from minimizacao import minimizar
from uniao import uniao

afd1 = minimizar(construir_afd(parsear_er("[a-zA-Z]([a-zA-Z]|[0-9])*"), "id"))
afd2 = minimizar(construir_afd(parsear_er("[1-9]([0-9])*|0"), "num"))

afnd = uniao(afd1, afd2)
print(f"estados:   {afnd.estados}")
print(f"inicial:   {afnd.start}")
print(f"aceitacao: {afnd.aceitacao}")
print(f"transicoes:")
for (estado, simbolo), destinos in afnd.transicoes.items():
    print(f"  {estado} --{simbolo}--> {destinos}")