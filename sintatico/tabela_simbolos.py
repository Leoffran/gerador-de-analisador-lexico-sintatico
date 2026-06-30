class TabelaSimbolos:
    """Tabela de símbolos com suporte a palavras reservadas.

    Palavras reservadas retornam (lexema, 'PR').
    Novos identificadores são inseridos e retornam (lexema, linha).
    """

    def __init__(self, palavras_reservadas=None):
        # palavras reservadas ficam num set para busca em O(1)
        self._pr = set(palavras_reservadas or [])
        # tabela de identificadores: {lexema: número da linha}
        self._tabela = {}
        self._contador = 1  # começa na linha 1

    def buscar_ou_inserir(self, lexema):
        # se for palavra reservada: retorna PR, sem inserir na tabela
        # ex: buscar_ou_inserir("for")  ->  ("for", "PR")
        if lexema in self._pr:
            return (lexema, 'PR')

        # se o identificador já foi visto antes: retorna a linha existente
        # se for novo: insere e atribui a próxima linha disponível
        # ex: primeira vez que aparece "x"  ->  ("x", 1)
        #     segunda vez que aparece "x"   ->  ("x", 1)  (mesmo número)
        if lexema not in self._tabela:
            self._tabela[lexema] = self._contador
            self._contador += 1
        return (lexema, self._tabela[lexema])

    def __repr__(self):
        return f"TabelaSimbolos(PR={self._pr}, ids={self._tabela})"
