import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from gramatica import ler_gramatica
from first_follow import first, follow
from closure import colecao_canonica
from tabela_slr import construir_tabela_slr
from parser import parsear

def testar(caminho, entrada_tokens):
    producoes, nao_terminais, terminais, inicial = ler_gramatica(caminho)

    print(f"Inicial: {inicial}")
    print(f"Não-terminais: {nao_terminais}")
    print(f"Terminais: {terminais}")
    print()

    first_sets = first(producoes, nao_terminais)
    follow_sets = follow(producoes, nao_terminais, first_sets, inicial)

    print("FIRST:")
    for nt in sorted(nao_terminais):
        print(f"  {nt}: {first_sets[nt]}")
    print("FOLLOW:")
    for nt in sorted(nao_terminais):
        print(f"  {nt}: {follow_sets[nt]}")
    print()

    colecao, goto_map, prods_aug, inicial_aug = colecao_canonica(producoes, inicial)
    print(f"Estados LR(0): {len(colecao)}")

    tabela_acao, tabela_goto, conflitos, prods_orig = construir_tabela_slr(
        colecao, goto_map, follow_sets, prods_aug, inicial_aug
    )

    if conflitos:
        print("CONFLITOS:")
        for c in conflitos:
            print(f"  {c}")
    else:
        print("Gramática SLR(1) sem conflitos.")
    print()

    # tokens: lista de (lexema, padrao)
    tokens = [(t, t) for t in entrada_tokens.split()]
    print(f"Entrada: {entrada_tokens}")
    passos, erro = parsear(tokens, tabela_acao, tabela_goto, prods_orig)
    for p in passos:
        print(" ", p)
    if erro:
        print("ERRO:", erro)


if __name__ == '__main__':
    testar('gramaticas/gramatica1.txt', 'id + id * id')
