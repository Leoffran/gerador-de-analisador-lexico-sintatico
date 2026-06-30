def _parsear_linhas(linhas):
    producoes = []
    nao_terminais = set()

    for linha in linhas:
        linha = linha.strip()
        # pula linhas vazias e comentários
        if not linha or linha.startswith('#'):
            continue

        # divide pelo ::= para separar o lado esquerdo do direito
        # ex: "<E> ::= <E> + <T> | <T>"  ->  esq="<E>", dir="<E> + <T> | <T>"
        esq, _, dir = linha.partition('::=')
        esq = esq.strip()
        dir = dir.strip()

        # o lado esquerdo sempre é um não-terminal
        nao_terminais.add(esq)

        # alternativas na mesma linha separadas por |
        # ex: "<E> + <T> | <T>"  ->  ["<E> + <T>", "<T>"]
        for alt in dir.split('|'):
            # cada alternativa vira uma lista de símbolos separados por espaço
            # ex: "<E> + <T>"  ->  ["<E>", "+", "<T>"]
            simbolos = alt.strip().split()
            producoes.append((esq, simbolos))

    # terminais = tudo que aparece no lado direito e não é não-terminal
    terminais = set()
    for _, simbolos in producoes:
        for s in simbolos:
            if s not in nao_terminais and s != '&':
                terminais.add(s)

    # o símbolo inicial é o lado esquerdo da primeira produção
    inicial = producoes[0][0]
    return producoes, nao_terminais, terminais, inicial


def ler_gramatica(caminho):
    """Lê a gramática de um arquivo e retorna (producoes, nao_terminais, terminais, inicial)"""
    with open(caminho) as f:
        return _parsear_linhas(f)


def ler_gramatica_texto(texto):
    """Lê a gramática de uma string e retorna (producoes, nao_terminais, terminais, inicial)"""
    return _parsear_linhas(texto.splitlines())
