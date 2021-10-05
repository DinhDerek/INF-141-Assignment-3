# HoloSearch

HoloSearch is our implementation of a search engine.  Developed by Derek Dinh and Tung Nguyen

## How it works
There are three main parts to the search engine: indexer.py, merge.py, and search.py

indexer.py:
index() goes through each JSON file in each folder of the DEV folder and grabs the text from the content.  The text is tokenized and stemmed before being indexed.  We used a SimHash library to remove duplicates and computed weights for each token that belonged in a special tag for a given JSON file.  The dictionary is offloaded to three partial indices that are created after every 13334 files parsed.

merge.py:
merge() reads chunks from each of the three partial indices into memory to combine and offload to index.txt.  Each chunk is shared by the first character of the tokens.  tf-idfs get computed and replace the term frequencies in the index, and a lexicon is created to map tokens to its position in index.txt

search.py:
search() takes the query as a string and seeks index.txt to retrieve lists of postings.  The tf-idf is computed for the query and cosine similarity is used to rank the top 10 URLs for the whole query.

site.py():
This is the main file that is run and if an inverted index has not been created then site.py will automatically call index() and merge() from indexer.py and merge.py respectively.  It retrieves results using search() and displays them to the site.

## Usage
Run the site.py file with the following command
```python
python3 site.py
```

Once the local web server is initialized, open "127.0.0.1:5000" in a browser and begin querying searches.
