import os
import re
import sys
import xml.sax
from collections import defaultdict
from heapq import heappop, heappush

from nltk.corpus import stopwords
from Stemmer import Stemmer
from tqdm import tqdm

from ParsingHandler import WikiHandler
from utils import (DocCleaner, FieldWriter, mergeFiles, tokenize,
                   writeFinalIndex, writeIntoFile)

if __name__ == '__main__':
    parser = xml.sax.make_parser()
    stemmer = Stemmer('english')
    stopWords = set(stopwords.words('english'))

    handler = WikiHandler(stopWords, stemmer)

    parser.setContentHandler(handler)

    xmlFolder = sys.argv[1]
    filenames = [os.path.join(xmlFolder, i) for i in os.listdir(xmlFolder)]

    if not os.path.exists('./inverted_index'):
        os.mkdir('./inverted_index')

    for xmlFileName in filenames:
        parser.parse(xmlFileName)

    with open('./inverted_index/fileNumbers.txt', 'w') as f:
        f.write(str(handler.pageCount))

    handler.offset = writeIntoFile(
        handler.indexMap,
        handler.dictID,
        handler.fileCount,
        handler.offset)

    handler.indexMap = defaultdict(list)
    handler.dictID = defaultdict()
    handler.fileCount += 1

    mergeFiles(handler.fileCount)
