import requests
from io import BytesIO
import xml.etree.ElementTree as ET
import config
import concurrent.futures


class EbayApiHelper(object):
    """Make xml request and get response from eBay"""

    def __init__(self, keywords, request, sort=None, page='1'):

        self.__headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
                   'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
                   'X-EBAY-SOA-SECURITY-APPNAME': config.key,
                   'Content-Type': 'text/xml'}
        self.__output_selector = ['SellerInfo']
        self.__item_filter = {'name': 'listingType', 'value': 'FixedPrice'}
        self.__keywords = keywords
        self.__sort = sort
        self.__request = request

    def create_xml(self, page_num):
        """Returns request in xml format"""

        keywords = self.__keywords
        root = ET.Element("findItemsByKeywords",
                             xmlns="http://www.ebay.com/marketplace/search/v1/services")

        keywords_elem = ET.SubElement(root, "keywords")
        keywords_elem.text = keywords

        # itemFilter is a dict
        if self.__item_filter:
            item_filter_elem = ET.SubElement(root, "itemFilter")
            for key in self.__item_filter:
                key_elem = ET.SubElement(item_filter_elem, key)
                key_elem.text = self.__item_filter[key]

        # outputSelector is a list
        if self.__output_selector:
            for item in self.__output_selector:
                output_selector_elem = ET.SubElement(root, "outputSelector")
                output_selector_elem.text = item

        # paginationInput is a dict
        pagination_input = {'entriesPerPage': '100', 'pageNumber': page_num}
        if pagination_input:
            pagination_input_elem = ET.SubElement(root, "paginationInput")
            for key in pagination_input:
                key_elem = ET.SubElement(pagination_input_elem, key)
                key_elem.text = pagination_input[key]

        # sortOrder is a string
        if self.__sort:
            sort_elem = ET.SubElement(root, "sortOrder")
            sort_elem.text = self.__sort
        return ET.tostring(root).decode("utf-8")

    def futures(self, pages):
        """Parallel request's post"""

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(self.request, page, pages): page for page in range(1, pages)}
        return futures

    def request(self, page, pages):
        s = requests.post('http://svcs.ebay.com/services/search/FindingService/v1', data=self.create_xml(str(page)),
                          headers=self.__headers)
        self.__request.progress += int(1/pages*100)
        return BytesIO(s.content)
