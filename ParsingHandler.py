import time
import xml.sax
from collections import defaultdict

from utils import DocCleaner, writeIntoFile


class WikiHandler(xml.sax.ContentHandler):
    """
    Content Handler class to deal with the article data found in the xml files
    """
    def __init__(self, stopwords, stemmer):
        """
        Constructor for the article content handler
            Parameters:
                stopwords (list): List of all stopwords in the corpus
                stemmer   (Stemmer): Stemmer for preprocessing of the text 
        """
        self.CurrentData = ''
        self.title = ''
        self.text = ''
        self.ID = ''
        self.idFlag = 0
        self.stopwords = stopwords
        self.stemmer = stemmer
        self.pageCount = 0
        self.fileCount = 0
        self.indexMap = defaultdict(list)
        self.dictID = defaultdict()
        self.offset = 0
        self.startTime = time.time()

    def createIndex(self, **details):
        """
        Takes article details as input and adds them to the index and writes to a file after every 10,000 articles.
            Parameters:
                title (list) : List of title tokens
                body (list) : List of body tokens
                info (list) : List of info tokens
                categories (list) : List of categories tokens
                links (list) : List of links tokens
                references (list) : List of references tokens
        """
        ID = self.pageCount
        words = defaultdict(int)
        k = defaultdict()
        for key in details.keys():
            k[key] = None

        for key in k.keys():
            d = defaultdict(int)
            for word in details[key]:
                d[word] += 1
                words[word] += 1
            k[key] = d

        title = k['title']
        body = k['body']
        info = k['info']
        categories = k['categories']
        links = k['links']
        references = k['references']

        for word in words.keys():
            t, b, i, c, l, r = title[word], body[word], info[word], categories[word], links[word], references[word]

            string = 'd' + str(ID)
            if t > 0:
                string += 't' + str(t)
            if b > 0:
                string += 'b' + str(b)
            if i > 0:
                string += 'i' + str(i)
            if c > 0:
                string += 'c' + str(c)
            if l > 0:
                string += 'l' + str(l)
            if r > 0:
                string += 'r' + str(r)

            self.indexMap[word].append(string)
        self.pageCount += 1
        if self.pageCount % 10000 == 0:
            self.offset = writeIntoFile(
                self.indexMap, self.dictID, self.fileCount, self.offset)
            self.indexMap = defaultdict(list)
            self.dictID = defaultdict()
            self.fileCount += 1

    def startElement(self, tag, attributes):
        """Callback method to xml handler"""
        self.CurrentData = tag
        if tag == 'page':
            print(self.pageCount, time.time() - self.startTime, end='\r')

    def endElement(self, tag):
        """Callback method to xml handler"""
        if tag == 'page':
            d = DocCleaner(self.stopwords, self.stemmer)
            self.dictID[self.pageCount] = self.title.strip().encode(
                "ascii", errors="ignore").decode()
            title, body, info, categories, links, references = d.processText(
                self.pageCount, self.text, self.title)
            # i = Indexer( )
            self.createIndex(
                title=title,
                body=body,
                info=info,
                categories=categories,
                links=links,
                references=references)
            self.CurrentData = ''
            self.title = ''
            self.text = ''
            self.ID = ''
            self.idFlag = 0

    def characters(self, content):
        """Callback method to xml handler"""
        if self.CurrentData == 'title':
            self.title += content
        elif self.CurrentData == 'text':
            self.text += content
        elif self.CurrentData == 'id' and self.idFlag == 0:
            self.ID = content
            self.idFlag = 1
