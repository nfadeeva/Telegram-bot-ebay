from collections import OrderedDict


class ResponseParser(object):
    """Sort items received from eBay"""

    def __init__(self, xmldocs, sort, score, solds):
        self.__sort = sort
        self.__score = score
        self.__solds = solds
        self.__xmldocs = xmldocs

    def parse_xml(self, tag):
        """Get the xmldoc and tag and return list of elements"""

        res = []
        for xmldoc in self.__xmldocs:
            for element in xmldoc.getElementsByTagName(tag):
                res.append(element.firstChild.nodeValue)
        return res

    def parse_request(self):
        if self.__sort:
            urls = self.parse_xml('viewItemURL')
            scores = self.parse_xml('feedbackScore')
            rating = self.parse_xml('positiveFeedbackPercent')
            fixed = self.parse_xml('listingType')
            # to avoid duplicates because of reload pages while making request
            items = list(zip(urls,scores,rating,fixed))
            # api doesn't work, so filter items by myself
            items = filter(lambda x: x[3]=='FixedPrice',items)
            items = list(OrderedDict.fromkeys(items))
            items.sort(key = lambda x: x[1], reverse=True)
        if self.__score.isdigit():
            items = list(filter(lambda x: float(x[2]) >= int(self.__score), items))
        if self.__solds.isdigit():
            items = list(filter(lambda x: int(x[1]) >= int(self.__solds), items))
        # WILL BE FIXED
        else:
            return self.parse_xml('viewItemURL')
        print(len(items))
        # print(items)
        return items
