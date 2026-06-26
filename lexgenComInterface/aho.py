from no import NoChar, NoConcat, NoUniao, NoFecho
from automato import Automato

def aumentar_er(ast):
    """"Concatena # no final da ER"""
    return NoConcat(ast, NoChar('#'))

class Contador:
    """"Contador pra numerar as posições dos nós char"""
    def __init__(self):
        self.valor = 0

def numerar_posicoes(no, contador = None):
    """"Percorre uma árvore e numera cada folha NoChar com uma posição"""
    # ex: ab*# -> NoChar('a') pos=1, NoChar('b') pos=2, NoChar('#') pos=3
    # começa pelo nó raiz e vai chamando recursivamente
    if contador is None:
        # se não houver contador -> cria um contador
        contador = Contador()
    if isinstance(no, NoChar):
        # se for um char, avança o contador e define a posição
        contador.valor += 1
        no.pos = contador.valor
    elif isinstance(no, NoFecho):
        # se for um nó fecho, chama o filho
        numerar_posicoes(no.filho, contador)
    elif isinstance(no, (NoConcat, NoUniao)):
        # se for concat ou união, chama primeiro o filho da esquerda
        numerar_posicoes(no.esq, contador)
        numerar_posicoes(no.dir, contador)
    return contador.valor # retorna o número de nós da árvore

def nullable(no):
    """Verifica se o nó pode gerar a palavra vazia"""
    if isinstance(no, NoChar):
        # o char só é anulável se for épslon
        return no.char == '&'
    if isinstance(no, NoFecho):
        # a* pode gerar épslon
        return True
    if isinstance(no, NoUniao):
        # se for união, é anulável se:
        # ou o da direita ou o da esquerda forem anuláveis
        return nullable(no.esq) or nullable(no.dir)
    if isinstance(no, NoConcat):
        # concatenação só é anulável se:
        # os dois nós forem anuláveis
        return nullable(no.esq) and nullable(no.dir)
    
def firstpos(no):
    """Retorna o conjunto de posições que podem ser a primeira de uma palavra"""
    if isinstance(no, NoChar):
        # se for um char, retorna sua posição "caso base"
        # NoChar('a') pos=1  ->  firstpos = {1}
        return {no.pos} # retorna um set pra garantir que não há repetição

    if isinstance(no, NoFecho):
        # se for nó fecho, retorna firstpos do filho
        # ex: a* -> NoFecho(NoChar('a') pos=1)
        # firstpos = firstpos(NoChar('a')) = {1}
        return firstpos(no.filho)
    
    if isinstance(no, NoUniao):
        # se for nó união, retorna a união dos firstpos dos filhos
        # ex a|b -> NoUniao(NoChar('a') pos=1, NoChar('b') pos=2)
        # firstpos = firstpos(a) ∪ firstpos(b) = {1} ∪ {2} = {1, 2}
        return firstpos(no.esq) | firstpos(no.dir)
    
    if isinstance(no, NoConcat):
        # se for um nó concat:
        # se o esquerdo for anulável, o da direita também pode ser o primeiro
        if nullable(no.esq):
            return firstpos(no.esq) | firstpos(no.dir)
        else:
            # caso contrário só o esquerdo pode ser o primeiro
            return firstpos(no.esq)
        
def lastpos(no):
    """Retorna o conjunto de posições que podem ser a última de uma palavra"""
    if isinstance(no, NoChar):
        # se for um char, retorna sua posição "caso base"
        return {no.pos}
    
    if isinstance(no, NoFecho):
        # se for nó fecho, retorna o lastpos do filho
        return lastpos(no.filho)
    
    if isinstance(no, NoUniao):
        # se for nó união, retorna a união do lastpos dos filhos
        return lastpos(no.esq) | lastpos(no.dir)
    
    if isinstance(no, NoConcat):
        # se for um nó concat:
        # se o da direita for anulável, o da esquerda também pode ser o último
        if nullable(no.dir):
            return lastpos(no.esq) | lastpos(no.dir)
        else:
            # caso contrário, só o da direita pode ser o último
            return lastpos(no.dir)

def followpos(no, tabela):
    """Preenche a tabela de followpos para cada posição"""
    # tabela = {pos: set de posições que podem vir depois}
    if isinstance(no, NoChar):
        return # caso base -> folha não gera followpos
    
    if isinstance(no, NoConcat):
        # todos que terminam no esquerdo podem ser seguidos pelo primeiro do direito
        for p in lastpos(no.esq):
            # concatena
            tabela[p] |= firstpos(no.dir)
        # desce nos filhos
        followpos(no.esq, tabela)
        followpos(no.dir, tabela)
    
    if isinstance(no, NoFecho):
        # quem termina no fecho pode ser seguido pelo primeiro do fecho
        for p in lastpos(no.filho):
            # concatena
            tabela[p] |= firstpos(no.filho)
        # desce no filho
        followpos(no.filho, tabela)

    if isinstance(no, NoUniao):
        # união não gera followpos
        # segue para os filhos:
        followpos(no.esq, tabela)
        followpos(no.dir, tabela)

def calcular_followpos(ast, num_posicoes):
    """Inicializa a tabela e chama followpos"""
    # num_posicoes = número total de folhas da árvore (precisa saber pra criar a tabela)
    # cada posição começa com um set vazio
    tabela = {i: set() for i in range(1, num_posicoes + 1)}
    followpos(ast, tabela) # preenche a tabela
    return tabela

def mapear_posicoes(no, mapa=None):
    """Retorna um dicionário {pos: símbolo} para cada folha da árvore"""
    # se não houver um mapa, cria
    if mapa is None:
        mapa = {}
    # se o nó for um char, mapeia
    if isinstance(no, NoChar):
        mapa[no.pos] = no.char
    
    # se não: mapeia recursivamente os filhos
    elif isinstance(no, NoFecho):
        mapear_posicoes(no.filho, mapa)
    elif isinstance(no, (NoConcat, NoUniao)):
        mapear_posicoes(no.esq, mapa)
        mapear_posicoes(no.dir, mapa)
    return mapa

def construir_afd(ast, nome_padrao):
    """Constrói o AFD a partir da AST usando algoritmo de Aho"""
    # nome_padrao é o nome da ER

    # prepara a árvore:
    # concatena # no final da ER
    ast = aumentar_er(ast)
    # percorre a árvore e numera cada folha
    num_pos = numerar_posicoes(ast)
    # percorre a árvore e cria um dicionário {posição : símbolo}
    mapa = mapear_posicoes(ast)
    # calcula o followpos de todos os elementos da árvore
    tabela_fp = calcular_followpos(ast, num_pos)

    # posição do '#' é a última
    pos_hash = num_pos

    # percorre o dicionário pra pegar todas as letras do alfabeto
    alfabeto = {mapa[p] for p in mapa if mapa[p] != '#'}

    # estado inicial = firstpos da raiz
    # como set() não pode ser utilizado como chave do dicionário:
    # é preciso utilizar frozenset(), que funciona da mesma maneira
    # mas não pode ser modificado após ser criado
    estado_inicial = frozenset(firstpos(ast))

    # estrutura do AFD
    visitados = set()
    estados = set()
    transicoes = {}
    aceitacao = {}

    fila = [estado_inicial]

    while fila:
        # pega o próximo estado a processar
        estado_atual = fila.pop(0)

        # se ele já foi visitado, pula
        if estado_atual in visitados:
            continue
        
        # adiciona aos estados visitados
        visitados.add(estado_atual)
        estados.add(estado_atual)

        # se o estado contém '#' -> é de aceitação
        if pos_hash in estado_atual:
            # para formar <lexema, nome padrão>
            aceitacao[estado_atual] = nome_padrao
        
        # calcula as transições para cada símbolo do alfabeto
        for simbolo in alfabeto:
            # filtra as posições do estado atual que tem o símbolo atual
            posicoes = {p for p in estado_atual if mapa[p] == simbolo}

            # sem transição
            if not posicoes:
                continue

            # próximo estado = união dos followpos dessas posições
            proximo = frozenset(p for pos in posicoes for p in tabela_fp[pos])
            
            # guarda a transição
            transicoes[(estado_atual, simbolo)] = proximo

            # adiciona na fila
            if proximo not in visitados:
                fila.append(proximo)
    
    return Automato(estados, alfabeto, transicoes, estado_inicial, aceitacao)