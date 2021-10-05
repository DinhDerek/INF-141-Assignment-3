from math import log

def merge():
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"           
    alpha_pos = 0
    seek_1 = 0
    seek_2 = 0
    seek_3 = 0
    
    #The lexicon dictionary will keep track of where each token is found on the index file
    lexicon_dict = {}

    #This initial while loop will only keep all tokens that begin with a specific number or letter in memory at a time
    while alpha_pos < len(alphabet):

        #Create a partial dictionary out of the tokens in index 1 that begin with the specified number or letter
        index_part1_dict = {}
        with open("index_part1.txt") as index_1:
            index_1.seek(seek_1)                            #This is important for every followup iteration after the first one to pick up right where we left off
            current_token1 = index_1.readline().rstrip()

            #Ensure that the token on the line being read is still matching the special character.  If it doesn't, we will seek to this line in the next iteration
            while current_token1[0] == alphabet[alpha_pos]: 
                seek_1 = index_1.tell()                     #Tell is used to determine where the line begins for the first token of the next special character
                token1 = current_token1.split(':')[0]       #Split into token - list of postings pair
                postings1 = eval(current_token1.split(':')[1])
                index_part1_dict[token1] = postings1        #Record the token - list of postings pair into the partial dictionary
                current_token1 = index_1.readline().rstrip()#Read the next line into memory and rinse and repeat

        #Exact same operation as index 1
        index_part2_dict = {}
        with open("index_part2.txt") as index_2:
            index_2.seek(seek_2)
            current_token2 = index_2.readline().rstrip()
            seek_2 = index_2.tell()

            while current_token2[0] == alphabet[alpha_pos]:
                seek_2 = index_2.tell()
                token2 = current_token2.split(':')[0]
                postings2 = eval(current_token2.split(':')[1])
                index_part2_dict[token2] = postings2
                current_token2 = index_2.readline().rstrip()

        #Exact same operation as index 1
        index_part3_dict = {}
        with open("index_part3.txt") as index_3:
            index_3.seek(seek_3)
            current_token3 = index_3.readline().rstrip()
            seek_3 = index_3.tell()
            
            while current_token3[0] == alphabet[alpha_pos]:
                seek_3 = index_3.tell()
                token3 = current_token3.split(':')[0]
                postings3 = eval(current_token3.split(':')[1])
                index_part3_dict[token3] = postings3
                current_token3 = index_3.readline().rstrip()

        #Use index part 1's dictionary as the base for the merged dictionary (the merged dictionary is the dictionary for the tokens beginning in a specific character)
        merged_dict = index_part1_dict
        
        #Similarly to what was done in indexer.py, iterate through index part 2's dictionary and combine matches or record them into the merged dictionary if not found
        for token in index_part2_dict:
            if token in merged_dict:
                merged_dict[token] = merged_dict[token] + index_part2_dict[token]
            else: 
                merged_dict[token] = index_part2_dict[token]
        
        #Exactly the same operation as the above for index part 2's dictionary
        for token in index_part3_dict:
            if token in merged_dict:
                merged_dict[token] = merged_dict[token] + index_part3_dict[token]
            else: 
                merged_dict[token] = index_part3_dict[token]

        #Once the merged dictionary is created, compute and replace the frequency in each posting with the tf-idf score
        #The new structure for the index is - term : [list of postings] (each posting is a list with [docID, tf-idf, weight])
        for token in merged_dict:
            updated_postings = merged_dict[token]
            for posting in updated_postings:
                #((1 + log(term_freq, 10)) * log((55393 / doc_freq), 10) + 1) * weight
                posting[1] = (1 + log(posting[1], 10)) * posting[2]
            merged_dict[token] = updated_postings

        #Write it into the file and offload from memory
        with open("index.txt", "a", encoding="utf-8") as index:
            for token in sorted(merged_dict):
                with open("lexicon.txt", "a", encoding="utf-8") as lexicon:
                    lexicon_dict[token] = index.tell()
                    lexicon.write(token + " " + str(lexicon_dict[token]) + "\n")
                index.write(token + ":" + str(sorted(merged_dict[token], key=lambda x:x[0])) + "\n")
        
        alpha_pos += 1

    #Exactly the same as what was done in the for loop, except this is to take care of the weird characters that are not alphanumeric.  For ex. those in other languages or etc.
    #This won't take up the entirety of memory so it's ok to build a dictionary out of these leftovers.
    index_part1_dict = {}
    with open("index_part1.txt") as index_1:
        index_1.seek(seek_1)
        current_token1 = index_1.readline().rstrip()
        
        while len(current_token1) != 0:
            token1 = current_token1.split(':')[0]
            postings1 = eval(current_token1.split(':')[1])
            index_part1_dict[token1] = postings1
            current_token1 = index_1.readline().rstrip()

    index_part2_dict = {}
    with open("index_part2.txt") as index_2:
        index_2.seek(seek_2)
        current_token2 = index_2.readline().rstrip()
        
        while len(current_token2) != 0:
            token2 = current_token2.split(':')[0]
            postings2 = eval(current_token2.split(':')[1])
            index_part2_dict[token2] = postings2
            current_token2 = index_2.readline().rstrip()

    index_part3_dict = {}
    with open("index_part3.txt") as index_3:
        index_3.seek(seek_3)
        current_token1 = index_3.readline().rstrip()
        
        while len(current_token3) != 0:
            token3 = current_token3.split(':')[0]
            postings3 = eval(current_token3.split(':')[1])
            index_part3_dict[token3] = postings3
            current_token3 = index_3.readline().rstrip()

    merged_dict = index_part1_dict
            
    for token in index_part2_dict:
        if token in merged_dict:
            merged_dict[token] = merged_dict[token] + index_part2_dict[token]
        else: 
            merged_dict[token] = index_part2_dict[token]

    for token in index_part3_dict:
        if token in merged_dict:
            merged_dict[token] = merged_dict[token] + index_part3_dict[token]
        else: 
            merged_dict[token] = index_part3_dict[token]

    for token in merged_dict:
        updated_postings = merged_dict[token]
        for posting in updated_postings:
            #((1 + log(term_freq, 10)) * log((55393 / doc_freq), 10) + 1) * weight
            posting[1] = (1 + log(posting[1], 10)) * posting[2]
        merged_dict[token] = updated_postings

    with open("index.txt", "a", encoding="utf-8") as index:
        for token in sorted(merged_dict):
            with open("lexicon.txt", "a", encoding="utf-8") as lexicon: #The lexicon is structured as follows - token : position in index.txt that the line for the token begins
                lexicon_dict[token] = index.tell()
                lexicon.write(token + " " + str(lexicon_dict[token]) + "\n")
            index.write(token + ":" + str(sorted(merged_dict[token], key=lambda x:x[0])) + "\n")


if __name__ == "__main__":
    merge()
