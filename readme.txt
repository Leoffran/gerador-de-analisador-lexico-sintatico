Para usar o programa execute main.py a partir da raiz do projeto: python3 main.py

A interface abre com três abas: Projeto Léxico, Projeto Sintático, Execução.

FORMATO DOS ARQUIVOS DE ENTRADA

Arquivo de definições léxicas (.er):

    nome: expressão_regular

Operadores de ER suportados:
    *        fecho de Kleene
    +        fecho positivo (um ou mais)
    ?        opcional (zero ou um)
    |        alternância
    ( )      agrupamento
    [a-z]    classe de caracteres
    &        épsilon
    \x       caractere literal x (útil para escapar operadores:
             \+ \* \? \| \( \) )

Arquivo de gramática (.g):

    <NaoTerminal> ::= <Corpo da producao>

Cada linha é uma produção. Alternativas na mesma linha separadas por |.
Símbolos separados por espaço. Não-terminais entre < >.
Os terminais devem corresponder aos nomes definidos no arquivo .er.

Arquivo .g com palavras reservadas (seções opcionais):

    [keywords]
    for
    while

    [grammar]
    <S> ::= ...
