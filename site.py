from flask import Flask, render_template, request, redirect
from search import search
from indexer import index
from merge import merge
import os.path

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/", methods=['POST'])
def get_search_query():
    user_input = request.form['u']
    results = search(user_input, lexicon_dict, index, stop_words_list)
    top_results = [{'url' : mappings_dict[url]} for url, score in sorted(results[1].items(), key=lambda item: item[1], reverse=True)]
    return render_template("results.html", query=user_input, urls=top_results, time=results[0])
    # return redirect("/results")

# @app.route("/results")
# def display_results():
#     return "yes"

if __name__ == "__main__":
    if not os.path.isfile("index.txt"):
        index()
        merge()
        
    mappings_dict = {}
    with open("mappings.txt") as mappings:
        for line in mappings:
            id_url = line.rstrip().split()
            mappings_dict[int(id_url[0])] = id_url[1]

    lexicon_dict = {}
    with open("lexicon.txt") as lexicon:
        for line in lexicon:
            token_postings = line.rstrip().split()
            lexicon_dict[token_postings[0]] = int(token_postings[1])

    with open("stop_words.txt", "r") as stop_words_file:
        stop_words_list = [word for line in stop_words_file for word in line.rstrip().split()]
    index = open("index.txt")
    app.run(port=5000, debug=True)