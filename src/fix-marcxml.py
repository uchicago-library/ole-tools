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
import xml.sax
import xml.sax.saxutils

xml_decl = '<?xml version="1.0" encoding="UTF-8"?>'
marcxml_ns = "http://www.loc.gov/MARC21/slim"
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

class MyXMLGenerator(xml.sax.saxutils.XMLGenerator):

    def __init__(self, out=None, encoding="iso-8859-1", short_empty_elements=False):
        self.doc_count = 0
        super().__init__(out, encoding, short_empty_elements)

    def super(self):
        """provide access to base class methods.
        
        Use with caution, this is egregious abuse!"""

        return super()

    def startDocument(self):
        """Custom startDocument to ensure that only one XML declaration is output.
        
        With the base startDocument, a new XML declaration would be output with each line/each new parser.
        """

        if self.doc_count > 0:
            pass
        else:
            self.doc_count += 1
            super().startDocument()

    def startElement(self, name, attrs):

        if name == 'collection':
            return
        super().startElement(name, attrs)

    def endElement(self, name):

        if name == 'collection':
            return

        super().endElement(name)
        
        if name == 'record':
            self.ignorableWhitespace('\n')


def sax(infile, outfile):
    """ Fix using xml.sax package.

    Basic strategy is to subclass the stock XMLGenerator and conveniently omit collection.
    This will have the side-effect of also trimming namespaces.
    """

    global xml_decl
    global marcxml_ns
    global start_coll
    global end_coll

    #handler = xml.sax.saxutils.XMLGenerator(outfile, encoding='utf-8')
    handler = MyXMLGenerator(outfile, encoding='utf-8')
    # call startDocument explicitly, so we control
    handler.startDocument()
    handler.super().startElement('collection', {'xmlns':marcxml_ns})
    handler.ignorableWhitespace('\n')
    #sys.exit(0)
    for line in infile:
        xml.sax.parseString(line, handler)
    handler.super().endElement('collection')
    handler.ignorableWhitespace('\n')

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
    elif args.method == 'sax':
        sax(args.infile, args.outfile)
    else:
        sys.stderr.write('Invalid method: {}\n'.format(args.method))
        sys.exit(3)

    sys.exit(0)


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(1)
