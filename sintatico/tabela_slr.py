def construir_tabela_slr(colecao, goto_map, follow_sets, prods_aug, inicial_aug):
    """Algoritmo 4.46 (slide p.70-71): constrói ACTION e GOTO do SLR.

    Retorna (tabela_acao, tabela_goto, conflitos, prods_originais).
      tabela_acao — {(estado, terminal): ('shift',j) | ('reduce',idx) | ('accept',)}
      tabela_goto — {(estado, nao_terminal): estado}
      conflitos   — lista de strings descrevendo conflitos shift/reduce ou reduce/reduce
      prods_originais — [(esq, dir_tupla), ...] sem a produção aumentada S' → S
    """
    nao_terminais = {esq for esq, _ in prods_aug}
    prods_originais = prods_aug[1:]

    tabela_acao = {}
    tabela_goto = {}
    conflitos = []

    def registrar_acao(chave, valor):
        if chave in tabela_acao and tabela_acao[chave] != valor:
            conflitos.append(
                f"conflito em estado {chave[0]}, símbolo '{chave[1]}': "
                f"{tabela_acao[chave]} vs {valor}"
            )
        tabela_acao[chave] = valor

    # Passo 2a e 3: shift e goto a partir do goto_map
    for (i, X), j in goto_map.items():
        if X in nao_terminais:
            tabela_goto[(i, X)] = j
        else:
            registrar_acao((i, X), ('shift', j))

    # Passos 2b e 2c: reduce e accept a partir dos itens com ponto no fim
    for i, I in enumerate(colecao):
        for esq, dir, dot in I:
            if dot < len(dir):
                continue
            if esq == inicial_aug:
                registrar_acao((i, '$'), ('accept',))
            else:
                prod = (esq, dir)
                idx = next(j for j, p in enumerate(prods_originais) if p == prod)
                for a in follow_sets.get(esq, set()):
                    registrar_acao((i, a), ('reduce', idx))

    return tabela_acao, tabela_goto, conflitos, prods_originais
