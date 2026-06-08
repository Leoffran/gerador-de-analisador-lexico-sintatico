from automato import Automato

def remover_inalcancaveis(afd):
    """Remove os estados que não são alcançáveis"""
    alcancaveis = set()
    fila = [afd.start]

    # varre os estados
    while fila:
        # ao atingir o estado
        estado = fila.pop(0)
        # se já tiver sido alcançado: continua
        if estado in alcancaveis:
            continue
        # se não: adiciona aos alcançados
        alcancaveis.add(estado)
        # para cada símbolo do alfabeto
        for simbolo in afd.alfabeto:
            # transiciona por eles e pega os estados
            destino = afd.transicoes.get((estado, simbolo))
            # se o destino não havia sido alcançado antes: adiciona na
            if destino and destino not in alcancaveis:
                fila.append(destino)
    
    # filtra o que não é alcançável
    novos_estados = {e for e in afd.estados if e in alcancaveis}

    # limpa o dicionário dos estados de aceitação <lexema, nome padrão>
    nova_aceitacao = {e: v for e, v in afd.aceitacao.items() if e in alcancaveis}

    # limpa as transições
    novas_transicoes = {(e, s): d for (e, s), d in afd.transicoes.items() if e in alcancaveis and d in alcancaveis}

    # retorna o novo autômato sem estados inalcançáveis
    return Automato(novos_estados, afd.alfabeto, novas_transicoes, afd.start, nova_aceitacao)

def remover_mortos(afd):
    """Remove estados que nunca levam a um estado de aceitação"""
    # monta as transições inversas: {destino: [estados que chegam nele]}
    inversas = {}
    # para cada transição:
    for (estado, simbolo), destino in afd.transicoes.items():
        # se o destino não estiver no dicionário inverso: cria a lista
        if destino not in inversas:
            inversas[destino] = []
        # adiciona o estado na lista que chega no destino
        inversas[destino].append(estado)
    
    # começa pelos estados de aceitação:
    vivos = set(afd.aceitacao.keys())
    fila = list(vivos)

    while fila:
        estado = fila.pop(0)
        # verifica quais estados chegam nesse estado
        for origem in inversas.get(estado, []):
            # se o que chega ainda não estava na lista
            if origem not in vivos:
                # adiciona nos vivos
                vivos.add(origem)
                # adiciona na fila
                fila.append(origem)

    # filtra estados mortos
    novos_estados    = {e for e in afd.estados if e in vivos}
    
    # filtra as transições -> só pode se ambos os estados forem vivos
    novas_transicoes = {(e, s): d for (e, s), d in afd.transicoes.items() if e in vivos and d in vivos}
    
    return Automato(novos_estados, afd.alfabeto, novas_transicoes, afd.start, afd.aceitacao)