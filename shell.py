from indexer import index
from merge import merge
from search import search

def shell():
    #index()
    mappings_dict = {}
    with open("mappings.txt") as mappings:
        for line in mappings:
            id_url = line.rstrip().split()
            mappings_dict[int(id_url[0])] = id_url[1]

    #merge()
    lexicon_dict = {}
    with open("lexicon.txt") as lexicon:
        for line in lexicon:
            token_postings = line.rstrip().split()
            lexicon_dict[token_postings[0]] = int(token_postings[1])
    
    index = open("index.txt")

    with open("stop_words.txt", "r") as stop_words_file:
        stop_words_list = [word for line in stop_words_file for word in line.rstrip().split()]

    user_input = input(">> ")

    while (user_input not in ["q", "quit"]):
        search(user_input, lexicon_dict, index, stop_words_list)
        user_input = input(">> ")

    index.close()

if __name__ == "__main__":
    shell()