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
