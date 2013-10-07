class Compressor:
    def __init__(self, delimiter="|"):
        self.delimiter = delimiter
        
    def compress_to_string(self, text):        
        nonterminal = 0
        productions = {}
    
        characters = list(text)
        for character in list(text):
            if not character in productions.values():
                productions[nonterminal] = character
                for index, element in enumerate(characters):
                    if element == character:
                        characters[index] = str(nonterminal)
                nonterminal += 1
                    
        while len(characters) > 1:
            productions[nonterminal] = self.delimiter.join(characters[0:2])
            characters[0] = str(nonterminal)
            del characters[1]
              
            for index in range(1, len(characters)):
                if (self.delimiter.join(characters[index:index + 2]) == productions[nonterminal]):
                    characters[index] = str(nonterminal)
                    del characters[index + 1]                
                      
            nonterminal += 1      
        
        return productions
    
    def compress_to_file(self, text, filename):
        productions = self.compress_to_string(text)
        
        output = ""
        for key, value in productions.iteritems():
            output += str(key);
            if self.delimiter in value:
                pair = value.split(self.delimiter)
                output += pair[0] + pair[1]
            else:
                output += value; 
        
        f = open(filename, 'w')
        f.write(output)
        f.close()    
        
        return productions 

    def decompress_to_string(self, encoded_text, productions):
        def decompress_symbol(encoded_symbol):
            value = productions[int(encoded_symbol)]
            if self.delimiter in value:
                pair = value.split(self.delimiter)
                return decompress_symbol(pair[0]) + decompress_symbol(pair[1])
            else:
                return value
        
        text = ""
        for encoded_symbol in list(encoded_text):
            text += decompress_symbol(encoded_symbol) 
    
        return text
        
    def decompress_to_file(self, encoded_text, productions, filename):
        text = self.decompress_to_string(encoded_text, productions)
        
        f = open(filename, 'w')
        f.write(text)
        f.close()
        
        return text