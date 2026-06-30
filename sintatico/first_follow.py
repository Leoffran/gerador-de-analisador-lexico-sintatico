def _first_cadeia(simbolos, first_sets, nao_terminais):
    """Retorna FIRST de uma sequência de símbolos."""
    resultado = set()
    for s in simbolos:
        if s in nao_terminais:
            resultado |= (first_sets[s] - {'&'})
            if '&' not in first_sets[s]:
                break
        else:
            resultado.add(s)
            break
    else:
        resultado.add('&')
    return resultado


def first(producoes, nao_terminais):
    """Computa FIRST para todos os não-terminais. Retorna {nt: set}."""
    sets = {nt: set() for nt in nao_terminais}

    changed = True
    while changed:
        changed = False
        for esq, dir in producoes:
            antes = len(sets[esq])
            sets[esq] |= _first_cadeia(dir, sets, nao_terminais)
            if len(sets[esq]) > antes:
                changed = True

    return sets


def follow(producoes, nao_terminais, first_sets, inicial):
    """Computa FOLLOW para todos os não-terminais. Retorna {nt: set}."""
    sets = {nt: set() for nt in nao_terminais}
    sets[inicial].add('$')

    changed = True
    while changed:
        changed = False
        for esq, dir in producoes:
            for i, B in enumerate(dir):
                if B not in nao_terminais:
                    continue
                antes = len(sets[B])
                beta = dir[i + 1:]
                first_beta = _first_cadeia(beta, first_sets, nao_terminais)
                sets[B] |= (first_beta - {'&'})
                if not beta or '&' in first_beta:
                    sets[B] |= sets[esq]
                if len(sets[B]) > antes:
                    changed = True

    return sets
