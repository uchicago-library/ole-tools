#!/usr/bin/env python3

"""Test OLE NCIP services.

"""

import argparse
import os
import string
import sys
import urllib.request
import time
import xml.etree.ElementTree as ET


class NCIPItems:
    """simple class to represent an NCIP item to be created and loaned"""
    
    def __init__(self, item_barcode, patron_barcode, 
                 author = "NCIP test program", title = "NCIP test record",
                 callnumber = "NCIP 123.TST45"):
        self.item_barcode = item_barcode
        self.patron_barcode = patron_barcode
        self.author = author
        self.title = title
        self.callnumber = callnumber
        self.accept_status = False
        self.checkout_status = False
        self.checkin_status = False
        
    def __repr__(self):
        str = type(self).__name__ + "("
        for k in sorted(self.__dict__.keys()):
            str += k + '=' + repr(self.__dict__[k]) + ','
        str += ")"
        return str

def accept_item_request(svc, ncip_item):
    """Return a Request object for a NCIP AcceptItem"""

    global args
    
    accept_template = """<?xml version="1.0" encoding="UTF-8"?>
<NCIPMessage xmlns:v="http://www.niso.org/2008/ncip" xmlns="http://www.niso.org/2008/ncip" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" v:version="5.6" xsi:schemaLocation="http://www.niso.org/2008/ncip http://www.niso.org/schemas/ncip/v2_0/ncip_v2_0.xsd ">
  <AcceptItem>
    <InitiationHeader>
      <FromAgencyId>
        <AgencyId>BORROWDIRECT</AgencyId>
      </FromAgencyId>
      <ToAgencyId>
        <AgencyId>CHICAGO</AgencyId>
      </ToAgencyId>
    </InitiationHeader>
    <RequestId>
      <RequestIdentifierValue>{0}</RequestIdentifierValue>
    </RequestId>
    <RequestedActionType>Hold For Pickup</RequestedActionType>
    <UserId>
      <UserIdentifierValue>{1}</UserIdentifierValue>
    </UserId>
    <ItemId>
      <ItemIdentifierValue>{0}</ItemIdentifierValue>
    </ItemId>
    <ItemOptionalFields>
      <BibliographicDescription>
        <Author>{2}</Author>
        <Title>{3}</Title>
      </BibliographicDescription>
      <ItemDescription>
        <CallNumber>{4}</CallNumber>
      </ItemDescription>
    </ItemOptionalFields>
    <PickupLocation>JRLMAIN</PickupLocation>
  </AcceptItem>
</NCIPMessage>"""
    accept_msg = accept_template.format(ncip_item.item_barcode,
                                        ncip_item.patron_barcode,
                                        ncip_item.author, ncip_item.title,
                                        ncip_item.callnumber)
    if args.verbose:
        print(accept_msg)
    return urllib.request.Request(svc, method="POST",
                                  headers = {'Content-Type': 'application/xml'},
                                  data=accept_msg.encode(encoding="utf-8"))

def checkout_item_request(svc, ncip_item):
    """Return a Request object for a NCIP CheckoutItem"""

    global args
    
    checkout_template = """<?xml version="1.0" encoding="UTF-8"?>
<NCIPMessage xmlns:v="http://www.niso.org/2008/ncip" xmlns="http://www.niso.org/2008/ncip" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" v:version="5.6" xsi:schemaLocation="http://www.niso.org/2008/ncip http://www.niso.org/schemas/ncip/v2_0/ncip_v2_0.xsd ">
  <CheckOutItem>
    <InitiationHeader>
      <FromAgencyId>
        <AgencyId>BORROWDIRECT</AgencyId>
      </FromAgencyId>
      <ToAgencyId>
        <AgencyId>University of Chicago</AgencyId>
      </ToAgencyId>
    </InitiationHeader>
    <UserId>
      <AgencyId>BORROWDIRECT</AgencyId>
      <UserIdentifierValue>{0}</UserIdentifierValue>
    </UserId>
    <ItemId>
      <AgencyId>BORROWDIRECT</AgencyId>
      <ItemIdentifierValue>{1}</ItemIdentifierValue>
    </ItemId>
  </CheckOutItem>
</NCIPMessage>"""
    checkout_msg = checkout_template.format(ncip_item.patron_barcode,
                                           ncip_item.item_barcode)
    if args.verbose:
        print(checkout_msg)
    return urllib.request.Request(svc, method="POST",
                                  headers = {'Content-Type': 'application/xml'},
                                  data=checkout_msg.encode(encoding="utf-8"))

def checkin_item_request(svc, ncip_item):
    """Return a Request object for a NCIP CheckinItem"""

    global args

    checkin_template = """<?xml version = '1.0' encoding='UTF-8'?> <NCIPMessage
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
version="http://www.niso.org/schemas/ncip/v2_0/ncip_v2_0.xsd">
 <CheckInItem>
   <InitiationHeader>
     <FromAgencyId>
       <AgencyId>BORROWDIRECT</AgencyId>
     </FromAgencyId>
     <ToAgencyId>
       <AgencyId>CHICAGO</AgencyId>
     </ToAgencyId>
   </InitiationHeader>
   <ItemId>
     <ItemIdentifierValue>{0}</ItemIdentifierValue>
   </ItemId>
   <ItemElementType>Bibliographic Description</ItemElementType>
   <ItemElementType>Item Description</ItemElementType>
 </CheckInItem>
</NCIPMessage>"""
    checkin_msg = checkin_template.format(ncip_item.item_barcode)
    if args.verbose:
        print(checkin_msg)
    return urllib.request.Request(svc, method="POST",
                                  headers = {'Content-Type': 'application/xml'},
                                  data=checkin_msg.encode(encoding="utf-8"))

def make_request(request):
    """Makes NCIP request, returns response and elapsed time"""
    
    start = time.time()
    response = urllib.request.urlopen(request)
    end = time.time()
    return (response, end - start)

_success_msg = """
Success:
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<NCIPMessage xmlns="http://www.niso.org/2008/ncip" version="http://www.niso.org/schemas/ncip/v2_0/imp1/xsd/ncip_v2_0.xsd">
    <AcceptItemResponse>
            <RequestId>
                <AgencyId>BORROWDIRECT</AgencyId>
                <RequestIdentifierType Scheme="Scheme">Request Id</RequestIdentifierType>
                <RequestIdentifierValue>108975</RequestIdentifierValue>
            </RequestId>
            <ItemId>
                <AgencyId>BORROWDIRECT</AgencyId>
                <ItemIdentifierType Scheme="Scheme">Item Barcode</ItemIdentifierType>
                <ItemIdentifierValue>TST-66504-0001</ItemIdentifierValue>
            </ItemId>
        </AcceptItemResponse>
</NCIPMessage>
"""

_fail_msg = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<NCIPMessage xmlns="http://www.niso.org/2008/ncip" version="http://www.niso.org/schemas/ncip/v2_0/imp1/xsd/ncip_v2_0.xsd">
    <AcceptItemResponse>
        <Problem>
            <ProblemType></ProblemType>
            <ProblemDetail>Request failed</ProblemDetail>
            <ProblemElement>Item</ProblemElement>
            <ProblemValue>TST-66450-0001</ProblemValue>
        </Problem>
    </AcceptItemResponse>
</NCIPMessage>
"""
def check_accept_item(response):
    if response.getcode() != 200:
        print("response code: " + str(response.getcode()))
        #for h in response.getheaders():
        #    print(h)
        response_body = response.read().decode("utf-8")
        print("response body: " + response_body)

def check_ncip_response(response):
    global fail
    
    response_body = response.read().decode("utf-8")

    if response.getcode() != 200:
        print("Server error: HTTP " + str(response.getcode()))
        print("response body: " + response_body)
        return
    
    ncip_message = ET.fromstring(response_body)
    #ncip_message = ET.fromstring(fail)
    # print("Msg:" + repr(ncip_message))
    problem = ncip_message.find('.//ncip:Problem',
                                namespaces = {'ncip': 'http://www.niso.org/2008/ncip'})
    #print("Prob:" + repr(problem)) 
    if problem != None:
        print("Failure!:")
        for e in problem:
            print('\t' + e.tag + '=' + str(e.text))
    else:
        print("Success!")
        
    return
        
def parse_arguments(arguments):
    """parse command-line arguments and return a Namespace object"""
    
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser.add_argument('infile', help="Input file", type=argparse.FileType('r'))
    parser.add_argument('patron_barcode',
                        help="patron barcode to use with NCIP requests")
    parser.add_argument('ncip_service', help="Base URL for NCIP responder")
    parser.add_argument('-a', '--accept_items_only', action='store_true',
                        help='run AcceptItems only')
    parser.add_argument('-n', '--number_items', type=int, default=3,
                        help="number of items to create (default: 3)")
    parser.add_argument('-o', '--outfile', help="Output file",
                        default=sys.stdout, type=argparse.FileType('w'))
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose mode, print out NCIP request messages')
    return parser.parse_args(arguments)

def main(arguments):
    global args
    args = parse_arguments(arguments)
    print(args)

    # build item list
    item_list = []
    for i in range(args.number_items):
        item_barcode = 'TST-{0}-{1:0>4}'.format(str(os.getpid()), i)
        title = 'NCIP test record {0}, process {1}'.format(i, str(os.getpid()))
        item = NCIPItems(item_barcode=item_barcode, 
                         patron_barcode=args.patron_barcode, 
                         title=title)
        item_list.append(item)
        
    #print(item_list)

    # run AcceptItem for all items in list
    for ncip_item in item_list:
        print("Accept: " + str(ncip_item))
        #response = accept_item(args.ncip_service, item)
        request = accept_item_request(args.ncip_service, ncip_item)
        response, response_time = make_request(request)
        print('AcceptItem time for barcode {0}: {1:.2f}'.format(ncip_item.item_barcode, response_time))
        check_ncip_response(response)
        time.sleep(2)
        
    if not args.accept_items_only:
        print("Sleeping...")
        time.sleep(5)
        # call CheckoutItem on each item
        for ncip_item in item_list:
            print("Checkout: " + ncip_item.item_barcode)
            request = checkout_item_request(args.ncip_service, ncip_item)
            response, response_time = make_request(request)
            print('CheckoutItem time for barcode {0}: {1:.2f}'.format(ncip_item.item_barcode, response_time))
            check_ncip_response(response)
            time.sleep(2)
        print("Sleeping...")
        time.sleep(5)
        # call CheckinItem on each item
        for item in item_list:
            print("Checking: " + item.item_barcode)
            request = checkin_item_request(args.ncip_service, ncip_item)
            response, response_time = make_request(request)
            print('CheckinItem time for barcode {0}: {1:.2f}'.format(ncip_item.item_barcode, response_time))
            check_ncip_response(response)
            time.sleep(2)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
