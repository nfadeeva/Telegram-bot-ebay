import requests
import config
from xml.dom import minidom
from io import StringIO, BytesIO


def request(keywords):
    headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
               'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
               'X-EBAY-SOA-SECURITY-APPNAME': config.Key,
               'Content-Type': 'text/xml'}

    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <findItemsByKeywordsRequest xmlns="http://www.ebay.com/marketplace/search/v1/services">
      <keywords>""" + keywords + """</keywords>
      <outputSelector>SellerInfo</outputSelector>
      <paginationInput>
        <entriesPerPage>20</entriesPerPage>
      </paginationInput>
    </findItemsByKeywordsRequest>"""

    s = requests.post('http://svcs.sandbox.ebay.com/services/search/FindingService/v1', data=xml, headers=headers)
    return BytesIO(s.content)


xmldoc = minidom.parse(request('pen'))


def parse_xml(xmldoc, tag):
    """Get the xmldoc and tag and return list of elements"""

    res = []
    for element in xmldoc.getElementsByTagName(tag):
        res.append(element.firstChild.nodeValue)
    return res


print(parse_xml(xmldoc, 'sellerUserName'))