#/usr/bin/python
import argparse
import ast
import operator

class Compressor:
    def __init__(self, delimiter="|"):
        self.delimiter = delimiter
        
    def compress_to_string(self, text):        
        nonterminal = 1
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

    def decompress_to_string(self, productions):
        def decompress_symbol(encoded_symbol):
            value = productions[int(encoded_symbol)]
            if self.delimiter in value:
                pair = value.split(self.delimiter)
                return decompress_symbol(pair[0]) + decompress_symbol(pair[1])
            else:
                return value          
              
        base = max(productions.iteritems(), key=operator.itemgetter(0))[0]
        return decompress_symbol(base)
        
    def decompress_to_file(self, productions, filename):
        text = self.decompress_to_string(productions)
        
        f = open(filename, 'w')
        f.write(text)
        f.close()
        
        return text
        
def main():
    parser = argparse.ArgumentParser(description='Handles straight-line program compression and decompression of text')
    parser.add_argument('action', metavar='A', choices=['compress', 'decompress'], help='the operation [compress or decompress] to be applied')
    parser.add_argument('text', metavar='T', help='the text or production rules to be evaluated')
    parser.add_argument('-f', '--file', help='the location of the result')
    args = parser.parse_args()        
    
    compressor = Compressor("|")    
    if args.action == "compress":
        if args.file:
            compressor.compress_to_file(args.text, args.file)
        print compressor.compress_to_string(args.text)
    elif args.action == "decompress":
        productions = ast.literal_eval(args.text)
        if args.file:
            compressor.decompress_to_file(productions, args.file)  
        print compressor.decompress_to_string(productions)

if __name__ == "__main__":
    main()