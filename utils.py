import re
import os
import heapq
from collections import defaultdict
import tqdm

class dataWriting():
    def __init__(self, type):
        self.data = []
        self.offset = []
        self.prev = 0
        self.type = type
    
    def addData(self, string, offset):
        self.data.append(string)
        self.offset.append("{0} {1}".format(self.prev, offset))
        self.prev += len(string) + 1
    
    def write(self, folderName, count):
        filename = os.path.join(folderName, "{0}{1}.txt".format(self.type, count))
        with open(filename, 'w') as f:
            print('\n'.join(self.data), file=f)
        
        filename = os.path.join(folderName, "offset_{0}{1}.txt".format(self.type, count))
        with open(filename, 'w') as f:
            print('\n'.join(self.offset), file=f)

def tokenize(data):
    data = data.encode('ascii', errors='ignore').decode()
    data = re.sub(r'http[^\ ]*\ ', r' ', data)
    data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data)
    data = re.sub(
        r'\—|\%|\$|\'|\||\.|\*|\[|\]|\:|\;|\,|\{|\}|\(|\)|\=|\+|\-|\_|\#|\!|\`|\"|\?|\/|\>|\<|\&|\\|\u2013|\n',
        r' ',
        data)
    return data.split()


def writeFinalIndex(data, finalCount, offsetSize, folderName):
    info = {
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
    infoData = {
        'title': dataWriting('t'),
        'body': dataWriting('b'),
        'info': dataWriting('i'),
        'category': dataWriting('c'),
        'link': dataWriting('l'),
        'reference': dataWriting('r')
    }

    distinctWords = []
    offset = []

    for key in tqdm.tqdm(sorted(data.keys())):
        docs = data[key]
        for idx, posting in enumerate(docs):
            id = re.sub(r'.*d([0-9]*).*', r'\1', posting)

            for k in info.keys():
                temp = re.sub(patterns[k], r'\1', posting)
                if temp != posting:
                    info[k][key][id] = float(temp)
        
        string = "{0} {1} {2}".format(key, finalCount, len(docs))
        distinctWords.append(string)
        offset.append(str(offsetSize))
        offsetSize += len(string) + 1
    
    for key in tqdm.tqdm(sorted(data.keys())):
        for k in info.keys():
            if key in info[k]:
                string = key + " "
                docs = sorted(info[k][key], key=info[k][key].get, reverse=True)
                for doc in docs:
                    string += "{0} {1} ".format(doc, info[k][key][doc])
                infoData[k].addData(string, len(docs))
    for k in infoData.keys():
        infoData[k].write(folderName, finalCount)
    
    with open(os.path.join(folderName, 'vocab.txt'), 'a') as f:
        print('\n'.join(distinctWords), file=f)
        print('\n', file=f)
    
    with open(os.path.join(folderName, 'offset.txt'), 'a') as f:
        print('\n'.join(offset), file=f)
        print('\n', file=f)
    
    return finalCount + 1, offsetSize

    


def mergeIndex(fileCount, folderName):
    words = defaultdict()
    files = defaultdict()
    top = defaultdict()
    flag = [True for i in range(fileCount)]
    data = defaultdict(list)
    heap = []
    finalCount = 0
    offsetSize = 0

    for i in range(fileCount):
        filename = os.path.join(folderName, "index{0}.txt".format(i))
        files[i] = open(filename, "r")

        top[i] = files[i].readline().strip()
        words[i] = top[i].split(":")
        if words[i][0] not in heap:
            heapq.heappush(heap, words[i][0])

    count = 0
    while any(flag):
        try:
            temp = heapq.heappop(heap)
        except:
            print(heapq)
        count += 1

        if count % 100000 == 0:
            oldFileCount = finalCount
            finalCount, offsetSize = writeFinalIndex(data, finalCount, offsetSize, folderName)
            if oldFileCount != finalCount:
                data = defaultdict(list)
        for i in range(fileCount):
            if flag[i]:
                if words[i][0] == temp:
                    data[temp].extend(words[i][1].split(" "))
                    top[i] = files[i].readline().strip()
                    if top[i] == '':
                        flag[i] = False
                        files[i].close()
                    else:
                        words[i] = top[i].split(":")
                        if words[i][0] not in heap:
                            heapq.heappush(heap, words[i][0])
    finalCount, offsetSize = writeFinalIndex(data, finalCount, offsetSize, folderName)


# def writeIndexToFile(index, dictID, fileNum, titleOffset, folderName):
#     prevTitleOffset = titleOffset
#     data = []
#     for key in sorted(index.keys()):
#         string = key + ':' + ' '.join(index[key])
#         data.append(string)

#     fileName = os.path.join(folderName, "index{0}.txt".format(fileNum))
#     with open(fileName, 'w') as f:
#         print('\n'.join(data), file=f)

#     data = []
#     dataOffset = []

#     for key in sorted(dictID):
#         string = ' '.join([str(key), dictID[key].strip()])
#         data.append(string)
#         dataOffset.append(str(prevTitleOffset))
#         prevTitleOffset += len(string) + 1

#     fileName = os.path.join(folderName, "title.txt")
#     with open(fileName, 'a') as f:
#         print('\n'.join(data), file=f)

#     fileName = os.path.join(folderName, "titleOffSet.txt")
#     with open(fileName, 'a') as f:
#         print('\n'.join(dataOffset), file=f)

#     return prevTitleOffset


class DocCleaner():
    def __init__(self, stemmer, stopWords):
        self.stemmer = stemmer
        self.stopWords = stopWords

    def removeStopWords(self, data):
        return [word for word in data if word not in self.stopWords]

    def cleanReferences(self, data):
        # data = data.split("\n")
        references = []
        for line in data:
            if "<ref" in line:
                references.append(
                    re.sub(
                        r'.*title[\ ]*=[\ ]*([^\|]*).*',
                        r' ',
                        line))

        data = tokenize(' '.join(references))
        data = self.removeStopWords(data)
        data = self.stemmer.stemWords(data)

        return data

    def cleanTitle(self, title):
        title = tokenize(title)
        title = self.removeStopWords(title)
        title = self.stemmer.stemWords(title)
        return title

    def cleanInfoBox(self, data):
        data = data.split("\n")
        flag = False
        box = []
        for line in data:
            if 'infobox' in line:
                flag = True
                box.append(re.sub(r'\{\{infobox(.*)', r' ', line))
            elif flag:
                if '}}' in line:
                    flag = False
                    continue
                box.append(line)
        data = tokenize(' '.join(box))
        data = self.removeStopWords(data)
        data = self.stemmer.stemWords(data)

        return data

    def cleanBody(self, text):
        data = re.sub(r'\{\{.*\}\}', r' ', text)
        data = tokenize(data)
        data = self.removeStopWords(data)
        data = self.stemmer.stemWords(data)

        return data

    def cleanExternalLinks(self, data):
        # data = data.split('\n')
        links = []
        for line in data:
            if re.match(r'\*[\ ]*\[', line):
                links.append(line)

        data = tokenize(' '.join(links))
        data = self.removeStopWords(data)
        data = self.stemmer.stemWords(data)

        return data

    def cleanCategories(self, data):
        # data = data.split("\n")
        categories = []
        for idx in range(len(data)):
            line = data[idx]
            if re.match(r'\[\[category', line):
                categories.append(
                    re.sub(
                        r'\[\[category:(.*)\]\]',
                        r'\1',
                        line))
        data = tokenize(' '.join(categories))
        data = self.removeStopWords(data)
        data = self.stemmer.stemWords(data)
        return data

    def cleanData(self, ID, text, title):
        text = text.lower()
        title = title.lower()
        references = []
        links = []
        categories = []
        data = text.split("==references==")

        if len(data) == 1:
            data = text.split('== references == ')
        else:
            references = self.cleanReferences(data[1].split("\n"))
            links = self.cleanExternalLinks(data[1].split("\n"))
            categories = self.cleanCategories(data[1].split("\n"))
        title = self.cleanTitle(title)
        infobox = self.cleanInfoBox(data[0])
        body = self.cleanBody(data[0])
        return title, body, infobox, references, links, categories
