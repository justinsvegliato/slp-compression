#/usr/bin/python
import argparse
import ast
import operator
import struct
import timeit

class Compressor:

    def __init__(self, file_delimiter=65535):
        self.file_delimiter = file_delimiter;
        
    def compress(self, filename):                
        with open(filename, 'rb') as input_file:
            text = input_file.read()
            with open(filename + '.slp', 'wb') as output_file:  
                # The current nonterminal
                head = 1            
                
                # List of all characters in the string  
                bodies = list(text)
                
                # Dictionary containing terminal-nonterminal pairs (thi
                reverseProductions = {}
                               
                # Handle terminal rules by iterating through each character
                for i in xrange(len(bodies)):
                    # Add this character to the production rules if it hasn't been added yet
                    if not bodies[i] in reverseProductions:                        
                        # Create the reverse production rule
                        reverseProductions[bodies[i]] = head
                  
                        # Output the production rule to the file
                        output_file.write(struct.pack('>H', head))
                        output_file.write(struct.pack('>H', ord(bodies[i])))
                        
                        # Move onto the next nonterminal
                        head += 1   
                    
                    # Replace this character with its corresponding nonterminal    
                    bodies[i] = str(reverseProductions[bodies[i]])                                            
                      
                # Output the file delimiter to the file      
                output_file.write(struct.pack('>H', self.file_delimiter))                                            
                
                # Handle nonterminal conjunction rules until compressed into one symbol
                while len(bodies) > 1:
                    body = (bodies[0], bodies[1])
                    # If we have not yet seen this conjunction
                    if not body in reverseProductions:
                        # If we have already seen the next conjunction, replace with the nonterminal
                        if len(bodies) > 2 and (bodies[1], bodies[2]) in reverseProductions:
                            # Replace the nonterminal conjunction with the new nonterminal
                            bodies[1] = str(reverseProductions[(bodies[1], bodies[2])])
                            del bodies[2]
                        else:
                            # Create the reverse production rule                            
                            reverseProductions[body] = head
                            
                            # Output the nonterminal conjunction rule to the file
                            output_file.write(struct.pack('>H', head))
                            output_file.write(struct.pack('>H', int(bodies[0])))
                            output_file.write(struct.pack('>H', int(bodies[1])))
                            
                            # Replace the nonterminal conjunction with the new nonterminal
                            bodies[0] = str(reverseProductions[body])
                            del bodies[1]
                            
                            # Move onto the next nonterminal
                            head += 1
                    else:
                        # Replace the nonterminal conjunction with the new nonterminal
                        bodies[0] = str(reverseProductions[body])
                        del bodies[1]                        

    def old_compress(self, filename):                
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
                                
                        # Move onto the next nonterminal      
                        head += 1                      
                      
                # Output the file delimiter to the file      
                output_file.write(struct.pack('>H', self.file_delimiter))                 
                
                # Handle nonterminal conjunction rules
                while len(bodies) > 1:
                    # Create a nonterminal conjunction rule
                    productions[head] = (bodies[0], bodies[1])
                    
                    # Output the nonterminal conjunction rule to the file
                    output_file.write(struct.pack('>H', head))
                    output_file.write(struct.pack('>H', int(bodies[0])))
                    output_file.write(struct.pack('>H', int(bodies[1])))
                                      
                    # Replace the current nonterminal conjunction with the higher-order nonterminal
                    bodies[0] = str(head)
                    del bodies[1]                
            
                    # Replace all occurrences of this production rule
                    for index in xrange(1, len(bodies)):
                        # This condition is messy because I focused my time on optimizing
                        # the algorithm rather than making the old algorithm look nice
                        if ((index + 1) < len(bodies)) and ((bodies[index], bodies[index + 1]) == productions[head]):
                            bodies[index] = str(head)
                            del bodies[index + 1]
                            
                    # Move onto the next nonterminal                                                          
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
                    productions[nonterminal] = (left_nonterminal, right_nonterminal)
                
                character = input_file.read(2)                 
           
            # Decompress the production rules                 
            with open(filename[:-4], 'w') as output_file:       
                list = [max(productions.iteritems(), key=operator.itemgetter(0))[0]]
                while len(list):                                                
                    value = productions[int(list.pop(0))]                    
                    # Handle production rule if it is a nonterminal conjunction
                    if len(value) == 2:
                        list = [value[0], value[1]] + list
                    # Handle production rule if it is a terminal assignment
                    else:
                        output_file.write(value)
                                                                                                
def main():
    parser = argparse.ArgumentParser(description='Handles straight-line program compression and decompression of text')
    parser.add_argument('action', metavar='A', choices=['compress', 'oldcompress', 'decompress'], help='the operation [compress or decompress] to be applied')
    parser.add_argument('file', metavar='F', help='the file to be evaluated')
    args = parser.parse_args()
    
    start = timeit.timeit()
    
    compressor = Compressor()    
    if args.action == "compress":
        print "Compressing..."        
        compressor.compress(args.file)
    elif args.action == "oldcompress":
        print "Compressing..."
        compressor.old_compress(args.file)
    elif args.action == "decompress":
        print "Decompressing..."
        compressor.decompress(args.file)  
    
    print "Execution Time: %d" % (timeit.timeit() - start) 

if __name__ == "__main__":
    main()