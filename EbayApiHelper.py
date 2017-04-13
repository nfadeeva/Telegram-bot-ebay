import requests
from io import BytesIO
import xml.etree.ElementTree as ET
import config

class EbayApiHelper(object):
    """
    This class is for making xml request and get xml response
    """

    def __init__(self, keywords, sort=None, page = '1'):

        self.__headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
                   'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
                   'X-EBAY-SOA-SECURITY-APPNAME': config.key,
                   'Content-Type': 'text/xml'}
        self.__pagination_input = {'entriesPerPage': '100', 'pageNumber': page}
        self.__output_selector = ['SellerInfo']
        self.__keywords = keywords
        self.__sort = sort

    def createXml(self):
        """
        returns xml request
        """
        keywords = self.__keywords;
        root = ET.Element("findItemsByKeywords",
                             xmlns="http://www.ebay.com/marketplace/search/v1/services")

        keywords_elem = ET.SubElement(root, "keywords")
        keywords_elem.text = keywords

        # outputSelector is a list
        if self.__output_selector:
            for item in self.__output_selector:
                outputSelector_elem = ET.SubElement(root, "outputSelector")
                outputSelector_elem.text = item

        # paginationInput is a dict
        if self.__pagination_input:
            paginationInput_elem = ET.SubElement(root, "paginationInput")
            for key in self.__pagination_input:
                key_elem = ET.SubElement(paginationInput_elem, key)
                key_elem.text = self.__pagination_input[key]

        # sortOrder
        if self.__sort:
            sort_elem = ET.SubElement(root, "sortOrder")
            sort_elem.text = self.__sort
        return ET.tostring(root).decode("utf-8")

    # def request(self):
    #     xml = self.__findItemsByKeywords__(self.__keywords)
    #     f = open('text.txt', 'wb');
    #     f.write(xml);
    #     s = requests.post('http://svcs.ebay.com/services/search/FindingService/v1', data=xml, headers=self.__headers)
    #     return BytesIO(s.content)