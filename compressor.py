#/usr/bin/python
import argparse
import ast
import operator
import struct

class Compressor:
    def __init__(self, text_delimiter="|", file_delimiter=65535):
        self.text_delimiter = text_delimiter
        self.file_delimiter = file_delimiter;
        
    def compress_string(self, text):        
        head = 1
        productions = {}
    
        bodies = list(text)
        for body in list(text):
            if not body in productions.values():
                productions[head] = body
                for index, element in enumerate(bodies):
                    if element == body:
                        bodies[index] = str(head)
                head += 1
                    
        while len(bodies) > 1:
            productions[head] = self.text_delimiter.join(bodies[0:2])
            bodies[0] = str(head)
            del bodies[1]
              
            for index in range(1, len(bodies)):
                if (self.text_delimiter.join(bodies[index:index + 2]) == productions[head]):
                    bodies[index] = str(head)
                    del bodies[index + 1]                
                                          
            head += 1      
        
        return productions
        
    def decompress_string(self, productions):
        def decompress_symbol(encoded_symbol):
            value = productions[int(encoded_symbol)]
            if self.text_delimiter in value:
                pair = value.split(self.text_delimiter)
                return decompress_symbol(pair[0]) + decompress_symbol(pair[1])
            else:
                return value
                                                        
        base = max(productions.iteritems(), key=operator.itemgetter(0))[0]
        return decompress_symbol(base)
    
    def compress_file(self, filename):    
        handledDelimiter = False         
        with open(filename, 'r') as input_file:
            input_text = input_file.read()
            productions = self.compress_string(input_text)       
                 
            with open(filename  + ".slp", 'wb') as output_file:                
                for head, body in productions.iteritems():
                    if not self.text_delimiter in body:
                        output_file.write(struct.pack('>H', head))
                        output_file.write(struct.pack('>H', ord(body)))
                    else:       
                        if not handledDelimiter:
                            output_file.write(struct.pack('>H', self.file_delimiter)) 
                            handledDelimiter = True
                            
                        output_file.write(struct.pack('>H', head))                     
                        nonterminals = body.split(self.text_delimiter)                
                        output_file.write(struct.pack('>H', int(nonterminals[0])))
                        output_file.write(struct.pack('>H', int(nonterminals[1])))
        
    def decompress_file(self, filename):
        productions = {}
        handledTerminals = False
        with open(filename, 'rb') as input_file:
            character = input_file.read(2)
            while character:
                nonterminal = struct.unpack('>H', character)[0]
                if not handledTerminals:
                    if nonterminal == self.file_delimiter:
                        handledTerminals = True
                    else:
                        terminal = chr(struct.unpack('>H', input_file.read(2))[0])
                        productions[nonterminal] = terminal
                else:
                    left_nonterminal = str(struct.unpack('>H', input_file.read(2))[0])
                    right_nonterminal = str(struct.unpack('>H', input_file.read(2))[0])
                    productions[nonterminal] = left_nonterminal + self.text_delimiter + right_nonterminal                     
                character = input_file.read(2)                                               
            
            with open(filename[:-4], 'w') as output_file:                    
                output_file.write(self.decompress_string(productions))
        
def main():
    parser = argparse.ArgumentParser(description='Handles straight-line program compression and decompression of text')
    parser.add_argument('action', metavar='A', choices=['compress', 'decompress'], help='the operation [compress or decompress] to be applied')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--text', help='the text or production rules to be evaluated')
    group.add_argument('-f', '--file', help='the file to be evaluated')
    args = parser.parse_args()        
    
    compressor = Compressor("|")    
    if args.action == "compress":
        print "Compressing..."
        if args.file:
            compressor.compress_file(args.file)
        elif args.text:
            print compressor.compress_string(args.text)
    elif args.action == "decompress":
        print "Decompressing..."
        if args.file:
            compressor.decompress_file(args.file)  
        elif args.text:
            print compressor.decompress_string(ast.literal_eval(args.text))

if __name__ == "__main__":
    main()