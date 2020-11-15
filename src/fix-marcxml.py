#!/usr/bin/env python3

"""Fix OLE MARCXML export files.

OLE MARCXML files wrap each record in a collection element, 
and prefix each with an XML declaration. 
In effect, it is concatenated single-record XML files. 

"""

import argparse
import io
import os
import string
import sys
import time
import xml.etree.ElementTree as ET

xml_decl = '<?xml version="1.0" encoding="UTF-8"?>'
start_coll = '<collection xmlns="http://www.loc.gov/MARC21/slim">'
end_coll = '</collection>'
        
def brute_force(infile, outfile):
    """Brute foce method of fixing the OLE MARCXML output, relies on hard-coded assumptions about file structure.
    """

    global xml_decl
    global start_coll
    global end_coll

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

def etree(infile, outfile):
    """Fix using xml.etree package.

    Each line is a complete document with an enclosing <collection> and a default namespace.
    Strategy is the read each line which and only print the <record> elements, effectively stripping the <collection> element. 
    The single enclosing <colllection> start and end tags are added in hard-coded fashion.

    One complication is that every call of ET.tostring() includes the defined namespace.
    So if we set a default namespace to avoid prefixes everywhere, we still get a 
    """

    global xml_decl
    global start_coll
    global end_coll

    # Register MARCXML namespace as default, it still prints with every <record>
    ET.register_namespace('', "http://www.loc.gov/MARC21/slim")
    #outfile.write(ET.ProcessingInstruction('xml'))
    outfile.write(xml_decl + '\n')
    outfile.write(start_coll + '\n')

    for line in infile:
        for event,elem in ET.iterparse(io.StringIO(line), ['start', 'end']):
            if (event == "end" and elem.tag == "{http://www.loc.gov/MARC21/slim}record"):
                #outfile.write("event: {}\telement: {}\n".format(event, elem.tag))
                elem.tail = '\n'
                outfile.write(str(ET.tostring(elem),'utf-8'))

    outfile.write(end_coll + '\n')
    outfile.flush()

def parse_arguments(arguments):
    """parse command-line arguments and return a Namespace object"""
    
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-m', '--method', help="Parsing method: bute, etree, or sax (default: %(default)s)",
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
        etree(args.infile, args.outfile)
    else:
        sys.stderr.write('Invalid method: {}\n'.format(args.method))
        sys.exit(3)

    sys.exit(0)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(1)
