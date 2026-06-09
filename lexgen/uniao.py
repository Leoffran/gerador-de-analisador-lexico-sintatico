from automato import Automato

def uniao(*afds):
    """Une AFDs via e-transição, gerando um AFND"""

    todos_estados = set()
    todas_transicoes = {}
    toda_aceitacao = {}
    inicios_afds = []

    # offset garante que estados de AFDs diferentes não colidem
    # ex: AFD1={0,1,2}, AFD2={0,1}
    # sem offset: estado 0 existe nos dois
    # com offset: AFD1={0,1,2}, AFD2={3,4} → sem colisão
    offset = 0

    for afd in afds:
        # renomeia cada estado somando o offset
        for estado in afd.estados:
            todos_estados.add(estado + offset)

        # renomeia as transições
        # ex: (0, 'a') -> 1  vira  (0+offset, 'a') -> {1+offset}
        for (estado, simbolo), destino in afd.transicoes.items():
            todas_transicoes[(estado + offset, simbolo)] = {destino + offset}
        
        # renomeia os estados de aceitação
        for estado, padrao in afd.aceitacao.items():
            toda_aceitacao[estado + offset] = padrao

        # guarda o estado inicial desse AFD 
        inicios_afds.append(afd.start + offset)

        # avança o offset pelo número de estados do AFD
        offset += len(afd.estados)

    # novo estado inicial
    novo_inicio = offset
    todos_estados.add(novo_inicio)

    # e-transições do novo estado inicial para o inicial de cada AFD
    todas_transicoes[(novo_inicio, '&')] = set(inicios_afds)

    # junta todos os alfabetos dos AFDs
    alfabeto = set()
    for afd in afds:
        alfabeto |= afd.alfabeto # união
    
    return Automato(todos_estados, alfabeto, todas_transicoes, novo_inicio, toda_aceitacao)