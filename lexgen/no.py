from dataclasses import dataclass

# Nós da árvore
class No:
    pass

@dataclass
class NoChar(No):
    char: str
    pos: int = 0 # numerado pelo aho

@dataclass
class NoConcat(No):
    esq: No
    dir: No

@dataclass
class NoUniao(No):
    esq: No
    dir: No

@dataclass
class NoFecho(No):
    filho: No