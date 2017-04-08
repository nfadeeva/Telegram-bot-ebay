class ResponseParser(object):

    def __init__(self, xmldoc, sort, score, solds):
        self.__sort = sort
        self.__score = score
        self.__solds = solds
        self.__xmldoc = xmldoc

    def parse_xml(self, tag):
        """Get the __xmldoc and tag and return list of elements"""

        res = []
        for element in self.__xmldoc.getElementsByTagName(tag):
            res.append(element.firstChild.nodeValue)
        return res

    def parse_sellerInfo(self):
        for element in self.__xmldoc.getElementsByTagName('sellerInfo'):
            element = element.firstChild
            print(element.localName, element.firstChild.nodeValue)
            while element.nextSibling:
                element = element.nextSibling
                print(element.localName, element.firstChild.nodeValue)
            print()

    def parse_request(self):
        if (self.__sort):
            urls = self.parse_xml('viewItemURL')
            scores = self.parse_xml('feedbackScore')
            rating = self.parse_xml('positiveFeedbackPercent')
            items = list(zip(urls,scores,rating))
            print(items)
            items.sort(key = lambda x: x[1], reverse=True)
        if (self.__score.isdigit()):
            items = list(filter(lambda x: (int)(x[1]) >= (int)(self.__score), items))
        if (self.__solds.isdigit()):
            items = list(filter(lambda x: (int)(x[1]) >= (int)(self.__solds), items))
        ###WILL BE FIXED
        else:
            return self.parse_xml('viewItemURL')
        print(items)
        return items