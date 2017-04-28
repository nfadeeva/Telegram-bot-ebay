import requests
from io import BytesIO
import xml.etree.ElementTree as ET
import config
import concurrent.futures
import time
from collections import OrderedDict
class EbayApiHelper(object):
    """
    This class makes xml request and gets xml response
    """

    def __init__(self, keywords, request,sort=None, page = '1'):

        self.__headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
                   'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
                   'X-EBAY-SOA-SECURITY-APPNAME': config.key,
                   'Content-Type': 'text/xml'}
        self.__output_selector = ['SellerInfo']
        self.__itemFilter = {'name': 'listingType', 'value': 'FixedPrice'}

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

        #itemFilter is a dict
        if self.__itemFilter:
            itemFilter_elem = ET.SubElement(root, "__itemFilter")
            for key in self.__itemFilter:
                key_elem = ET.SubElement(itemFilter_elem, key)
                key_elem.text = self.__itemFilter[key]

        # outputSelector is a list
        if self.__output_selector:
            for item in self.__output_selector:
                outputSelector_elem = ET.SubElement(root, "outputSelector")
                outputSelector_elem.text = item

        # paginationInput is a dict
        pagination_input = {'entriesPerPage': '100', 'pageNumber': page}
        if pagination_input:
            paginationInput_elem = ET.SubElement(root, "paginationInput")
            for key in pagination_input:
                key_elem = ET.SubElement(paginationInput_elem, key)
                key_elem.text = pagination_input[key]

        # sortOrder
        if self.__sort:
            sort_elem = ET.SubElement(root, "sortOrder")
            sort_elem.text = self.__sort
        return ET.tostring(root).decode("utf-8")

    def request(self, page, pages):
        s = requests.post('http://svcs.ebay.com/services/search/FindingService/v1', data=self.createXml(str(page)), headers=self.__headers)
        self.__request.progress += int(1/pages*100)
        return BytesIO(s.content)

    def futures(self,pages):
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(self.request, page, pages): page for page in range(1, pages)}
        return futures
