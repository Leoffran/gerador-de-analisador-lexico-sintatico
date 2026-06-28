def parsear(tokens, tabela_acao, tabela_goto, producoes):
    """Algoritmo LR com pilha de estados (slide p.53/56, alg. 4.44).

    tokens    — lista de (lexema, padrao) do analisador léxico
    producoes — lista de (esq, dir_tupla) sem a produção aumentada

    Retorna (passos: list[str], erro: str | None).
    passos lista cada ação tomada; erro é None se aceito.
    """
    pilha_estados = [0]
    pilha_simbolos = []
    passos = []

    entrada = [padrao for _, padrao in tokens] + ['$']
    pos = 0

    while True:
        s = pilha_estados[-1]
        a = entrada[pos]

        if (s, a) not in tabela_acao:
            erro = f"Erro sintático: símbolo inesperado '{a}' no estado {s}"
            return passos, erro

        acao = tabela_acao[(s, a)]

        if acao[0] == 'shift':
            _, t = acao
            pilha_estados.append(t)
            pilha_simbolos.append(a)
            pos += 1
            passos.append(f"shift  {a!r:15} → estado {t}")

        elif acao[0] == 'reduce':
            _, idx = acao
            esq, dir = producoes[idx]
            n = len(dir)
            if n > 0:
                pilha_estados = pilha_estados[:-n]
                pilha_simbolos = pilha_simbolos[:-n]
            t = pilha_estados[-1]
            proximo = tabela_goto.get((t, esq))
            if proximo is None:
                return passos, f"Erro: GOTO({t}, {esq}) indefinido"
            pilha_estados.append(proximo)
            pilha_simbolos.append(esq)
            corpo = ' '.join(dir) if dir else 'ε'
            passos.append(f"reduce {esq} ::= {corpo}")

        elif acao[0] == 'accept':
            passos.append("aceito")
            return passos, None
