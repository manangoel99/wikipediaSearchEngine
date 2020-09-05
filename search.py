from nltk.corpus import stopwords
import re
import sys
import os
from collections import defaultdict, Counter
import operator
from Stemmer import Stemmer
import sys
from utils import tokenize

stopWords = set(stopwords.words('english'))
stemmer = Stemmer('english')


def search(arguments):
    invertedIndexDir = arguments[1]
    with open(os.path.join(invertedIndexDir, "vocab.txt"), 'r') as f:
        words = f.readlines()[0].split(',')
    with open(os.path.join(invertedIndexDir, "index.txt"), 'r') as f:
        index = f.readlines()
    with open(os.path.join(invertedIndexDir, "title.txt"), 'r') as f:
        titles = f.readlines()

    titleDict = {}
    for i in titles:
        k = i.split(" ")
        key = int(k[0])
        titleDict[key] = " ".join(k[1:]).strip()
    dataquery = " ".join(sys.argv[2:])
    words = words[:-1]
    key_words = ['t:', 'b:', 'i:', 'c:', 'r:', 'l:']
    queryType = "Plain"
    for w in key_words:
        if w in dataquery:
            queryType = "Field"
            break
    if queryType == "Field":
        query = re.split("(t:)|(b:)|(i:)|(c:)|(r:)|(l:)", dataquery)
        query = [i.strip() for i in query if i is not None and i != ""]
        queryDict = defaultdict(list)
        for idx in range(0, len(query), 2):
            data = tokenize(query[idx + 1].lower())
            data = [w for w in data if w not in stopWords]
            data = stemmer.stemWords(data)
            queryDict[query[idx].split(":")[0]].extend(data)
        docs = defaultdict(list)
        for key in queryDict.keys():
            for word in queryDict[key]:
                temp = index[words.index(word)].strip()
                temp = temp.split(":")
                temp = temp[1].split(" ")
                for idx in temp:
                    if key == 't':
                        if 't1' in idx:
                            docs[word].append(idx)
                    if key == 'b':
                        if 'b1' in idx:
                            docs[word].append(idx)
                    if key == 'i':
                        if 'i1' in idx:
                            docs[word].append(idx)
                    if key == 'c':
                        if 'c1' in idx:
                            docs[word].append(idx)
                    if key == 'r':
                        if 'r1' in idx:
                            docs[word].append(idx)
                    if key == 'l':
                        if 'l1' in idx:
                            docs[word].append(idx)
    elif queryType == 'Plain':
        data = dataquery.lower()
        data = tokenize(data)
        data = [w for w in data if w not in stopWords]
        data = stemmer.stemWords(data)
        docs = defaultdict(list)
        for word in data:
            temp = index[words.index(word)].strip()
            temp = temp.split(":")
            temp = temp[1].split(" ")
            for idx in temp:
                docs[word].append(idx)

    for key in docs.keys():
        print(
            "{0}:{1}".format(
                key,
                ",".join(
                    docs[key])),
            end='\n\n')


if __name__ == '__main__':
    search(sys.argv)
