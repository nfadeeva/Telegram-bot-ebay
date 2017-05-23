from collections import OrderedDict
from collections import namedtuple


class ResponseParser(object):
    """Sort items received from eBay"""

    def __init__(self, xmldocs, rating, feedback, sort):
        self.__rating = rating
        self.__feedback = feedback
        self.__xmldocs = xmldocs
        self.__sort = sort

    def parse_xml(self, tag):
        """Get the xmldoc and tag and return list of elements"""

        res = []
        for xmldoc in self.__xmldocs:
            for element in xmldoc.getElementsByTagName(tag):
                res.append(element.firstChild.nodeValue)
        return res

    @property
    def items(self):
        urls = self.parse_xml('viewItemURL')
        print(len(urls))
        feedback = self.parse_xml('feedbackScore')
        listingtype = self.parse_xml('listingType')
        rating = self.parse_xml('positiveFeedbackPercent')
        price = self.parse_xml('currentPrice')
        shipping = self.parse_xml('shippingServiceCost')
        titles = self.parse_xml('title')
        imgs = self.parse_xml('galleryURL')
        item = namedtuple('Item', ['url', 'title', 'feedback', 'rating', 'price', 'shipping', 'img', 'listingtype'], verbose=True)
        # to avoid duplicates because of reload pages while making request
        items = list(zip(urls, titles, feedback, rating, price, shipping, imgs, listingtype))
        items = list(OrderedDict.fromkeys(items))
        items = map(lambda x: item(*x), items)
        if self.__rating:
            items = list(filter(lambda x: float(x.rating) >= int(self.__rating), items))
        if self.__feedback:
            items = list(filter(lambda x: int(x.feedback) >= int(self.__feedback), items))
        if self.__sort == 'Price Plus Shipping Lowest':
            items = sorted(items, key = lambda x: float(x.price) + float(x.shipping))
        return items
