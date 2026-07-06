from automato import Automato

def lexer(afd, texto):
    """Tokeniza o texto fonte usando o AFD final (regra do maximal munch)."""
    # Retorna uma lista de tuplas <Lexema, Nome Padrão> ou <Lexema, 'erro!'>
    tokens = []
    i = 0
    n = len(texto)

    while i < n:
        ch = texto[i]

        # espaços e quebras de linha só separam tokens, não fazem parte de nenhum
        if ch in ' \n\t':
            i += 1
            continue

        # tenta casar o maior prefixo possível a partir de i (maximal munch)
        estado = afd.start
        j = i
        pos_aceite = None      # última posição em que o AFD passou por aceitação
        padrao_aceite = None

        while j < n and texto[j] not in ' \n\t':
            proximo = afd.transicoes.get((estado, texto[j]))
            if proximo is None:
                break
            estado = proximo
            j += 1
            if estado in afd.aceitacao:
                # atualiza o melhor casamento visto até agora
                pos_aceite = j
                padrao_aceite = afd.aceitacao[estado]

        if pos_aceite is not None:
            # emite o maior lexema aceito e retoma a busca a partir dele
            tokens.append((texto[i:pos_aceite], padrao_aceite))
            i = pos_aceite
        elif j > i:
            # consumiu caracteres válidos no AFD, mas nunca passou por aceitação
            tokens.append((texto[i:j], 'erro!'))
            i = j
        else:
            # nem o primeiro caractere tem transição válida
            tokens.append((texto[i], 'erro!'))
            i += 1

    return tokens