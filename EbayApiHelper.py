import requests
import re
import xml.etree.ElementTree as ET
import config
import concurrent.futures
import threading
from Utils import bot


class EbayApiHelper(object):
    """Make xml request and get response from eBay"""

    def __init__(self, keywords, request, sort, message):

        self.__headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
                   'X-EBAY-SOA-OPERATION-NAME': 'findItemsByKeywords',
                   'X-EBAY-SOA-SECURITY-APPNAME': config.key,
                   'Content-Type': 'text/xml'}
        self.__output_selector = ['SellerInfo']
        self.__item_filter = {'name': 'listingType', 'value': 'FixedPrice'}
        self.__keywords = keywords
        self.__sort = sort
        self.__request = request
        self.message = message
        self.lock = threading.Lock()

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
        pg = re.findall(r'<totalPages>(\d+)<',self.request(1,pages).decode())[0]
        pages = min(int(pg),pages)
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(self.request, page, pages): page for page in range(1, pages)}
        self.__request.progress = 0
        return futures


    def request(self, page, pages):
        s = requests.post('http://svcs.ebay.com/services/search/FindingService/v1', data=self.create_xml(str(page)),
                          headers=self.__headers)
        self.send(pages)
        return s.content

    def send(self, pages):
        self.lock.acquire()
        self.__request.progress += (1 / pages * 100)
        bot.edit_message_text(chat_id=self.message.chat.id, message_id=self.message.message_id,
                              text="Please, wait...\n"
                                   "{}% is done".format(int(self.__request.progress)))
        self.lock.release()

