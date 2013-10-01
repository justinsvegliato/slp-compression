#/usr/bin/python

from compressor import Compressor
import sys

def main():
    text = sys.argv[1]
    compressor = Compressor("|")
    productions = compressor.compress_to_file(text, "yo")  
    compressor.decompress_to_file("4", productions, "decompression")  

if __name__ == "__main__":
    main()