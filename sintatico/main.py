# main.py
from gramatica import ler_gramatica

producoes, nao_terminais, terminais, inicial = ler_gramatica('gramaticas/gramatica1.txt')

print(f"inicial:       {inicial}")
print(f"não-terminais: {nao_terminais}")
print(f"terminais:     {terminais}")
print(f"produções:")
for esq, dir in producoes:
    print(f"  {esq} ::= {' '.join(dir)}")