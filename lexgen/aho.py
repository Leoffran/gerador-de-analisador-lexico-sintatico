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
    