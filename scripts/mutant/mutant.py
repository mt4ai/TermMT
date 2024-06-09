import json
# from tqdm import tqdm
import re
import torch
import sys
import os
import bgesimien as bgesim
# import sbertsimien as sbertsim
import posfilter as posfilter
import bertInsert as bertInsert
import numpy as np
import logging
import io
import time
import mysplit
import argparse
from typing import Any, List, Optional

simimodel = bgesim


# get the origin term without []
def getOriginSentenceLst(sentencelst):
    originSentence = []
    for word in sentencelst:
        if word.startswith("[|term:") and word.endswith("|]") and len(word) > 2:
            originSentence.append(word[7:-2])
        else:
            originSentence.append(word)
    return originSentence

# get origin sentence without mark
def getOriginSentence(marked_Sentence):
    originSentence = re.sub(r'\[\|term:(.*?)\|\]', r'\1', marked_Sentence)
    return originSentence

# split sentence into words
def splitSentence(sentence):
    return mysplit.splitSentence(sentence)

def get_max_index(arr):
    arr = np.array(arr) 
    max_index = np.argmax(arr)  
    return int(max_index)

def chooseMostSimilarMeaningMuntantBge(originsentence, mutantsentences):
    similaritylst = simimodel.getSimilarity([originsentence], mutantsentences)    

    indexofmeaning = get_max_index(similaritylst)
    return [mutantsentences[indexofmeaning], indexofmeaning, similaritylst]

# meaning added to sentence
def addedmeaning(meaning):
    # delete the ., at the end of meaning
    meaning = meaning.strip()
    # meaning = meaning[:-1] if meaning.endswith(".") else meaning
    # meaning = meaning[:-1] if meaning.endswith(",") else meaning
    return "("+meaning+")"

def lst2str(lst):
    return " ".join(lst)

def judge_term_in_brackets(sentence, term_char_bg, term_char_ed):
    branket_sign = 0
    in_branket = False
    for i in range(len(sentence)):
        if sentence[i] == "(":
            branket_sign += 1
        elif sentence[i] == ")":
            branket_sign -= 1
        elif sentence[i] == "（":
            branket_sign += 1
        elif sentence[i] == "）":
            branket_sign -= 1
        elif sentence[i] == "[":
            branket_sign += 1
        elif sentence[i] == "]":
            branket_sign -= 1
        # if any char in term is in brackets, don't take the mutant
        if i >= term_char_bg and i < term_char_ed:
            if branket_sign > 0:
                in_branket = True
                break
        if i >= term_char_ed:
            break
    return in_branket


def write_jsonl(file_path: str, data: List[Any]):
    with open(file_path, 'w', encoding="utf-8") as file:
        for item in data:
            json_line = json.dumps(item,ensure_ascii=False)
            file.write(json_line + '\n')


def mutantSentencePhrase(Sentence, terms, meanings, alternativeforms_all, synonyms_all, translations_all):
    textlst = splitSentence(Sentence)
    originSentenceLst = getOriginSentenceLst(textlst)
    originSentence = getOriginSentence(Sentence)
    termMuntants = []
    poslstabsolute = []
    poslablst = []

    # if sentence length is over 50 tokens, don't take the mutant
    if len(originSentence.split()) > 50:
        return termMuntants


    for i in range(len(textlst)):

        # generate mutants for each term
        if textlst[i].startswith("[|term:") and textlst[i].endswith("|]"):
            
            # print(textlst[i])
            termMuntant = dict()
            term = textlst[i][7:-2]
            
            
            realterm = term
            
            term_char_bg = Sentence.find(textlst[i])
            term_char_ed = term_char_bg + len(term)
            # if term is in brackets, don't take the mutant
            if judge_term_in_brackets(originSentence, term_char_bg, term_char_ed):
                continue

            # if term exists in terms over 1 time, continue
            if originSentence.lower().count(term.lower()) > 1:
                continue

            # if term in terms, use term, else use term.lower()
            if term in terms:
                realterm = term
            elif term.lower() in terms:
                realterm = term.lower()
            else:
                continue



            termMuntant["term"] = realterm
            # phrase term differs from word term in that length of phrase term is more than 1, so we need to record the real index of phrase in sentence

            termMuntant["index"] = sum([len(item.split()) for item in originSentenceLst[:i]])

            if poslstabsolute == []:
                poslstabsolute = posfilter.getSentencePosTags(lst2str(originSentenceLst).split())

            if poslablst == []:
                poslablst = posfilter.getSentencePosTags(originSentenceLst)
            
            # if the term is not a noun, proper noun, or pronoun, don't take the mutant
            if not posfilter.isNounProNoun(poslablst, i):
                continue

            candiposlst = posfilter.getPosByIndex(poslablst, i)

            termmeanings = [meaning for meaning in meanings[terms.index(realterm)] if meaning["pos"] in candiposlst]
            alternativeforms = alternativeforms_all[terms.index(realterm)]
            synonyms = synonyms_all[terms.index(realterm)]
            translations = translations_all[terms.index(realterm)]
            if termmeanings == []:
                termmeanings = meanings[terms.index(realterm)]
            # insertMutantSentences = []

            candidates = []
            for termmeaning in termmeanings: 
                insertedmeaning = addedmeaning(termmeaning["meaning"])
                candidates.append(Sentence.replace(textlst[i], term+" "+insertedmeaning))

            mostSimilarMutant,indexofmeaning,similarity = chooseMostSimilarMeaningMuntantBge(getOriginSentence(Sentence), candidates)
            
            # termMuntant["indexofmeaning"] = indexofmeaning

            # Mutant1 : insert term meaning into sentence
            tgtmeaning = termmeanings[indexofmeaning]["meaning"]
            insertedmeaning = addedmeaning(tgtmeaning)
            termMuntant["infInsertMutant"] = originSentence.replace(term, term+" "+insertedmeaning)
            termMuntant["infInsertMeaning"] = tgtmeaning
            termMuntant["term_translations"] = translations
            termMuntant["term_synonyms"] = synonyms
            termMuntant["term_alternativeforms"] = alternativeforms

            # print(originSentenceLst)
            # Mutant2 : replace term words with [MASK] and predict, only for phrase
            # to keep the grammar, we only replace term words of "noun"
            allowed_pos_set = {"NN", "NNS", "NNP", "NNPS"}
            term_range = [termMuntant["index"], termMuntant["index"]+len(realterm.split())]
            indexInPos = posfilter.getIndexInPos(poslstabsolute, allowed_pos_set, term_range)
            # relative location of term words in term
            relative_index = [index-term_range[0] for index in indexInPos]
            if relative_index == []:
                # don't take the mutant3
                termMuntants.append(termMuntant)
                continue
            try:
                bertorigin, bertmutants = bertInsert.get_insert_mutants(originSentenceLst, i, relative_index, originSentence)
            except:
                termMuntants.append(termMuntant)
                continue

            # if bertmutants == []:, don't take the mutant 3
            if bertmutants == []:
                termMuntants.append(termMuntant)
                continue 

            termMuntant["bertorigin"] = bertorigin
            # termMuntant["relative_index"] = poslstabsolute

            # if changed mutant is an alternative form or synonym of term, don't take the mutant
            filtered_bertmutants = []
            mutanted_terms = []
            lower_alternativeforms = [item.lower() for item in alternativeforms]
            lower_synonyms = [item.lower() for item in synonyms]
            avoid_forms = lower_alternativeforms + lower_synonyms
            avoid_forms = list(set(avoid_forms))
            for bertmutant in bertmutants:
                mutanted_term = bertmutant[2]
                if mutanted_term.lower() in lower_alternativeforms or mutanted_term.lower() in lower_synonyms:
                    continue
                for avoid_form in avoid_forms:
                    if avoid_form in mutanted_term.lower() or mutanted_term.lower() in avoid_form:
                        continue
                else:
                    filtered_bertmutants.append(bertmutant)
                    mutanted_terms.append(mutanted_term)
            bertmutants = filtered_bertmutants
            termMuntant['mutanted_terms'] = mutanted_terms
            termMuntant['filtered_terms'] = alternativeforms + synonyms
            termMuntant["bertmutants"] = bertmutants

            termMuntants.append(termMuntant)
    return termMuntants

def make_src(meaningdict, input_path, output_path, term_level, tgtarea, breakpoint=0):


    # set logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(output_path+"/mutant.log")
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    # tqdm_out = TqdmToLogger(logger, level=logging.INFO)


    meanings = []
    terms = []
    alternativeforms_all = []
    synonyms_all = []
    translations_all = []
    logger.info("*"*80)
    logger.info("Reading meaning dict...")


    # Counting part of speech types
    posset = set()

    with open(meaningdict, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # create dict
        # for line in tqdm(lines, ncols=80, file=tqdm_out):
        for line in lines:
            meaning = json.loads(line)
            if meaning['meanitems'] == []:
                continue
            meanings.append(meaning['meanitems'])
            terms.append(meaning['term'])
            alternativeforms_all.append(meaning['alternative_forms'])
            synonyms_all.append(meaning['synonyms'])
            translations_all.append(meaning['translations'])
            # Counting part of speech types
            for meanitem in meaning['meanitems']:
                posset.add(meanitem['pos'])
    logger.info("Reading meaning dict done!")
    logger.info("*"*80)

    # open datasets and write mutant sentences
    # areas = ["Education"]#, "Laws", "Microblog", "News", "Science", "Spoken", "Subtitles", "Thesis"]
    areas = [tgtarea]
    for area in areas:
        phrase_dataset_path = input_path+"/{0}/{1}mark.txt".format(area, 'phrase')
        insertMutant_path = output_path+"/{0}/insertMutant.jsonl".format(area)
        generalMutant_path = output_path+"/{0}/generalMutant.jsonl".format(area)
        bertInsertMutant_path = output_path+"/{0}/bertInsertMutant.jsonl".format(area)
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        if not os.path.exists(output_path+"/{0}".format(area)):
            os.mkdir(output_path+"/{0}".format(area))
        insertMutant_data = []
        generalMutant_data = []
        bertInsertMutant_data = []
        with open(phrase_dataset_path, 'r', encoding='utf-8') as phrase_dataset:

            phrase_lines = phrase_dataset.readlines()
            logger.info("start processing {0}...".format(area))
            # for i in tqdm(range(0, len(lines), 2), ncols=80, file=tqdm_out):
            for i in range(breakpoint, len(phrase_lines), 2):
                if i % 2000 == 0:
                    logger.info("processing {0}: {1}/{2}...".format(area, i//2, len(phrase_lines)//2))
                originSentence = phrase_lines[i].strip()
                refer_trans = phrase_lines[i+1].strip()
                try:
                    mutantItems = mutantSentencePhrase(originSentence, terms, meanings, alternativeforms_all, synonyms_all, translations_all)
                except:
                    mutantItems = []
                if mutantItems == []:
                    continue
                insertMutants = []

                bertInsertMutants = []
                for mutantItem in mutantItems:
                    if "infInsertMutant" in mutantItem:
                        insertMutants.append(mutantItem["infInsertMutant"])
                    if term_level == "phrase" and "bertmutants" in mutantItem and len(mutantItem["bertmutants"])!=0:
                        bertInsertMutants.append({"bertorigin":mutantItem["bertorigin"], "term_origin":mutantItem["term"], "bertmutants":str(mutantItem["bertmutants"]), 'mutanted_terms':str(mutantItem['mutanted_terms']), 'filtered_terms':str(mutantItem['filtered_terms'])})
                insertMutant_data.append(insertMutants)
                generalMutant_data.append({"mutantItems":mutantItems, "marked_sentence":originSentence, "refer_trans":refer_trans})
                bertInsertMutant_data.append(bertInsertMutants)
            write_jsonl(insertMutant_path, insertMutant_data)
            write_jsonl(generalMutant_path, generalMutant_data)
            write_jsonl(bertInsertMutant_path, bertInsertMutant_data)

# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='make csv file for src')
    parser.add_argument('--meaningdict', type=str, help='meaning dict path')
    parser.add_argument('--input_path', type=str, help='input path')
    parser.add_argument('--output_path', type=str, help='output path')
    parser.add_argument('--term_level', type=str, help='term level')
    parser.add_argument('--tgtarea', type=str, help='target area')
    parser.add_argument('--breakpoint', type=int, help='breakpoint', default=0)

    args = parser.parse_args()
    
    # read meaning dict
    meaningdict = args.meaningdict
    input_path = args.input_path
    output_path = args.output_path
    term_level = args.term_level
    tgtarea = args.tgtarea
    breakpoint = args.breakpoint
    make_src(meaningdict, input_path, output_path, term_level, tgtarea, breakpoint)
