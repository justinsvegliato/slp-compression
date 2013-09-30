def compress(text):
    nonterminal = 0
    productions = {}
    
    for character in ''.join(set(text)):
        if not character in productions.values():
            productions[nonterminal] = character
            text = text.replace(character, str(nonterminal))
            nonterminal += 1
            
    i = 0            
    while len(text) > 1:
        pair = text[0:2]
        text = text.replace(character, str(nonterminal))
        nonterminal += 1
        print text
    
    print productions
    print text