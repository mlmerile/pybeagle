import gzip
import sys
import os
import logging

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def ungzip(file):
    dirpath = os.path.dirname(file)
    filename, fileextension = os.path.splitext(file)
    res_file = os.path.join(dirpath,filename)

    logging.info(res_file)
    with gzip.open(file,'rb') as infile:
        with open(res_file,'w') as outfile:
            for line in infile:
                outfile.write(line)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("{0} filename".format(sys.argv[0]))
        sys.exit(0)
    ungzip(sys.argv[1])
