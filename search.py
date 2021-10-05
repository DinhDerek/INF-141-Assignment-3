from nltk.stem.porter import *
from math import log
from numpy import dot
from numpy.linalg import norm
from collections import Counter
import datetime
import json

def search(query_words, lexicon_dict, index, stop_words_list):
    # mappings_dict = {}
    # with open("mappings.txt") as mappings:
    #     for line in mappings:
    #         id_url = line.rstrip().split()
    #         mappings_dict[int(id_url[0])] = id_url[1]
    
    # lexicon_dict = {}
    # with open("lexicon.txt") as lexicon:
    #     for line in lexicon:
    #         token_postings = line.rstrip().split()
    #         lexicon_dict[token_postings[0]] = int(token_postings[1])

    start_time = datetime.datetime.now()        
    stemmer = PorterStemmer()
    list_of_queries = [stemmer.stem(token) for token in query_words.lower().split()]
    list_of_queries_nostop = [word for word in list_of_queries if word not in stop_words_list]

    query_vector = []
    if len(list_of_queries_nostop) / len(list_of_queries) >= 0.75:
        query_dict = Counter(list_of_queries_nostop)
    else:
        query_dict = Counter(list_of_queries)
    document_dict = {}
    for query in query_dict:
        if query in lexicon_dict:
            seek_position = lexicon_dict[query]
            index.seek(seek_position)
            result = json.loads(index.readline().rstrip().split(':')[1]) # <- returns the list of postings

            query_vector.append((1 + log(query_dict[query], 10)) * log((40002 / len(result)), 10))

            for posting in result:
                if posting[0] not in document_dict:
                    document_dict[posting[0]] = [[posting[1]], posting[2]]
                else:
                    document_dict[posting[0]][0].append(posting[1])
                    document_dict[posting[0]][1] += posting[2]
            
    # score_dict = {}
    # list_of_dictionaries.sort(key=lambda x: len(x))
    # for posting_id in smallest_list:
    #     if all(posting_id in d.keys() for d in list_of_dictionaries[1:]):
    #         score_dict[posting_id] = sum([d[posting_id] for d in list_of_dictionaries])
    
    # print("Total number of shared postings: " + str(len(score_dict)) + "\n")
    # counter = 0
    # for url, score in sorted(score_dict.items(), key=lambda item: item[1], reverse=True):
    #     print(mappings_dict[url] + " " + str(score) + "\n")
    #     counter += 1
    #     if counter == 5:
    #         break
    
    elapsed = datetime.datetime.now() - start_time
    # print("Time to get results: " + str(elapsed.total_seconds()*1000) + "\n")

    document_dict = {key:value for key, value in document_dict.items() if len(value[0]) == len(query_vector)}
    # score_dict = {}
    # for doc in document_dict:
    #     score_dict[doc] = dot(document_dict[doc][0], query_vector)/(norm(document_dict[doc][0])*norm(query_vector)) * document_dict[doc][1]

    return [elapsed.total_seconds()*1000, dict(sorted(document_dict.items(), key=lambda item: dot(item[1][0], query_vector)/(norm(item[1][0])*norm(query_vector)) * item[1][1], reverse=True)[:10])]


# if __name__ == "__main__":
#     search("cristina lopes")
#     search("machine learning")
#     search("ACM")
#     search("master of software engineering")