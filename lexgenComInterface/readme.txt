Para usar o programa execute main.py (a partir do diretório lexgenComInterface):

    python3 main.py


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALISADOR LÉXICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

────────────────────────────────────────────────────────
Exemplo 1 — identificadores e números (testes/exemplo1.er)
────────────────────────────────────────────────────────
Definições (exemplo1.er):
    id:  [a-zA-Z]([a-zA-Z]|[0-9])*
    num: [1-9]([0-9])* | 0

Entrada (exemplo1.txt):      Saída esperada:
    a1                           <a1, id>
    0                            <0, num>
    teste2                       <teste2, id>
    21                           <21, num>
    alpha123                     <alpha123, id>
    3444                         <3444, num>
    a43teste                     <a43teste, id>

────────────────────────────────────────────────────────
Exemplo 2 — padrões sobrepostos er1/er2 (testes/exemplo2.er)
────────────────────────────────────────────────────────
Definições (exemplo2.er):
    er1: a?(a|b)+
    er2: b?(a|b)+

Entrada (exemplo2.txt):      Saída real da implementação:
    aa                           <aa, er1>
    bbbba                        <bbbba, er1>
    ababab                       <ababab, er1>
    bbbbb                        <bbbbb, er1>

Nota: er1 e er2 aceitam exatamente a mesma linguagem
(toda string não-vazia sobre {a,b}). Por isso o DFA não
consegue distinguir qual padrão "deveria" vencer — ambos
chegam ao mesmo estado de aceitação para qualquer entrada.
A regra adotada é "primeiro definido vence" (padrão de
lexers como Flex/Lex), logo er1 sempre ganha.
O PDF do enunciado apresenta uma saída pedagogicamente
motivada que não é reproduzível com um lexer baseado em DFA.

────────────────────────────────────────────────────────
Exemplo 3 — desempate funcional: keywords vs id (testes/exemplo3.er)
────────────────────────────────────────────────────────
Definições (exemplo3.er):
    if:    if
    while: while
    id:    [a-zA-Z]([a-zA-Z]|[0-9])*
    num:   [1-9]([0-9])*|0

Entrada (exemplo3.txt):      Saída esperada:
    if                           <if, if>
    while                        <while, while>
    ifx                          <ifx, id>
    whileloop                    <whileloop, id>
    x                            <x, id>
    42                           <42, num>

Neste caso os padrões têm linguagens distintas. O desempate
"primeiro definido vence" funciona corretamente: "if" casa
com o padrão `if` antes de chegar a `id`.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALISADOR SINTÁTICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Aba "Projeto Léxico": carregue testes/exemplo_sintatico.er

    id:    [a-zA-Z]([a-zA-Z]|[0-9])*
    num:   [1-9]([0-9])*|0
    atrib: =
    pv:    ;
    menos: -

Clique em "Gerar Analisador".

Aba "Projeto Sintático": carregue testes/exemplo_sintatico.g

O arquivo usa seções [keywords] e [grammar]. Carregar o arquivo
preenche automaticamente a gramática e as palavras reservadas:

    [keywords]
    if
    while
    int
    float
    return

    [grammar]
    <Prog> ::= <Cmd>
    <Prog> ::= <Prog> pv <Cmd>
    <Cmd>  ::= id atrib <Expr>
    <Expr> ::= id
    <Expr> ::= num
    <Expr> ::= id menos <Expr>
    <Expr> ::= num menos <Expr>

Clique em "Gerar Tabela". Mensagem esperada: "Gramática SLR(1) — tabela gerada com sucesso."

Aba "Execução" → botão "Análise Sintática": use as entradas abaixo.


SENTENÇAS ACEITAS (arquivo testes/entradas_aceitas.txt)
────────────────────────────────────────────────────────
x = 42
  → atribuição simples: id recebe num

resultado = a
  → atribuição entre dois identificadores

x = a - 3
  → expressão com subtração (id menos num)

x = 0 ; y = 1
  → dois comandos separados por ponto-e-vírgula

a = 10 ; b = a ; c = b - 5
  → cadeia de três atribuições, última com subtração


SENTENÇAS REJEITADAS (arquivo testes/entradas_erro.txt)
────────────────────────────────────────────────────────
42 = x
  → Erro sintático: símbolo inesperado 'num' no estado 0
  → número no lado esquerdo da atribuição

x =
  → Erro sintático: símbolo inesperado '$' no estado 4
  → falta a expressão após o =

= x
  → Erro sintático: símbolo inesperado 'atrib' no estado 0
  → falta o identificador antes do =

if = 42
  → Erro sintático: símbolo inesperado 'if' no estado 0
  → "if" é palavra reservada (PR), não é aceito como id

x = a - - b
  → Erro sintático: símbolo inesperado 'menos' no estado 10
  → menos duplo: Expr não permite operador consecutivo

x = y ; ;
  → Erro sintático: símbolo inesperado 'pv' no estado 5
  → ponto-e-vírgula sem comando a seguir


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTA SOBRE TERMINAIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Os terminais da gramática devem corresponder aos nomes dos
padrões definidos no léxico (a coluna esquerda do arquivo .er).
Caracteres que são operadores de ER (* + ? | ( )) não podem
ser usados como terminais via interface — use a demo standalone:

    cd ../sintatico && python3 main.py

Esse script testa a gramática clássica E → E+T | T com a
entrada "id + id * id" alimentando tokens diretamente,
sem passar pelo analisador léxico.
