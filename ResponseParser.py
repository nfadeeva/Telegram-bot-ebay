from collections import OrderedDict
from collections import namedtuple

class ResponseParser(object):
    """Sort items received from eBay"""

    def __init__(self, xmldocs, rating, feedback):
        self.__rating = rating
        self.__feedback = feedback
        self.__xmldocs = xmldocs

    def parse_xml(self, tag):
        """Get the xmldoc and tag and return list of elements"""

        res = []
        for xmldoc in self.__xmldocs:
            for element in xmldoc.getElementsByTagName(tag):
                res.append(element.firstChild.nodeValue)
        return res

    def parse_request(self):
        urls = self.parse_xml('viewItemURL')
        scores = self.parse_xml('feedbackScore')
        rating = self.parse_xml('positiveFeedbackPercent')
        price = self.parse_xml('currentPrice')
        shipping = self.parse_xml('shippingServiceCost')
        titles = self.parse_xml('title')
        imgs = self.parse_xml('galleryURL')
        # to avoid duplicates because of reload pages while making request
        items = list(zip(urls, titles, rating, scores, price, shipping, imgs))
        Item = namedtuple('Item', ['url', 'title','rating','score','price','shipping','img'], verbose=True)
        items = list(OrderedDict.fromkeys(items))
        items = map(lambda x: Item(*x), items)
        if self.__rating:
            items = list(filter(lambda x: float(x.rating) >= int(self.__rating), items))
        if self.__feedback:
            items = list(filter(lambda x: int(x.score) >= int(self.__feedback), items))
        print(len(items))
        return items
