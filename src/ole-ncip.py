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
        
    def __repr__(self):
        str = type(self).__name__ + "("
        for k in sorted(self.__dict__.keys()):
            str += k + '=' + repr(self.__dict__[k]) + ','
        str += ")"
        return str


def accept_item(svc, ncip_item):
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
    request = urllib.request.Request(svc, method="POST",
                                     data=accept_msg.encode(encoding="utf-8"))
    start = time.time()
    response = urllib.request.urlopen(request)
    end = time.time()
    print('Accept item time for barcode {0}: {1:.2f}'.format(ncip_item.item_barcode, end - start))
    return response

def checkout_item(svc, ncip_item):
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
    request = urllib.request.Request(svc, method="POST",
                                     data=checkout_msg.encode(encoding="utf-8"))
    start = time.time()
    response = urllib.request.urlopen(request)
    end = time.time()
    print('Checkout item time for barcode {0}: {1:.2f}'.format(ncip_item.item_barcode, end - start))
    return response

def checkin_item(svc, ncip_item):
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
    request = urllib.request.Request(svc, method="POST",
                                     data=checkin_msg.encode(encoding="utf-8"))
    start = time.time()
    response = urllib.request.urlopen(request)
    end = time.time()
    print('Checkin item time for barcode {0}: {1:.2f}'.format(ncip_item.item_barcode, end - start))
    return response


"""
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

fail = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
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
    if response.getcode != 200:
        print("response code: " + str(response.getcode()))
        #for h in response.getheaders():
        #    print(h)
        response_body = response.read().decode("utf-8")
        print("response body: " + response_body)


def check_ncip_response(response):
    global fail
    
    #print("response code: " + str(response.getcode()))
    response_body = response.read().decode("utf-8")
    #print("response body: " + response_body)
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
        
def parse_arguments(arguments):
    """parse command-line arguments and return a Namespace object"""
    
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    #parser.add_argument('infile', help="Input file", type=argparse.FileType('r'))
    parser.add_argument('ncip_service', help="Base URL for NCIP responder")
    parser.add_argument('-n', '--number_items', type=int,
                        help="number of items to create")
    parser.add_argument('-o', '--outfile', help="Output file",
                        default=sys.stdout, type=argparse.FileType('w'))
    return parser.parse_args(arguments)

def main(arguments):
    args = parse_arguments(arguments)
    print(args)
    
    item_list = []
    for i in range(args.number_items):
        item_barcode = 'TST-{0}-{1:0>4}'.format(str(os.getpid()), i)
        patron_barcode = '6376346'
        title = 'NCIP test record {0}, process {1}'.format(i, str(os.getpid()))
        item = NCIPItems(item_barcode=item_barcode, 
                         patron_barcode=patron_barcode, 
                         title=title)
        item_list.append(item)
        
    #print(item_list)
    
    for item in item_list:
        print("Accept: " + str(item))
        response = accept_item(args.ncip_service, item)
        check_ncip_response(response)
    for item in item_list:
        print("Checkout: " + item.item_barcode)
        response = checkout_item(args.ncip_service, item)
        check_ncip_response(response)
    for item in item_list:
        print("Checkin: " + item.item_barcode)
        response = checkin_item(args.ncip_service, item)
        check_ncip_response(response)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
