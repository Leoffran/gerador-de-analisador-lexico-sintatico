def _parsear_linhas(linhas):
    producoes = []
    nao_terminais = set()

    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.startswith('#'):
            continue

        esq, _, dir = linha.partition('::=')
        esq = esq.strip()
        dir = dir.strip()

        nao_terminais.add(esq)

        for alt in dir.split('|'):
            simbolos = alt.strip().split()
            producoes.append((esq, simbolos))

    terminais = set()
    for _, simbolos in producoes:
        for s in simbolos:
            if s not in nao_terminais and s != '&':
                terminais.add(s)

    inicial = producoes[0][0]
    return producoes, nao_terminais, terminais, inicial


def ler_gramatica(caminho):
    with open(caminho) as f:
        return _parsear_linhas(f)


def ler_gramatica_texto(texto):
    return _parsear_linhas(texto.splitlines())