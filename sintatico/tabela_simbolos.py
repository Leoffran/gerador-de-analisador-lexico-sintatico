class TabelaSimbolos:
    """Tabela de símbolos com suporte a palavras reservadas.

    Palavras reservadas retornam (lexema, 'PR').
    Novos identificadores são inseridos e retornam (lexema, linha).
    """

    def __init__(self, palavras_reservadas=None):
        self._pr = set(palavras_reservadas or [])
        self._tabela = {}
        self._contador = 1

    def buscar_ou_inserir(self, lexema):
        if lexema in self._pr:
            return (lexema, 'PR')
        if lexema not in self._tabela:
            self._tabela[lexema] = self._contador
            self._contador += 1
        return (lexema, self._tabela[lexema])

    def __repr__(self):
        return f"TabelaSimbolos(PR={self._pr}, ids={self._tabela})"
