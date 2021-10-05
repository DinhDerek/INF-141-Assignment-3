import os, sys, json, nltk, re
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import *
from urllib.parse import urldefrag
from simhash import Simhash, SimhashIndex

nltk.download('punkt')

def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

def index():
    sim_hash_dict = {}
    all_token_dict = {}                                                             #This will contain the final token dict
    url_dict = {}                                                                   #This maps urls to docIDs
    weight_dict = {'title': 10, 'h1': 8, 'h2': 6, 'strong': 4, 'h3': 3, 'b': 2}     #This is how each important tag is weighed
    url_id = 0                                                                      #Begin at url_id 0 (naturally)

    #Find all of the files in each folder with os.walk()
    for (root,dirs,files) in os.walk('DEV', topdown=True):

        for json_file in files:
            page_token_dict = {}                        #Houses all of the tokens for a particular json file
            with open(root + "/" + json_file) as jf:
                #Load the json contents into a dictionary, defrag the url and map it to a docID
                json_dict = json.load(jf)
                url_dict[url_id] = urldefrag(json_dict['url'])[0]

            #Grab the text from the page
            page_soup = BeautifulSoup(json_dict['content'], "html.parser")
            page_text = page_soup.get_text(separator=' ').lower()

            if url_id == 0:
                index = SimhashIndex([(k, v) for k, v in sim_hash_dict.items()], k=3)
                
            current_hash = Simhash(get_features(page_text))
            dups = index.get_near_dups(current_hash)
            if len(dups) == 0:
                #sim_hash_dict[url_id] = Simhash(get_features(page_text))
                index.add(url_id, current_hash)

                #Write the mapping to the file for reference
                with open("mappings.txt", "a", encoding="utf-8") as mapping_file:
                    mapping_file.write( str(url_id) + " " + urldefrag(json_dict['url'])[0] + "\n" )

                #Tokenize the text
                regex_tokenizer = nltk.RegexpTokenizer(r"\w+")
                tokens = regex_tokenizer.tokenize(page_text)

                #As recommended, use the porter stemmer to stem all of the tokens
                stemmer = PorterStemmer()
                stemmed_tokens = [stemmer.stem(token) for token in tokens]

                #If the token exists in that page's dictionary, increment the count.  Otherwise, create a new addition to the dictionary and also compute the weight
                for token in stemmed_tokens:
                    if token in page_token_dict:
                        page_token_dict[token][1] += 1
                    else:
                        # weight = 0
                        # for tag in weight_dict:
                        #     if token in page_soup.find_all(tag):
                        #         weight += weight_dict[tag]
                        # page_token_dict[token] = [url_id, 1, weight]

                        #The inverted index is structured as follows - term : [list of postings] (each posting is a list with [docID, term frequency, weight])
                        page_token_dict[token] = [url_id, 1, 1]
                
                #Go through each tag in the weight dict and check if any of the text in each tag is a token we have indexed, and add the weight accordingly
                for tag in weight_dict:
                    for result in page_soup.find_all(tag):
                        if result.string is not None:
                            tag_tokens = [stemmer.stem(token) for token in regex_tokenizer.tokenize(result.string)]
                            for token in tag_tokens:
                                if token in page_token_dict:
                                    page_token_dict[token][2] += weight_dict[tag]
                                else:
                                    page_token_dict[token] = [url_id, 1, 1 + weight_dict[tag]]

                #For each token in the current page's dictionary, check if it exists in the main dictionary.  If it does append it to the existing list, else create a new addition
                for token in page_token_dict:
                    if token in all_token_dict:
                        all_token_dict[token].append(page_token_dict[token])
                    else:
                        all_token_dict[token] = [page_token_dict[token]]

                #Check to see if a milestone is reached to drop the partial index into a file, if it is then write it and then clear the dictionary
                if ((url_id + 1) / 13334) == 1: 
                    with open("index_part1.txt", "a", encoding="utf-8") as index_part1_file:
                        for token in sorted(all_token_dict):
                            index_part1_file.write(token + ":" + str(all_token_dict[token]) + "\n")        
                    all_token_dict = {}
                elif ((url_id + 1) / 13334) == 2:
                    with open("index_part2.txt", "a", encoding="utf-8") as index_part2_file:
                        for token in sorted(all_token_dict):
                            index_part2_file.write(token + ":" + str(all_token_dict[token]) + "\n")     
                    all_token_dict = {}
                elif ((url_id) / 13334) == 3:
                    with open("index_part3.txt", "a", encoding="utf-8") as index_part3_file:
                        for token in sorted(all_token_dict):
                            index_part3_file.write(token + ":" + str(all_token_dict[token]) + "\n")     
                    all_token_dict = {}
                url_id += 1                                                     #When all operations are complete, increment the docID
            else:
                for url in dups:
                    if int(url) != url_id:
                        print(url_dict[url_id] + " is similar to " + url_dict[int(url)] + "\n")


if __name__ == "__main__":
    index()