import argparse
import os
import utils_nlp
import json # for writing dict into file

from nltk.tokenize import word_tokenize
from nltk.text import Text

def nlpai(filename):
    print('here we are')

    with open(filename) as f:
        contents = f.read()
        print(contents)

    text = Text(word_tokenize(contents))
    tag='Leute'
    concordance_list = text.concordance(tag)

    return concordance_list

if __name__ == '__main__':
    main()


