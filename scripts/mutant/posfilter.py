from flair.data import Sentence
from flair.models import SequenceTagger
import re
from typing import List


wikposlst = ['Adjective', 'Numeral', 'Postposition', 'Preposition', 'Contraction', 'Adverb', 'Determiner', 
             'Article', 'Pronoun', 'Noun', 'Conjunction', 'Participle', 'Interjection', 'Proper noun', 'Particle', 'Verb']
flairposdict = {"JJ":["Adjective"], "JJR":["Adjective"], "JJS":["Adjective"], \
                "IN":["Postposition", "Preposition","Conjunction"], \
                "RB":["Adverb"], "RBR":["Adverb"], "RBS":["Adverb"], "WRB":["Adverb"], \
                "DT":["Determiner"], "PDT":["Determiner"], "WDT":["Determiner"], \
                "PRP":["Pronoun"], "PRP$":["Pronoun"], "WP":["Pronoun"], "WP$":["Pronoun"], \
                "NN":["Noun"], "NNP":["Noun","Proper noun"], "NNPS":["Noun","Proper noun"], "NNS":["Noun"], \
                "VBG":["Participle"], "VBN":["Participle"], "UH":["Interjection"], \
                "RP":["Particle"], "VB":["Verb"], "VBD":["Verb"], "VBG":["Verb"], "VBN":["Verb"],\
                "VBP":["Verb"], "VBZ":["Verb"]}
flairposinwik = ["JJ", "JJR", "JJS", "IN", "RB", "RBR", "RBS", "WRB", "DT", "PDT", "WDT", "PRP", "PRP$", "WP", "WP$", "NN"
                 , "NNP", "NNPS", "NNS", "VBG", "VBN", "UH", "RP", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
wikposnotinflairpos = ["Numeral", "Contraction", "Article"]






# load tagger
tagger = SequenceTagger.load("../models/pos-english/pytorch_model.bin")
# tagger = SequenceTagger.load("../../models/pos-english/pytorch_model.bin")



# judge if the term is a noun, proper noun, or pronoun
def isNounProNoun(labels, index):
    if labels[index].value in ["NN", "NNP", "NNPS", "NNS", "PRP", "PRP$", "WP", "WP$"]:
        return True
    else:
        return False

def getSentencePosTags(slst):

    # make example sentence
    sentence = Sentence(slst)
    # predict NER tagsf
    tagger.predict(sentence)
    return sentence.get_labels()

def getPosByIndex(lables, index):
    poslst = wikposnotinflairpos.copy()
    posOfIndex = lables[index].value
    if posOfIndex not in flairposinwik:
        return poslst+wikposlst
    else:
        for pos in flairposdict[posOfIndex]:
            poslst.append(pos)
        return poslst


def getTermPos(slst, index):
    poslst = wikposnotinflairpos.copy()
    # make example sentence
    sentence = Sentence(slst)
    # predict NER tagsf
    tagger.predict(sentence)
    posOfIndex = sentence.get_labels()[index].value
    if posOfIndex not in flairposinwik:
        return poslst+wikposlst
    else:
        for pos in flairposdict[posOfIndex]:
            poslst.append(pos)
        return poslst

def getIndexInPos(lables, posset, phraserange):
    resultindexs = []
    
    for index in range(phraserange[0], phraserange[1]):
        if lables[index].value in posset:
            resultindexs.append(index)
    return resultindexs

# test = "The United States, is a country in North America."
# lables = getSentencePosTags(test)
# posset = ["NN", "NNS", "NNP", "NNPS"]
# phraserange = [1, 3]
# print(lables)
# print(getIndexInPos(lables, posset, phraserange))

