#/usr/bin/python

from compressor import compress
import sys

def main():
    text = sys.argv[1]
    compress(text)

if __name__ == "__main__":
    main()