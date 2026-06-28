from automato import Automato

def epsilon_fecho(estados, transicoes):
    """Retorna todos os estados alcançáveis por e-transições"""
    fecho = set(estados)
    fila = list(estados)

    while fila:
        estado = fila.pop()
        # pega todos os estados alcançáveis por e-transições desse estado
        destinos = transicoes.get((estado, '&'), set())
        for destino in destinos:
            # se o destino não estiver no fecho
            if destino not in fecho:
                # adiciona
                fecho.add(destino)
                # adiciona na fila pra verificar se ele possui e-transições também
                fila.append(destino)

    return frozenset(fecho)

def determinizar(afnd):
    """Converte um AFND em AFD usando construção de subconjuntos"""

    # estado inicial = e-fecho do estado inicial do AFND
    estado_inicial = epsilon_fecho({afnd.start}, afnd.transicoes)

    estados = set()
    transicoes = {}
    aceitacao = {}
    fila = [estado_inicial]
    visitados = set()

    while fila:
        estado_atual = fila.pop(0)

        # se o estado atual já foi visitado: pula
        if estado_atual in visitados:
            continue
        
        # adiciona o estado
        visitados.add(estado_atual)
        estados.add(estado_atual)

        # verifica se o estado é de aceitação; menor ID = padrão definido primeiro (prioridade)
        aceitando = [e for e in estado_atual if e in afnd.aceitacao]
        if aceitando:
            aceitacao[estado_atual] = afnd.aceitacao[min(aceitando)]
        
        # calcula transições para cada símbolo
        for simbolo in afnd.alfabeto:
            if simbolo == '&':
                continue # ignora
                
            # pega todos os destinos dos estados do conjunto atual
            destinos = set()
            for estado in estado_atual:
                for d in afnd.transicoes.get((estado, simbolo), set()):
                    destinos.add(d)

            if not destinos:
                continue

            # calcula o e-fecho do resultado
            proximo = epsilon_fecho(destinos, afnd.transicoes)
            transicoes[(estado_atual, simbolo)] = proximo

            if proximo not in visitados:
                fila.append(proximo)

    # renomeia os estados para inteiros
    estado_para_id = {e: i for i, e in enumerate(estados)}

    novo_inicio      = estado_para_id[estado_inicial]
    novos_estados    = set(estado_para_id.values())
    nova_aceitacao   = {estado_para_id[e]: v for e, v in aceitacao.items()}
    novas_transicoes = {(estado_para_id[e], s): estado_para_id[d]
                        for (e, s), d in transicoes.items()}

    return Automato(novos_estados, afnd.alfabeto - {'&'}, novas_transicoes, novo_inicio, nova_aceitacao)