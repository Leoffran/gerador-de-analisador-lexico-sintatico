[grammar]
<Expr>  ::= <Expr> mais <Termo> | <Expr> menos <Termo> | <Termo>
<Termo> ::= <Termo> vezes <Pot> | <Termo> div <Pot> | <Termo> divint <Pot> | <Termo> mod <Pot> | <Pot>
<Pot>   ::= <Fator> pot <Pot> | <Fator>
<Fator> ::= menos <Fator> | <Base>
<Base>  ::= abre <Expr> fecha | id | num
