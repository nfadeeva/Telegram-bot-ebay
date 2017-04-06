class ResponseParser(object):

    def __init__(self, sort, num_items):
        self.result = None
        self.__sort = sort
        self.__num_items = num_items

    def parse_xml(xmldoc, tag):
        """Get the xmldoc and tag and return list of elements"""

        res = []
        for element in xmldoc.getElementsByTagName(tag):
            res.append(element.firstChild.nodeValue)
        return res

    def parse_sellerInfo(xmldoc):
        for element in xmldoc.getElementsByTagName('sellerInfo'):
            element = element.firstChild
            print(element.localName, element.firstChild.nodeValue)
            while element.nextSibling:
                element = element.nextSibling
                print(element.localName, element.firstChild.nodeValue)
            print()

