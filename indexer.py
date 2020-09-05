import xml.sax
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from collections import defaultdict
import re
from ParsingHandler import WikiHandler
from utils import *
from Stemmer import Stemmer
import sys
import os
stemmer = Stemmer('english')
stopWords = list(set(stopwords.words('english')))


if __name__ == '__main__':
    parser = xml.sax.make_parser()
    handler = WikiHandler(stemmer, stopWords, "./inverted_index")
    parser.setContentHandler(handler)
    filenames = [
        "/home/manan/dump/enwiki-20200801-pages-articles-multistream1.xml-p1p30303",
        "/home/manan/dump/enwiki-20200801-pages-articles-multistream2.xml-p30304p88444",
        # "/home/manan/dump/enwiki-20200801-pages-articles-multistream3.xml-p88445p200509",
    ]
    for xmlFileName in filenames:
        parser.parse(xmlFileName)

    print("\nFinished Parsing")
    handler.offset = writeIndexToFile(
        handler.indexMap,
        handler.dictID,
        handler.fileCount,
        handler.offset,
        handler.folderName)
    handler.reset()
    handler.fileCount += 1
    print(handler.fileCount, end='\n')
    mergeIndex(handler.fileCount, "./inverted_index")
