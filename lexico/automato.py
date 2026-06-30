class Automato:
    def __init__(self, estados, alfabeto, transicoes, start, aceitacao):
        """Construtor do autômato"""
        self.estados = estados
        self.alfabeto = alfabeto
        self.transicoes = transicoes
        self.start = start
        self.aceitacao = aceitacao

    def __repr__(self):
        """Retorna uma string com a quíntupla do autômato"""
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"Automato({attrs})"