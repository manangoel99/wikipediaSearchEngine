import os
import re
from collections import defaultdict
from heapq import heappop, heappush

from tqdm import tqdm


def tokenize(data):
    data = data.encode("ascii", errors="ignore").decode()
    data = re.sub(r'http[^\ ]*\ ', r' ', data)  # removing urls
    data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;',
                  r' ', data)  # removing html entities
    data = re.sub(
        r'\—|\%|\$|\'|\||\.|\*|\[|\]|\:|\;|\,|\{|\}|\(|\)|\=|\+|\-|\_|\#|\!|\`|\"|\?|\/|\>|\<|\&|\\|\u2013|\n',
        r' ',
        data)  # removing special characters
    return data.split()


class DocCleaner():
    """Class to preprocess and clean each article"""
    def __init__(self, stopwords, stemmer):
        """
        Constructor for the article content handler
            Parameters:
                stopwords (list): List of all stopwords in the corpus
                stemmer   (Stemmer): Stemmer for preprocessing of the text 
        """
        self.stopwords = stopwords
        self.stemmer = stemmer

    def removeStopWords(self, data):
        return [w for w in data if w not in self.stopwords]

    def cleanUp(self, text):
        data = tokenize(text)
        data = self.removeStopWords(data)
        data = self.stemmer.stemWords(data)

        return data

    def cleanTitle(self, text):
        return self.cleanUp(text)

    def cleanBody(self, text):
        data = re.sub(r'\{\{.*\}\}', r' ', text)
        return self.cleanUp(data)

    def cleanInfobox(self, text):
        data = text.split('\n')
        flag = False
        info = []

        for line in data:
            if re.match(r'\{\{infobox', line):
                flag = True
                info.append(re.sub(r'\{\{infobox(.*)', r'\1', line))
            elif flag:
                if line == '}}':
                    flag = False
                    continue
                info.append(line)
        return self.cleanUp(' '.join(info))

    def cleanReferences(self, text):
        data = text.split('\n')
        refs = []
        for line in data:
            if re.search(r'<ref', line):
                refs.append(
                    re.sub(
                        r'.*title[\ ]*=[\ ]*([^\|]*).*',
                        r'\1',
                        line))
        return self.cleanUp(' '.join(refs))

    def cleanCategories(self, text):
        data = text.split('\n')
        categories = []
        for line in data:
            if re.match(r'\[\[category', line):
                categories.append(
                    re.sub(
                        r'\[\[category:(.*)\]\]',
                        r'\1',
                        line))

        return self.cleanUp(' '.join(categories))

    def cleanLinks(self, text):
        data = text.split('\n')
        links = []
        for line in data:
            if re.match(r'\*[\ ]*\[', line):
                links.append(line)

        return self.cleanUp(' '.join(links))

    def cleanPart2(self, data):
        return self.cleanReferences(data), self.cleanLinks(
            data), self.cleanCategories(data)

    def cleanPart1(self, data, title):
        return self.cleanTitle(title), self.cleanBody(
            data), self.cleanInfobox(data)

    def processText(self, ID, text, title):
        text = text.lower()  # Case Folding
        data = text.split('==references==')

        references = []
        links = []
        categories = []
        if len(data) == 1:
            data = text.split('== references == ')
        else:
            references, links, categories = self.cleanPart2(data[1])
        title, body, info = self.cleanPart1(data[0], title.lower())

        return title, body, info, categories, links, references


class FieldWriter():
    """Class to write the inverted index for a particular field to a file"""
    def __init__(self, type):
        """
        Constructor
            Parameters:
                type (string) : Name of the field (t,b,c,l,r,i)
        """
        self.data = list()
        self.offset = list()
        self.prev = 0
        self.type = type

    def update(self, string, length_doc):
        self.data.append(string)
        self.prev += len(string) + 1
        self.offset.append(str(self.prev) + ' ' + str(length_doc))

    def write(self, finalCount):
        filename = os.path.join(
            "./inverted_index",
            "{0}{1}.txt".format(
                self.type,
                finalCount))
        with open(filename, 'w') as f:
            f.write('\n'.join(self.data))

        filename = os.path.join(
            './inverted_index',
            "offset_{0}{1}.txt".format(
                self.type,
                finalCount))
        with open(filename, 'w') as f:
            f.write('\n'.join(self.offset))


def writeIntoFile(index, dictID, fileCount, titleOffset):
    prevTitleOffset = titleOffset
    data = []
    for key in sorted(index.keys()):
        postings = index[key]
        string = key + ' ' + ' '.join(postings)
        data.append(string)

    filename = os.path.join(
        './inverted_index',
        'index{0}.txt'.format(fileCount))
    with open(filename, 'w') as f:
        f.write('\n'.join(data))

    data = []
    dataOffset = []
    for key in sorted(dictID):
        temp = ' '.join([str(key), dictID[key].strip()])
        data.append(temp)
        dataOffset.append(str(prevTitleOffset))
        prevTitleOffset += len(temp) + 1

    filename = os.path.join('./inverted_index', 'title.txt')
    with open(filename, 'a') as f:
        f.write('\n'.join(data))
        f.write('\n')

    filename = os.path.join('./inverted_index', 'titleOffset.txt')
    with open(filename, 'a') as f:
        f.write('\n'.join(dataOffset))
        f.write('\n')

    return prevTitleOffset


def writeFinalIndex(data, finalCount, offsetSize):
    """
    Write the final inverted index to a file from the intermediate files.
        Parameters:
            data (list) : Posting list
            finalCount (int) : Number of files
            offsetSize (int) : The offset from the beginning of the file
        Returns:
            finalCount (int)
            offsetSize (int)
    """
    information = {
        'title': defaultdict(dict),
        'body': defaultdict(dict),
        'info': defaultdict(dict),
        'category': defaultdict(dict),
        'link': defaultdict(dict),
        'reference': defaultdict(dict)
    }
    patterns = {
        'title': r'.*t([0-9]*).*',
        'body': r'.*b([0-9]*).*',
        'info': r'.*i([0-9]*).*',
        'category': r'.*c([0-9]*).*',
        'link': r'.*l([0-9]*).*',
        'reference': r'.*r([0-9]*).*'
    }
    fieldWriters = {
        'title': FieldWriter('t'),
        'body': FieldWriter('b'),
        'info': FieldWriter('i'),
        'category': FieldWriter('c'),
        'link': FieldWriter('l'),
        'reference': FieldWriter('r')
    }
    distWords = list()
    offset = list()
    for key in tqdm(sorted(data.keys())):
        docs = data[key]
        temp = []
        for idx, posting in enumerate(docs):
            ID = re.sub(r'.*d([0-9]*).*', r'\1', posting)

            for k in patterns.keys():
                temp = re.sub(patterns[k], r'\1', posting)
                if temp != posting:
                    information[k][key][ID] = float(temp)

        string = "{0} {1} {2}".format(key, finalCount, len(docs))
        distWords.append(string)
        offset.append(str(offsetSize))
        offsetSize += len(string) + 1

    for key in tqdm(sorted(data.keys())):
        for k in information.keys():
            if key in information[k]:
                string = key + ' '
                docs = information[k][key]
                docs = sorted(docs, key=docs.get, reverse=True)
                for doc in docs:
                    string += doc + ' ' + str(information[k][key][doc]) + ' '
                fieldWriters[k].offset.append(
                    str(fieldWriters[k].prev) + " " + str(len(docs)))
                fieldWriters[k].prev += len(string) + 1
                fieldWriters[k].data.append(string)

    for k in fieldWriters.keys():
        fieldWriters[k].write(finalCount)
    filename = os.path.join('./inverted_index', 'vocab.txt')
    with open(filename, 'a') as f:
        f.write('\n'.join(distWords))
        f.write('\n')

    with open(os.path.join('./inverted_index', 'offset.txt'), 'a') as f:
        f.write('\n'.join(offset))
        f.write('\n')

    return finalCount + 1, offsetSize


def mergeFiles(fileCount):
    words = defaultdict()
    files = defaultdict()
    top = defaultdict()

    flag = [False] * fileCount
    data = defaultdict(list)
    heap = list()
    finalCount = 0
    offsetSize = 0

    for i in range(fileCount):
        filename = os.path.join('./inverted_index', 'index{0}.txt'.format(i))
        files[i] = open(filename, 'r')
        flag[i] = True
        top[i] = files[i].readline().strip()
        words[i] = top[i].split()
        if words[i][0] not in heap:
            heappush(heap, words[i][0])

    count = 0
    while any(flag):
        temp = heappop(heap)
        count += 1

        if count % 100000 == 0:
            oldFileCount = finalCount
            finalCount, offsetSize = writeFinalIndex(
                data, finalCount, offsetSize)
            if not (oldFileCount == finalCount):
                data = defaultdict(list)

        for i in range(fileCount):
            if flag[i]:
                if words[i][0] == temp:
                    data[temp] += words[i][1:]
                    top[i] = files[i].readline().strip()
                    if len(top[i]) == 0:
                        flag[i] = False
                        files[i].close()
                    elif top[i] != '':
                        words[i] = top[i].split()
                        if words[i][0] not in heap:
                            heappush(heap, words[i][0])
    finalCount, offsetSize = writeFinalIndex(data, finalCount, offsetSize)
