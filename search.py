import math
import operator
import os
import re
import sys
import time
from collections import Counter, defaultdict

from nltk.corpus import stopwords
from Stemmer import Stemmer

from utils import tokenize

stopWords = set(stopwords.words('english'))
stemmer = Stemmer('english')


def fileBinarySearch(low, high, offset, word, f, ty='str'):
    """
    Perform a binary search on the file to find if the word is in the file
        Parameters:
            low (int) : Starting point of search
            high (int) : End point of search
            offset (int) : Since the search is on a file, we need offset to seek the pointer to that position
            word (str) : Word being searched for
            f (file) : File in which searching is being done
            ty (str) : Type of data being searched (int/str)
        Returns
            Posting list of the word
            offset to the position of the word in the file
    """
    while high > low:
        mid = int((low + high) / 2)

        f.seek(offset[mid])
        pointer = f.readline().strip().split()
        if not (ty != 'str'):
            if word == pointer[0]:
                return pointer[1:], mid
            elif word < pointer[0]:
                high = mid
            else:
                low = mid + 1
        elif not (ty != 'int'):
            if int(word) == int(pointer[0]):
                return pointer[1:], mid
            elif int(word) < int(pointer[0]):
                high = mid
            else:
                low = mid + 1
    return [], -1


def findDocs(filename, fileNo, field, word, fieldFile):
    fieldOffset = []
    docFreq = []
    fieldOffsetFileName = os.path.join(
        "./inverted_index",
        "offset_{0}{1}.txt".format(
            field,
            fileNo))
    with open(fieldOffsetFileName, 'r') as f:
        lines = f.readlines()
        for line in lines:
            offset, df = line.strip().split()
            docFreq += [int(df)]
            fieldOffset += [int(offset)]
    t = fileBinarySearch(
        0, len(fieldOffset), fieldOffset, word, fieldFile)
    docList, mid = t[0], t[1]
    return docList, docFreq[mid]


def fieldQuery(queryDict, vocabFile, offset):
    docList = defaultdict(dict)
    docFreq = defaultdict()

    for key in queryDict.keys():
        for w in queryDict[key]:
            word = w
            field = key
            docs, _ = fileBinarySearch(0, len(offset), offset, word, vocabFile)
            if len(docs) > 0:
                fileNo = docs[0]
                filename = os.path.join(
                    "./inverted_index",
                    "{0}{1}.txt".format(
                        field,
                        fileNo))
                with open(filename, "r") as fieldFile:

                    t = findDocs(
                        filename, fileNo, field, word, fieldFile)
                    returnedList, df = t[0], t[1]
                docList[word][field] = returnedList
                docFreq[word] = df
    return docList, docFreq


def simpleQuery(words, vocabFile, offset):
    docList, docFreq = defaultdict(dict), defaultdict()
    for word in words:
        docs, _ = fileBinarySearch(0, len(offset), offset, word, vocabFile)
        if len(docs) > 0:
            fileNo, docFreq[word] = docs[0], docs[1]
            for field in ['t', 'i', 'b', 'c', 'l', 'r']:
                filename = os.path.join(
                    "./inverted_index",
                    "{0}{1}.txt".format(
                        field,
                        fileNo))
                with open(filename, 'r') as f:
                    t = findDocs(filename, fileNo, field, word, f)
                    returnedList, _ = t[0], t[1]
                    docList[word][field] = returnedList
    return docList, docFreq


def rank(results, docFreq, nfiles):
    docs = defaultdict(float)
    queryIdf = {}

    scores = {
        't': 0.25, 'b': 0.25, 'i': 0.20,
        'c': 0.10, 'r': 0.05, 'l': 0.05
    }

    for key in docFreq:
        f = float(docFreq[key])
        queryIdf[key] = math.log(
            (float(nfiles) - f + 0.5) / (f + 0.5))
        docFreq[key] = math.log(float(nfiles) / f)

    for word in results:
        postingList = results[word]
        for field in postingList:
            if len(field) > 0:
                post = postingList[field]
                factor = scores[field]
                for i in range(0, len(post), 2):
                    docs[post[i]] += float(factor * (1 + \
                                           math.log(float(post[i + 1]))) * docFreq[word])
    return docs


def search(*arguments):
    print("Loading Files")
    outfile = open("./query_op.txt", 'w')
    with open(arguments[0], 'r') as f:
        queries = f.readlines()
    with open("./inverted_index/titleOffset.txt", 'r') as f:
        titleOffSet = [int(line.strip()) for line in f]
    with open("./inverted_index/offset.txt", 'r') as f:
        offset = []
        for line in f.readlines():
            try:
                offset.append(int(line.strip()))
            except BaseException:
                continue
    vocabFile = open("./inverted_index/vocab.txt", 'r')
    titleFile = open("./inverted_index/title.txt", 'r')
    with open("./inverted_index/fileNumbers.txt", 'r') as f:
        nFiles = int(f.read().strip())
    key_words = ['t:', 'b:', 'i:', 'c:', 'r:', 'l:']
    print("Starting Queries")
    numQueries = 0
    for query in queries:
        startTime = time.time()
        numQueries += 1
        query = query.strip().lower()
        numResults, query = query.split(",")
        query = query.strip()
        numResults = int(numResults)
        queryType = "Plain"
        for w in key_words:
            if w in query:
                queryType = "Field"
                break

        if queryType == "Field":
            q = re.split("(t:)|(b:)|(i:)|(c:)|(r:)|(l:)", query)
            q = [i.strip() for i in q if i is not None and i != ""]
            queryDict = defaultdict(list)
            for idx in range(0, len(q), 2):
                data = tokenize(q[idx + 1].lower())
                data = [w for w in data if w not in stopWords]
                data = stemmer.stemWords(data)
                queryDict[q[idx].split(":")[0]].extend(data)
            results, docFreq = fieldQuery(queryDict, vocabFile, offset)
            results = rank(results, docFreq, nFiles)
        else:
            q = tokenize(query)
            q = [w for w in q if w not in stopWords]
            q = stemmer.stemWords(q)
            t = simpleQuery(q, vocabFile, offset)
            results, docFreq = t[0], t[1]
            results = rank(results, docFreq, nFiles)

        if len(results) > 0:
            results = sorted(results, key=results.get, reverse=True)
            results = results[:numResults]
            for key in results:
                title, _ = fileBinarySearch(
                    0, len(titleOffSet), titleOffSet, key, titleFile, 'int')
                print(','.join([key] + [' '.join(title)]), file=outfile)
        endTime = time.time()
        print(
            "{0}, {1}".format(
                endTime - startTime,
                (endTime - startTime) / numResults),
            file=outfile)

        print('\n', file=outfile)
    outfile.close()


if __name__ == '__main__':
    search(sys.argv[1])
