def ler_gramatica(caminho):
    """Lê o arquivo de gramática e retorna a quádrupla"""
    # G = (producoes, nao_terminais, terminais, inicial)
    
    producoes = []
    nao_terminais = set()
    terminais = set()

    with open(caminho) as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue

            # separa lado esquerdo do direito pelo ::=
            esq, _, dir = linha.partition('::=')
            esq = esq.strip()
            dir = dir.strip()

            # esquerdo é sempre um não-terminal
            nao_terminais.add(esq)

            # separa as alternativas pelo |
            alternativas = dir.split('|')
            for alt in alternativas:
                # separa os símbolos por espaço
                simbolos = alt.strip().split()
                producoes.append((esq, simbolos))
    
    # terminais são os símbolos que não são não terminais
    for _, simbolos in producoes:
        for s in simbolos:
            if s not in nao_terminais:
                terminais.add(s)
    
    # símbolo inicial é o lado esquerdo da primeira produção
    inicial = producoes[0][0]

    return producoes, nao_terminais, terminais, inicial