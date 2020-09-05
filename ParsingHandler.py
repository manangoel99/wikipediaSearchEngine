import xml.sax
from utils import DocCleaner, writeIndexToFile
from collections import defaultdict
import time


class WikiHandler(xml.sax.ContentHandler):
    def __init__(self, stemmer, stopWords, folderName):
        self.CurrentData = ''
        self.title = ''
        self.text = ''
        self.ID = ''
        self.idFlag = 0
        self.stemmer = stemmer
        self.stopWords = stopWords
        self.pageCount = 0
        self.indexMap = defaultdict(list)
        self.fileCount = 0
        self.dictID = {}
        self.offset = 0
        self.titles = list()
        self.stateDict = {
            "title": "",
            "body": "",
            "info": "",
            "categories": "",
            "links": "",
            "references": "",
        }
        self.cleaner = DocCleaner(self.stemmer, self.stopWords)
        self.startTime = time.time()
        self.fileNum = 0
        self.folderName = folderName
        print("Started Parsing")

    def reset(self):
        self.indexMap = defaultdict(list)
        self.dictID = {}

    def createIndex(self):
        ID = self.pageCount
        words = defaultdict(int)
        dictionary = {}
        for key in self.stateDict.keys():
            d = defaultdict(int)
            for word in self.stateDict[key]:
                d[word] += 1
                words[word] += 1
            dictionary[key] = d

        title = dictionary["title"]
        body = dictionary["body"]
        references = dictionary["references"]
        info = dictionary["info"]
        links = dictionary["links"]
        categories = dictionary["categories"]

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
            self.offset = writeIndexToFile(
                self.indexMap,
                self.dictID,
                self.fileCount,
                self.offset,
                self.folderName)
            self.reset()
            self.fileCount += 1

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == 'page':
            self.currentTime = time.time()
            print(
                "Page Number {0} Total Time {1}".format(
                    self.pageCount,
                    self.currentTime -
                    self.startTime),
                end='\r')

    def endElement(self, tag):
        if tag == 'page':
            self.dictID[self.pageCount] = self.title.strip().encode(
                'ascii', errors='ignore').decode()
            self.stateDict["title"], self.stateDict["body"], self.stateDict["info"], self.stateDict["references"], self.stateDict[
                "links"], self.stateDict["categories"] = self.cleaner.cleanData(0, self.text, self.title)
            self.titles.append(self.stateDict["title"])
            self.createIndex()
            self.CurrentData = ''
            self.title = ''
            self.text = ''
            self.ID = ''
            self.idFlag = 0

    def characters(self, content):
        if self.CurrentData == 'title':
            self.title += content
        elif self.CurrentData == 'text':
            self.text += content
        elif self.CurrentData == 'id' and self.idFlag == 0:
            self.ID = content
            self.idFlag = 1
