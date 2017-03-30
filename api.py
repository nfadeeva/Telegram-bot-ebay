import requests
import config
from xml.dom import minidom
from io import BytesIO
import xml.etree.ElementTree as ET


def findItemsByKeywords(
        keywords, outputSelector=None,
        paginationInput=None,
        sortOrder=None, itemFilter=None):

    root = ET.Element("findItemsByKeywords",
                         xmlns="http://www.ebay.com/marketplace/search/v1/services")

    keywords_elem = ET.SubElement(root, "keywords")
    keywords_elem.text = keywords

    # outputSelector is a list
    if outputSelector:
        for item in outputSelector:
            outputSelector_elem = ET.SubElement(root, "outputSelector")
            outputSelector_elem.text = item

    # paginationInput is a dict
    if paginationInput:
        paginationInput_elem = ET.SubElement(root, "paginationInput")
        for key in paginationInput:
            key_elem = ET.SubElement(paginationInput_elem, key)
            key_elem.text = paginationInput[key]

    # itemFilter is a list of dicts
    if itemFilter:
        for item in itemFilter:
            itemFilter_elem = ET.SubElement(root, "itemFilter")
            for key in item:
                key_elem = ET.SubElement(itemFilter_elem, key)
                key_elem.text = item[key]

    # sortOrder
    if sortOrder:
        sortOrder_elem = ET.SubElement(root, "sortOrder")
        sortOrder_elem.text = sortOrder
    return ET.tostring(root)

def parse_xml(xmldoc, tag):
    """Get the xmldoc and tag and return list of elements"""

    res = []
    for element in xmldoc.getElementsByTagName(tag):
        res.append(element.firstChild.nodeValue)
    return res

def parse_sellerInfo(xmldoc):
    for element in xmldoc.getElementsByTagName('sellerInfo'):
        element = element.firstChild
        print(element.localName, element.firstChild.nodeValue)
        while(element.nextSibling):
            element = element.nextSibling
            print(element.localName, element.firstChild.nodeValue)
        print()

def request(keywords):
    headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
               'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
               'X-EBAY-SOA-SECURITY-APPNAME': config.Key,
               'Content-Type': 'text/xml'}

    xml = findItemsByKeywords('pen',outputSelector=['SellerInfo'],paginationInput={'entriesPerPage':'20', 'pageNumber': '1'})
    s = requests.post('http://svcs.ebay.com/services/search/FindingService/v1', data=xml, headers=headers)
    return BytesIO(s.content)


xmldoc = minidom.parse(request('pen'))
parse_sellerInfo(xmldoc)