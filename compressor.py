#/usr/bin/python
import argparse
import ast
import operator
import struct

class Compressor:

    def __init__(self, text_delimiter="|", file_delimiter=65535):
        self.text_delimiter = text_delimiter
        self.file_delimiter = file_delimiter;
        
    def compress(self, filename):                
        with open(filename, 'rb') as input_file:
            text = input_file.read()
            with open(filename + '.slp', 'wb') as output_file:  
                head = 1
                productions = {}       
                bodies = list(text)
                
                # Handle terminal rules
                for body in set(text):
                    # If we haven't added this character to the production rules yet
                    if not body in productions.values():
                        productions[head] = body
                  
                        # Output the terminal rule to the file
                        output_file.write(struct.pack('>H', head))
                        output_file.write(struct.pack('>H', ord(body)))
                    
                        # Replace all occurrences of this terminal with its corresponding nonterminal
                        for index, element in enumerate(bodies):
                            if element == body:
                                bodies[index] = str(head)
                                
                        head += 1                      
                      
                # Output the file delimiter to the file      
                output_file.write(struct.pack('>H', self.file_delimiter))                 
                
                # Handle nonterminal conjunction rules
                while len(bodies) > 1:
                    # Create a nonterminal conjunction rule
                    productions[head] = self.text_delimiter.join(bodies[0:2])
                    
                    # Output the nonterminal conjunction rule to the file
                    output_file.write(struct.pack('>H', head))
                    output_file.write(struct.pack('>H', int(bodies[0])))
                    output_file.write(struct.pack('>H', int(bodies[1])))
                                      
                    # Replace the current nonterminal conjunction with the higher-order nonterminal
                    bodies[0] = str(head)
                    del bodies[1]                
            
                    # Replace all occurrences of this production rule
                    for index in range(1, len(bodies)):
                        if (self.text_delimiter.join(bodies[index:index + 2]) == productions[head]):
                            bodies[index] = str(head)
                            del bodies[index + 1]
                                                                                      
                    head += 1                 
        
    def decompress(self, filename):
        productions = {}
        handledTerminals = False
        with open(filename, 'rb') as input_file:
            # Generate the production rules from the file
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
           
            # Decompress the production rules                 
            with open(filename[:-4], 'w') as output_file:         
                list = [max(productions.iteritems(), key=operator.itemgetter(0))[0]]
                while len(list):                                                
                    value = productions[int(list.pop(0))]                    
                    # Handle production rule if it is a nonterminal conjunction
                    if self.text_delimiter in value:
                        production_rule = value.split(self.text_delimiter)
                        list = production_rule + list
                    # Handle production rule if it is a terminal assignment
                    else:
                        output_file.write(value)
                                                                                                
def main():
    parser = argparse.ArgumentParser(description='Handles straight-line program compression and decompression of text')
    parser.add_argument('action', metavar='A', choices=['compress', 'decompress'], help='the operation [compress or decompress] to be applied')
    parser.add_argument('file', metavar='F', help='the file to be evaluated')
    args = parser.parse_args()
    
    compressor = Compressor("|")    
    if args.action == "compress":
        print "Compressing..."
        compressor.compress(args.file)
    elif args.action == "decompress":
        print "Decompressing..."
        compressor.decompress(args.file)        

if __name__ == "__main__":
    main()