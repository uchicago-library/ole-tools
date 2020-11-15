#!/usr/bin/env python3

"""Fix OLE MARCXML export files.

OLE MARCXML files wrap each record in a collection element, 
and prefix each with an XML declaration. 
In effect, it is concatenated single-record XML files. 

"""

import argparse
import os
import string
import sys
import time
import xml.etree.ElementTree as ET

        
def brute_force(infile, outfile):
    """Brute foce method of fixing the OLE MARCXML output, relies on hard-coded assumptions about file structure.
    """

    xml_decl = '<?xml version="1.0" encoding="UTF-8"?>'
    start_coll = '<collection xmlns="http://www.loc.gov/MARC21/slim">'
    end_coll = '</collection>'

    start_line = xml_decl + start_coll
    end_line = end_coll + '\n'

    outfile.write(xml_decl + '\n')
    outfile.write(start_coll + '\n')

    for line in infile:
        # sanity check
        if line.startswith(start_line) and line.endswith(end_line):
            out = line[len(start_line):-len(end_line)]
            outfile.write(out)

    outfile.write('\n' + end_coll + '\n')

def element_tree(infile, outfile):

    #outfile.write(ET.ProcessingInstruction('xml'))
    outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')


    
    for event,elem in ET.iterparse(infile, ['start', 'end']):
        if (event == "end" and elem.tag == "{http://www.loc.gov/MARC21/slim}record"):
            #outfile.write("event: {}\telement: {}\n".format(event, elem.tag))
            outfile.write(str(ET.tostring(elem),'utf-8'))
            outfile.write("\n")
            outfile.flush()


def parse_arguments(arguments):
    """parse command-line arguments and return a Namespace object"""
    

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-m', '--method', help="Parsing method: bute or etree (default: %(default)s)",
                        default='brute')
    parser.add_argument('-i', '--infile', help="Input file", 
                        default=sys.stdin, type=argparse.FileType('r'))
    parser.add_argument('-o', '--outfile', help="Output file",
                        default=sys.stdout, type=argparse.FileType('w'))
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose mode')
    return parser.parse_args(arguments)

def main(arguments):
    global args
    args = parse_arguments(arguments)
    
    if args.method == 'brute':
        brute_force(args.infile, args.outfile)
    elif args.method == 'etree':
        element_tree(args.infile, args.outfile)
    else:
        sys.stderr.write('Invalid method: {}\n'.format(args.method))
        sys.exit(3)

    sys.exit(0)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(1)
