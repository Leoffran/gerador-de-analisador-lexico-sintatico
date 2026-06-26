from automato import Automato

def lexer(afd, texto):
    """Tokeniza o texto fonte usando o AFD final"""
    # Retorna uma lista de tuplas <Lexema, Nome Padrão> ou <Lexema, 'erro!'>
    tokens = []
    # começa no estado inicial
    estado = afd.start 
    # acumula o lexema atual
    lexema = ''
    # posição no texto
    i = 0

    # varre o texto
    while i < len(texto):
        # pega a letra atual
        ch = texto[i]

        # espaços e quebras de linha separam tokens -> emite!
        if ch in ' \n\t':
            if lexema:
                # emite o token acumulado
                if estado in afd.aceitacao:
                    tokens.append((lexema, afd.aceitacao[estado]))
                else:
                    tokens.append((lexema, 'erro!'))
                # limpa pra próxima iteração
                lexema = ''
                estado = afd.start
            # avança
            i += 1 
            continue
        
        # se não for final do token, tenta transicionar
        proximo = afd.transicoes.get((estado, ch))

        # se existe transição:
        if proximo is not None:
            # acumula e avança
            lexema += ch
            estado = proximo
            i += 1
        
        # se não existe transição: emite oque acumulou
        # (encontrou um caractere que não pertence ao token atual) -> emite
        # ex: depois de acumular 'abc', recebeu '!' sem transição -> emite <abc, id>
        else:
            # se há algo acumulado até agora:
            if lexema:
                # se for aceito: emite e reinicia
                if estado in afd.aceitacao:
                    tokens.append((lexema, afd.aceitacao[estado]))
                # se não for aceito: emite o acumulado e erro
                else:
                    tokens.append((lexema, 'erro!'))
                # reinicia para a próxima iteração
                lexema = ''
                estado = afd.start
            # se não há nada acumulado:
            else:
                # caractere invalido sozinho:
                tokens.append((ch, 'erro!'))
                i += 1

    # o texto acabou mas ainda há lexema acumulado que não foi emitido
    # isso acontece quando o texto termina sem espaço ou quebra de linha
    # ex: "abc" -> loop termina com lexema = 'abc' sem ser transmitido
    if lexema:
        if estado in afd.aceitacao:
            tokens.append((lexema, afd.aceitacao[estado]))
        else:
            tokens.append((lexema, 'erro!'))

    return tokens

def salvar_tokens(tokens):
    """Salva os tokens no arquivo de saída"""
    with open('../tokens.txt', 'w') as f:
        for lexema, padrao in tokens:
            f.write(f"<{lexema}, {padrao}>\n")