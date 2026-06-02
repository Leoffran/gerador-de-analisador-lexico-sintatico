from enum import Enum, auto
from typing import Optional
from copy import deepcopy
from no import NoChar, NoConcat, NoFecho, NoUniao

# Leitura do arquivo
def ler_definicoes(caminho):
    """Lê o arquivo e retorna uma lista de pares (nome, expressão regular)"""
    defs = []
    # abre o arquivo e pega as informações das linhas
    with open(caminho) as f:
        for linha in f:
            linha = linha.strip()
            # pula linhas vazias e comentários
            if not linha or linha.startswith('#'):
                continue
            # pega o nome e a expressão
            nome, _, er = linha.partition(':')
            # adiciona os pares (nome, expressão regular) à lista
            defs.append((nome.strip(), er.strip()))
    return defs

# Expansão de classes
def expandir_classe(conteudo):
    """[a-zA-Z0-9] -> (a|b|...|z|A|...|Z|0|...|9)"""
    chars = []
    i = 0
    while i < len(conteudo):
        # verifica se há um intervalo, ex: a-z (2 caracteres à frente)
        if i + 2 < len(conteudo) and conteudo[i + 1] == '-':
            # converte o início e fim do intervalo pra inteiro ASCII
            inicio = ord(conteudo[i])
            fim = ord(conteudo[i + 2])
            # gera todos os elementos do intervalo e adiciona à lista
            chars.extend(chr(c) for c in range(inicio, fim + 1))
            i += 3 # avança
        # se não houver intervalo, adiciona o elemento
        else:
            chars.append(conteudo[i])
            i += 1
    return '(' + '|'.join(chars) + ')'

def preprocessar(er):
    """Lê a string inteira e chama o expandir_classe() lendo somente o conteúdo"""
    # ex: acha [a-zA-Z] → chama expandir_classe("a-zA-Z")
    resultado = ''
    i = 0
    # percorre a expressão
    while i < len(er):
        # se acha o [
        if er[i] == '[':
            # encontra o ] correspondente e varre o conteúdo entre eles
            j = er.index(']', i)
            resultado += expandir_classe(er[i + 1:j])
            i = j + 1
        # caso contrário:
        else:
            # adiciona o elemento
            resultado += er[i]
            i += 1
    return resultado

# Tokenizador
class TipoToken(Enum):
    """Tipos possíves de token em uma expressão regular"""
    CHAR     = auto() # caractere
    FECHO    = auto() # *
    MAIS     = auto() # + (fecho positivo)
    OPCIONAL = auto() # ?
    OU       = auto() # |
    ABRE     = auto() # (
    FECHA    = auto() # )
    CONCAT   = auto() # .

OPERADORES = {
    '*': TipoToken.FECHO,
    '+': TipoToken.MAIS,
    '?': TipoToken.OPCIONAL,
    '|': TipoToken.OU,
    '(': TipoToken.ABRE,
    ')': TipoToken.FECHA,
}

@dataclass
class Token:
    tipo:  TipoToken # tipo = char precisa guardar o valor desse char
    # Optional[str] é equivalente a str | None
    valor: Optional[str] = None

def tokenizar(er):
    """Converte a ER em uma lista de tokens"""
    tokens = []
    # Para cada char na expressão regular
    for ch in er:
        # se for um operador adiciona aos tokens
        if ch in OPERADORES:
            tokens.append(Token(OPERADORES[ch]))
        # se for épsilon adiciona aos tokens
        elif ch == '&':
            tokens.append(Token(TipoToken.CHAR, '&'))
        # se for qualquer outro char, adiciona aos tokens
        elif ch != ' ':
            tokens.append(Token(TipoToken.CHAR, ch))
    return tokens

def inserir_concat(tokens):
    """Insere tokens de concatenação entre os tokens da ER"""
    # insere . quando o token atual é CHAR, FECHO, MAIS, OPCIONAL ou FECHA
    # e o próximo é CHAR ou ABRE
    resultado = []
    for i, tok in enumerate(tokens):
        resultado.append(tok) # adiciona o token atual

        if i + 1 < len(tokens): # se ainda tem próximo token
            prox = tokens[i + 1]
            # lado esquerdo
            esq_ok = tok.tipo in {
                TipoToken.CHAR,
                TipoToken.FECHO,
                TipoToken.MAIS,
                TipoToken.OPCIONAL,
                TipoToken.FECHA
            }
            # lado direito
            dir_ok = prox.tipo in {
                TipoToken.CHAR,
                TipoToken.ABRE
            }
            # se seguir a regra: insere o .
            if esq_ok and dir_ok:
                resultado.append(Token(TipoToken.CONCAT))
    return resultado

# Parser
class Parser:
    """Constrói a árvore a partir da lista de tokens"""
    def __init__(self, tokens):
        """Construtor"""
        self.tokens = tokens
        self.pos = 0 # posição do token que tá sendo lido
    
    def _peek(self):
        """Retorna o token atual"""
        # serve pra garantir que não vai dar erro se já tiver lido todos
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None # retorna None se chega no final da lista
    
    def _consumir(self, tipo=None):
        """Consome o token atual"""
        # se passar tipo como argumento, só consome se o tipo for igual
        tok = self.tokens[self.pos]
        # se estiver esperando um tipo de token (ex: CHAR) e receber outro, retorna erro
        if tipo and tok.tipo != tipo:
            raise SyntaxError(f"Esperado {tipo}, encontrado {tok.tipo}")
        self.pos += 1 # avança
        return tok
    
    def parse(self):
        """Ponto de entrada do parser"""
        return self._expr()
    
    def _expr(self):
        """Cria nós de união"""
        # ex: [CHAR'a', OU, CHAR'b', OU, CHAR'c'] ->
        # NoUniao(NoUniao(NoChar('a'), NoChar('b')), NoChar('c'))
        no = self._termo()
        # enquanto o próximo token for | continua lendo
        while self._peek() and self._peek().tipo == TipoToken.OU:
            self._consumir(TipoToken.OU) # consome o |
            no = NoUniao(no, self._termo()) # consome e lê o próximo termo
        return no
    
    def _termo(self):
        """Cria nós de contactenação"""
        # ex: a·b·c -> NoConcat(NoConcat(a, b), c)
        no = self._fator()
        # enquanto o próximo token for . continua lendo
        while self._peek() and self._peek().tipo == TipoToken.CONCAT:
            self._consumir(TipoToken.CONCAT) # consome o .
            no = NoConcat(no, self._fator()) # consome e lê o próximo fator
        return no
    
    def _fator(self):
        """Trata operadores unários"""
        # lê um operando e verifica se há algum operador unário após ele
        # (* + ?). se não houver, retorna o operando sem modificar
        no = self._base()
        peek = self._peek()

        if peek and peek.tipo == TipoToken.FECHO:
            self._consumir() # consome o *
            return NoFecho(no)

        if peek and peek.tipo == TipoToken.MAIS:
            self._consumir() # consome o +
            # a+ = a . a*
            # usa deepcopy pra criar um novo objeto
            return NoConcat(no, NoFecho(deepcopy(no)))
        
        if peek and peek.tipo == TipoToken.OPCIONAL:
            self._consumir() # consome o ?
            # a? = (a | &)
            return NoUniao(no, NoChar('&'))
        return no
    
    def _base(self):
        """Trata os símbolos das folhas"""
        # transforma os símbolos em folhas da árvore
        # grupo entre parênteses -> trata e descarta os parênteses
        tok = self._peek()

        # símbolo literal
        if tok.tipo == TipoToken.CHAR:
            self._consumir() # consome o caractere
            return NoChar(tok.valor) # cria a folha (ex: 'a' -> NoChar('a'))
        
        # grupo entre parênteses
        if tok.tipo == TipoToken.ABRE:
            self._consumir(TipoToken.ABRE)
            no = self._expr() # processa o grupo
            self._consumir(TipoToken.FECHA)
            return no
        # ex: * ou ) aparecendo onde não deveria
        raise SyntaxError(f"Token inesperado: {tok}")
    
def parsear_er(er):
    """Ponto de entrada, função que é chamada"""
    
    # expande [a-zA-Z] -> (a|...|z|A|...|Z)
    er_prep = preprocessar(er)

    # converte cada caractere da ER em um Token
    # ex: "a(a|b)*" -> [Token(CHAR,'a'), Token(ABRE), ...]
    tokens = tokenizar(er_prep)

    # insere . onde há concatenação implícita
    # ex: [CHAR'a', ABRE, ...] → [CHAR'a', CONCAT, ABRE, ...]
    tokens = inserir_concat(tokens)

    # monta a árvore e devolve a raiz
    return Parser(tokens).parse()