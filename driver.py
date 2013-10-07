#/usr/bin/python
from compressor import Compressor
import argparse
import ast

def main():
    parser = argparse.ArgumentParser(description='Handles the straight-line program compression and decompression of text')
    parser.add_argument('action', metavar='A', choices=['compress', 'decompress'], help='the operation (compress or decompress) to be applied')
    parser.add_argument('text', metavar='T', help='the text to be operated upon')
    parser.add_argument('productions', metavar='P', nargs='?', help='the productions rules for decompression')
    parser.add_argument('-f', '--file', help='the location of the result')
    args = parser.parse_args()        
    
    compressor = Compressor("|")    
    if args.action == "compress":
        if args.file:
            compressor.compress_to_file(args.text, args.file)
        print compressor.compress_to_string(args.text)
    elif args.action == "decompress" and args.productions:
        productions = ast.literal_eval(args.productions)
        if args.file:
            compressor.decompress_to_file(args.text, productions, args.file)  
        print compressor.decompress_to_string(args.text, productions)

if __name__ == "__main__":
    main()