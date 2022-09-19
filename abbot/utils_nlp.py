# NLP utils
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk import FreqDist
from nltk.corpus import gutenberg
from nltk.text import Text
from nltk import Text
# from nltk.book import *

# just running all sorts of routines
def nlp_test(contents):
    satz_tokens = sent_tokenize(contents)
    wort_tokens = word_tokenize(contents)

    anzahl_satz_tokens = len(satz_tokens)
    anzahl_wort_tokens = len(wort_tokens)
    anzahl_zeichen = len(contents)
    print(anzahl_zeichen, ' Zeichen, ', anzahl_wort_tokens, 'Worte, ', anzahl_satz_tokens, 'Sätze')

    stop_words = set(stopwords.words("german"))

    gefilterte_liste = []
    for word in wort_tokens:
        if word.casefold() not in stop_words:
            gefilterte_liste.append(word)
    
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in wort_tokens]
    stemmed_words
    postags=nltk.pos_tag(wort_tokens)

    nltk.help.upenn_tagset()
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in wort_tokens]
    lemmatized_words

    # Chunking
    grammar = "NP: {<DT>?<JJ>*<NN>}"

    chunk_parser = nltk.RegexpParser(grammar)
    tree = chunk_parser.parse(postags)
    # tree.draw()
    tree = nltk.ne_chunk(postags)
    tree = nltk.ne_chunk(postags, binary=True)

    # Using a Concordance
    nltk.download("book")
    text8.concordance("man")

    # text6: Monty Python and the Holy Grail>
    text6.dispersion_plot(["grail", "god", "who", "Jesus", "wine", "bread", "man"])
    frequency_distribution = FreqDist(contents)

    # concordance 
    corpus = gutenberg.words('melville-moby_dick.txt')
    text = Text(corpus)
    con_list = text.concordance_list("monstrous")

    text = Text(word_tokenize(contents))
    con_list = text.concordance_list("Leute")
    con_list['text'] 
    con_list

    text.concordance("Leute")

    return


# 
def get_concordance(content, tag):
    text = Text(word_tokenize(contents))
    concor = text.concordance(tag)
    return concor


    