#/usr/bin/python
import argparse
import ast
import operator
import struct

class Compressor:
    def __init__(self, delimiter="|", file_delimiter=65535):
        self.delimiter = delimiter
        self.file_delimiter = file_delimiter;
        
    def compress_string(self, text):        
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
        
    def decompress_string(self, productions):
        def decompress_symbol(encoded_symbol):
            value = productions[int(encoded_symbol)]
            if self.delimiter in value:
                pair = value.split(self.delimiter)
                return decompress_symbol(pair[0]) + decompress_symbol(pair[1])
            else:
                return value
                                        
        base = max(productions.iteritems(), key=operator.itemgetter(0))[0]
        return decompress_symbol(base)
    
    def compress_file(self, filename):    
        components = []         
        with open(filename, 'r') as input_file:
            input_text = input_file.read()
            productions = self.compress_string(input_text)
            new_filename = filename.split(".")[0] + ".slp"
            with open(new_filename, 'wb') as output_file:                
                for head, body in productions.iteritems():
                    if not self.delimiter in body:
                        output_file.write(struct.pack('>H', head))
                        output_file.write(struct.pack('>H', ord(body)))
                    else:       
                        if not len(components):
                            output_file.write(struct.pack('>H', self.file_delimiter)) 
                        output_file.write(struct.pack('>H', head))                     
                        components = body.split(self.delimiter)                
                        output_file.write(struct.pack('>H', int(components[0])))
                        output_file.write(struct.pack('>H', int(components[1])))
        
    def decompress_file(self, filename):
        productions = {}
        initializedTerminals = False
        with open(filename, 'rb') as input_file:
            character = input_file.read(2)
            while character:
                nonterminal = struct.unpack('>H', character)[0]
                if not initializedTerminals:
                    if nonterminal == self.file_delimiter:
                        initializedTerminals = True
                    else:
                        terminal = chr(struct.unpack('>H', input_file.read(2))[0])
                        productions[nonterminal] = terminal
                else:
                    left_nonterminal = str(struct.unpack('>H', input_file.read(2))[0])
                    right_nonterminal = str(struct.unpack('>H', input_file.read(2))[0])
                    productions[nonterminal] = left_nonterminal + self.delimiter + right_nonterminal   
                  
                character = input_file.read(2)                                               
            
            new_filename = filename.split(".")[0] + ".txt"
            with open(new_filename, 'w') as output_file:                    
                output_file.write(self.decompress_string(productions))
        
def main():
    parser = argparse.ArgumentParser(description='Handles straight-line program compression and decompression of text')
    parser.add_argument('action', metavar='A', choices=['compress', 'decompress'], help='the operation [compress or decompress] to be applied')
    parser.add_argument('-t', '--text', help='the text or production rules to be evaluated')
    parser.add_argument('-f', '--file', help='the file to be evaluated')
    args = parser.parse_args()        
    
    compressor = Compressor("|")    
    if args.action == "compress":
        if args.file:
            compressor.compress_file(args.file)
        elif args.text:
            print compressor.compress_string(args.text)
    elif args.action == "decompress":
        if args.file:
            compressor.decompress_file(args.file)  
        elif args.text:
            print compressor.decompress_string(ast.literal_eval(args.text))

if __name__ == "__main__":
    main()