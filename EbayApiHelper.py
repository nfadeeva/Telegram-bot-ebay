import requests
from io import BytesIO
import xml.etree.ElementTree as ET
import config
from xml.dom import minidom

class EbayApiHelper:
    """
    This class is for making xml request and get xml response
    """

    def __init__(self):
        self.__headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
                   'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
                   'X-EBAY-SOA-SECURITY-APPNAME': config.key,
                   'Content-Type': 'text/xml'}
        self.__paginationInput = {'entriesPerPage': '20', 'pageNumber': '1'}
        self.__outputSelector = ['SellerInfo']
        self.sort = None
        self.result = None

    def __findItemsByKeywords__(self,keywords):
        root = ET.Element("findItemsByKeywords",
                             xmlns="http://www.ebay.com/marketplace/search/v1/services")

        keywords_elem = ET.SubElement(root, "keywords")
        keywords_elem.text = keywords

        # outputSelector is a list
        if self.__outputSelector:
            for item in self.__outputSelector:
                outputSelector_elem = ET.SubElement(root, "outputSelector")
                outputSelector_elem.text = item

        # paginationInput is a dict
        if self.__paginationInput:
            paginationInput_elem = ET.SubElement(root, "paginationInput")
            for key in self.__paginationInput:
                key_elem = ET.SubElement(paginationInput_elem, key)
                key_elem.text = self.__paginationInput[key]

        # sortOrder
        if self.sort:
            sortOrder_elem = ET.SubElement(root, "sortOrder")
            sortOrder_elem.text = self.sort
        return ET.tostring(root)

    def request(self,keywords):
        xml = self.__findItemsByKeywords__('pen')
        s = requests.post('http://svcs.ebay.com/services/search/FindingService/v1', data=xml, headers=self.__headers)
        self.result = BytesIO(s.content)
