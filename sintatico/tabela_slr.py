def construir_tabela_slr(colecao, goto_map, follow_sets, prods_aug, inicial_aug):
    """Tabela SLR — Aho Algoritmo 4.38.

    Para cada estado i e item [A → α · a β] com 'a' terminal: ACTION[i,a] = shift j
      onde j = GOTO(Ii, a).
    Para cada estado i e item [A → α ·] com A ≠ S': ACTION[i,a] = reduce A → α
      para todo a ∈ FOLLOW(A).
    Para o item [S' → S ·]: ACTION[i,$] = accept.
    Para GOTO(Ii, A) = j com A não-terminal: GOTO[i,A] = j.
    Conflitos (shift/reduce ou reduce/reduce) indicam gramática não-SLR(1).

    Retorna (tabela_acao, tabela_goto, conflitos, prods_originais).
    """
    # não-terminais = todos os lados esquerdos das produções aumentadas
    nao_terminais = {esq for esq, _ in prods_aug}

    # descarta a produção aumentada S' → S; as demais são as produções originais
    # o índice aqui é o número da redução: r0, r1, r2, ...
    prods_originais = prods_aug[1:]

    tabela_acao = {}
    tabela_goto = {}
    conflitos = []

    def registrar_acao(chave, valor):
        # detecta conflito: shift/reduce ou reduce/reduce
        if chave in tabela_acao and tabela_acao[chave] != valor:
            conflitos.append(
                f"conflito em estado {chave[0]}, símbolo '{chave[1]}': "
                f"{tabela_acao[chave]} vs {valor}"
            )
        tabela_acao[chave] = valor

    # passo 2a e 3: percorre o goto_map construído pela coleção canônica
    for (i, X), j in goto_map.items():
        if X in nao_terminais:
            # passo 3: GOTO para não-terminais
            # ex: estado 0 --<E>--> estado 1   →   GOTO[0, <E>] = 1
            tabela_goto[(i, X)] = j
        else:
            # passo 2a: shift para terminais
            # ex: estado 0 --id--> estado 5   →   ACTION[0, id] = shift 5
            registrar_acao((i, X), ('shift', j))

    # passos 2b e 2c: percorre todos os itens com ponto no final
    for i, I in enumerate(colecao):
        for esq, dir, dot in I:
            # ponto no final significa que o corpo foi reconhecido
            if dot < len(dir):
                continue

            if esq == inicial_aug:
                # passo 2c: item [S' → S ·]  →  accept
                registrar_acao((i, '$'), ('accept',))
            else:
                # passo 2b: item [A → α ·]  →  reduce para todo símbolo em FOLLOW(A)
                # descobre qual é o índice da produção entre as originais
                prod = (esq, dir)
                idx = next(j for j, p in enumerate(prods_originais) if p == prod)
                for a in follow_sets.get(esq, set()):
                    # ex: FOLLOW(<E>) = {$, +}  →  ACTION[i, $] = r0,  ACTION[i, +] = r0
                    registrar_acao((i, a), ('reduce', idx))

    return tabela_acao, tabela_goto, conflitos, prods_originais
