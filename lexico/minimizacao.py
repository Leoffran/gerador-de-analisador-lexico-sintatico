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

def hopcroft(afd):
    """Minimiza o AFD usando o algoritmo de Hopcroft"""
    
    # partição inicial: aceitação e não aceitação
    aceitacao = frozenset(afd.aceitacao.keys())
    nao_aceitacao = frozenset(afd.estados - aceitacao)

    # particoes iniciais -> filtra caso todos ou nenhum estado seja de aceitação
    particoes = set()
    if aceitacao:
        particoes.add(aceitacao)
    if nao_aceitacao:
        particoes.add(nao_aceitacao)

    fila = list(particoes)

    while fila:
        # pega a próxima partição
        particao_atual = fila.pop(0)
        
        for simbolo in afd.alfabeto:
            # para cada símbolo, descobre quais estados chegaram na partição atual
            antecessores = frozenset(
                e for e in afd.estados if afd.transicoes.get((e, simbolo)) in particao_atual
            )
        
            # se nenhum estado chega na particao_atual com esse simbolo: pula
            if not antecessores:
                continue

            novas_particoes = set()
            for particao in particoes:
                # tenta dividir essa particao em dois grupos

                # grupo 1: estados que chegam na posição_atual com esse símbolo
                dentro = particao & antecessores

                # grupo 2: estados que não chegam na posição_atual com esse símbolo
                fora = particao - antecessores

                # se um dos grupos for vazio: todos se comportam igual, 
                # mantém a partição como está
                if not dentro or not fora:
                    novas_particoes.add(particao)
                    continue

                # se os dois grupos não são vazios: comportamentos diferentes:
                # divide em duas
                novas_particoes.add(dentro)
                novas_particoes.add(fora)

                # atualiza a fila
                if particao in fila:
                    # se a partição já estava na fila:
                    # remove e coloca as duas novas no lugar
                    fila.remove(particao)
                    fila.append(dentro)
                    fila.append(fora)
                else:
                    # se não estava na fila
                    # adiciona só a menor das duas - otimização
                    # processar a menor garante complexidade O(n log n)
                    fila.append(dentro if len(dentro) <= len(fora) else fora)
            
            # atualiza as partições
            particoes = novas_particoes

    return particoes

def construir_afd_minimo(afd, particoes):
    """Converte as partições do Hopcroft em um novo Autômato minimizado"""

    # mapeia cada partição para um inteiro
    # ex: frozenset({1,2,3}) -> 0, frozenset({1,2,3,4}) -> 1, ...

    def encontrar_particao(estado):
        """Função auxiliar - acha qual partição contém um estado"""
        # ex: particoes = {{D}{E}, {C}, {B}, {A}} 
        # encontrar_particao({D}) = {D}{E}
        for particao in particoes:
            if estado in particao:
                return particao
        return None
    
    # novo estado inicial = partição que contém o estado inicial original
    novo_inicio = encontrar_particao(afd.start)

    # monta as novas transições
    novas_transicoes = {}
    for particao in particoes:
        # pega qualquer estado da partição como representante
        representante = next(iter(particao))
        for simbolo in afd.alfabeto:
            destino = afd.transicoes.get((representante, simbolo))
            if destino:
                # transição vai para a partição que contém o destino
                novas_transicoes[(particao, simbolo)] = encontrar_particao(destino)
    
    # monta os novos estados de aceitação
    nova_aceitacao = {}
    for particao in particoes:
        for estado in particao:
            if estado in afd.aceitacao:
                nova_aceitacao[particao] = afd.aceitacao[estado]
                # não precisa verificar os outros estados da mesma partição,
                # se um for de aceitação os outros são também
                break

    # renomeia as partições para inteiros
    particao_para_id = {particao: i for i, particao in enumerate(particoes)}

    novo_inicio      = particao_para_id[novo_inicio]
    novos_estados    = set(particao_para_id.values())
    nova_aceitacao   = {particao_para_id[p]: v for p, v in nova_aceitacao.items()}
    novas_transicoes = {(particao_para_id[e], s): particao_para_id[d]
                        for (e, s), d in novas_transicoes.items()}

    return Automato(novos_estados, afd.alfabeto, novas_transicoes, novo_inicio, nova_aceitacao)

def minimizar(afd):
    """Remove estados inúteis e minimiza o AFD"""
    afd = remover_inalcancaveis(afd)
    afd = remover_mortos(afd)
    particoes = hopcroft(afd)
    return construir_afd_minimo(afd, particoes)