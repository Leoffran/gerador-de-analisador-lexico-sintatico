def closure(itens, producoes):
    """Fecha um conjunto de itens LR(0).

    Itens têm a forma (esq, dir_tupla, dot).
    Produções épsilon usam dir_tupla = () — ponto já no fim desde o início.
    """
    fechamento = set(itens)
    fila = list(itens)

    while fila:
        esq, dir, dot = fila.pop()
        if dot >= len(dir):
            continue
        B = dir[dot]
        for prod_esq, prod_dir in producoes:
            if prod_esq != B:
                continue
            item = (prod_esq, prod_dir, 0)
            if item not in fechamento:
                fechamento.add(item)
                fila.append(item)

    return frozenset(fechamento)


def goto(itens, simbolo, producoes):
    """Transição de um conjunto de itens por um símbolo."""
    movidos = set()
    for esq, dir, dot in itens:
        if dot < len(dir) and dir[dot] == simbolo:
            movidos.add((esq, dir, dot + 1))
    if not movidos:
        return frozenset()
    return closure(movidos, producoes)


def colecao_canonica(producoes, inicial):
    """Constrói a coleção canônica LR(0).

    Retorna (colecao, goto_map, prods_aug, inicial_aug).
      colecao  — lista de frozenset de itens, índice = número do estado
      goto_map — {(idx_estado, simbolo): idx_estado}
      prods_aug — [(esq, dir_tupla), ...]; prods_aug[0] é S' → S
      inicial_aug — nome do símbolo inicial aumentado
    """
    inicial_aug = inicial + "'"

    # Converte produções para tuplas; épsilon ['&'] vira ()
    prods_aug = [(inicial_aug, (inicial,))] + [
        (e, () if d == ['&'] else tuple(d)) for e, d in producoes
    ]

    todos_simbolos = {s for _, d in prods_aug for s in d}

    I0 = closure(frozenset([(inicial_aug, (inicial,), 0)]), prods_aug)
    colecao = [I0]
    goto_map = {}

    i = 0
    while i < len(colecao):
        I = colecao[i]
        for X in todos_simbolos:
            J = goto(I, X, prods_aug)
            if not J:
                continue
            if J not in colecao:
                colecao.append(J)
            j = colecao.index(J)
            goto_map[(i, X)] = j
        i += 1

    return colecao, goto_map, prods_aug, inicial_aug
