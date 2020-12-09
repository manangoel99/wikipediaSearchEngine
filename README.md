Wikipedia Search Engine
========================
This repository contains my implementation of a search engine on the over the 65GB Wikipedia dump. The article data is stored as xml files which is then parsed and used to create an inverted index. The inverted index is then used for querying.

# Setting up the repository
The code is written in python3 and uses the nltk and PyStemmer libraries for preprocessing the text. Set up a new virtual environment with python3.7. The choice of tool for the virtualenv is left to the user. Run the following commands

```
    pip install PyStemmer nltk
```

# Creating the inverted index
In order to create the inverted index, first download the [Wikipedia Dump](https://dumps.wikimedia.org/enwiki/20200801/enwiki-20200801-pages-articles-multistream1.xml-p1p30303.bz2) and extract.

In order to generate the inverted index run

```
python indexer.py <path to folder with all xml files>
```

This creates the directory ```inverted_index``` which contains the files.

# Querying
The search engine supports 2 types of queries: General queries and Field queries. General queries search across all the tokens whether it may be in any field of the article. In case of Field queries, the presence of the token is searched only in the specific field. The returned results are then ranked using the TF-IDF scheme.

General Query

```
python search.py "cricket world cup 2019"
```

Field Query

```
python search.py "t:World Cup b:2019 c:cricket"
```
The supported fields are t (title), b(body), c(category), i(infobox), r(references) and l(links).