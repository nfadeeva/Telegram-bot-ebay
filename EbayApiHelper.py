import requests
from io import BytesIO
import xml.etree.ElementTree as ET
import config
import concurrent.futures
import time
from collections import OrderedDict
class EbayApiHelper(object):
    """
    This class is for making xml request and get xml response
    """

    def __init__(self, keywords, request,sort=None, page = '1'):

        self.__headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
                   'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
                   'X-EBAY-SOA-SECURITY-APPNAME': config.key,
                   'Content-Type': 'text/xml'}
        self.__pagination_input = {'entriesPerPage': '100', 'pageNumber': page}
        self.__output_selector = ['SellerInfo']
        self.itemFilter = OrderedDict([('name', 'listingType'), ('value','FixedPrice')])

        self.__keywords = keywords
        self.__sort = sort
        self.__request = request

    def createXml(self, page):
        """
        returns xml request
        """
        keywords = self.__keywords;
        root = ET.Element("findItemsByKeywords",
                             xmlns="http://www.ebay.com/marketplace/search/v1/services")

        keywords_elem = ET.SubElement(root, "keywords")
        keywords_elem.text = keywords

        if self.itemFilter:
            itemFilter_elem = ET.SubElement(root, "itemFilter")
            for key in self.itemFilter:
                key_elem = ET.SubElement(itemFilter_elem, key)
                key_elem.text = self.itemFilter[key]

        # outputSelector is a list
        if self.__output_selector:
            for item in self.__output_selector:
                outputSelector_elem = ET.SubElement(root, "outputSelector")
                outputSelector_elem.text = item

        # paginationInput is a dict
        pagination_input = {'entriesPerPage': '100', 'pageNumber': page}
        if pagination_input:
            paginationInput_elem = ET.SubElement(root, "paginationInput")
            for key in self.__pagination_input:
                key_elem = ET.SubElement(paginationInput_elem, key)
                key_elem.text = self.__pagination_input[key]

        # sortOrder
        if self.__sort:
            sort_elem = ET.SubElement(root, "sortOrder")
            sort_elem.text = self.__sort
        return ET.tostring(root).decode("utf-8")

    def request(self, page, pages):
        s = requests.post('http://svcs.ebay.com/services/search/FindingService/v1', data=self.createXml(page), headers=self.__headers)
        self.__request.progress+=int(1/pages);
        return BytesIO(s.content)

    def futures(self,pages):
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(self.request, page, pages): page for page in range(1, pages)}
        print("fin")
        return futures
