import csv
import json
import sys
import argparse
import logging
import re
import mysplit
from typing import List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# get the origin term without []
def getOriginSentenceLst(sentencelst):
    originSentence = []
    for word in sentencelst:
        if word.startswith("[|term:") and word.endswith("|]") and len(word) > 2:
            originSentence.append(word[7:-2])
        else:
            originSentence.append(word)
    return originSentence


# split sentence into words
def splitSentence(sentence):
    return mysplit.splitSentence(sentence)

def lst2str(lst):
    return " ".join(lst)

def getOriginSentence(marked_Sentence):
    # textlst = splitSentence(marked_Sentence)
    # originSentenceLst = getOriginSentenceLst(textlst)
    # originSentence = lst2str(originSentenceLst)
    originSentence = re.sub(r'\[\|term:(.*?)\|\]', r'\1', marked_Sentence)
    return originSentence

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

# write lst to file
def write_lst_to_file(lst, output_path, filename):
    with open(output_path+"/"+filename, 'w', encoding='utf-8') as file:
        for item in lst:
            file.write(str(item)+"\n")

# write json lst to file
def write_json_to_file(json_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

def read_json(file_path: str):
    with open(file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data

def write_json(file_path: str, data: List[Any]):
    with open(file_path, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# get term ids of sentence
def get_term_ids_of_sentence(marked_Sentence):
    textlst = splitSentence(marked_Sentence)
    term_ids = []
    wordid = 0
    for j in range(len(textlst)):
        word = textlst[j]
        if word.startswith("[|term:") and word.endswith("|]"):
            term = word[7:-2]
            # if the termmark is connected to the previous letter, the termid - 1
            char_index = marked_Sentence.find(word)
            if char_index > 0 and marked_Sentence[char_index-1] != " ":
                term_ids.append([wordid-1, wordid+len(term.split())-2])
            else:
                term_ids.append([wordid, wordid+len(term.split())-1])
            
            wordid += len(term.split())
        else:
            wordid += len(word.split())

    return term_ids
   


def infinsert_metamorphics(mutants, originSentence, general_term_ids, infinsertmutants):
    infinsert_metamorphics = []

    # deal with insert mutant
    for mutant in mutants:
        # infinsert mutant
        
        if "infInsertMutant" in mutant.keys() and mutant["infInsertMutant"] != "":
            infinsert_metamorphic = dict()
            infinsert_metamorphic["infinsert_mutant"] = mutant["infInsertMutant"]
            infinsert_metamorphic["infInsertMeaning"] = mutant["infInsertMeaning"]
            infinsert_metamorphic["mutant_trans_id"] = len(infinsertmutants)
            infinsertmutants.append(mutant["infInsertMutant"])
            

            # measure the distance between mutant and origin sentence
            insinflen = len(mutant["infInsertMutant"].split())
            orilen = len(originSentence.split())
            distence = abs(insinflen - orilen)
            # for id in termids , if id is larger than mutant['index'], id = id + distence
            termids_of_insmutant = []
            for termidset in general_term_ids:
                termid = termidset[0]
                if termid>mutant["index"]:
                    termids_of_insmutant.append([termid+distence, termidset[1]+distence])
                else:
                    termids_of_insmutant.append(termidset)
            infinsert_metamorphic["termids_of_insmutant"] = termids_of_insmutant
            infinsert_metamorphics.append(infinsert_metamorphic)
    return infinsert_metamorphics

def bertinsert_metamorphics(mutants, bertinsertmutants, phrase_term_ids):
    bertinsert_metamorphics = []
    for mutant in mutants:
        if "bertmutants" in mutant.keys() and mutant["bertmutants"] != []:
            bertinsert_metamorphic = dict()
            bertinsert_metamorphic["term_range"] = phrase_term_ids[0]
            bertinsert_metamorphic["term"] = mutant["term"]

            bertinsert_metamorphic["bertmutants"] = [item[1] for item in mutant["bertmutants"]]
            bertinsert_metamorphic["bertmutants_similarities"] = [item[0] for item in mutant["bertmutants"]]
            bertinsert_metamorphic["mutanted_terms"] = mutant["mutanted_terms"]
            bertinsert_metamorphic["mutant_trans_ids"] = [len(bertinsertmutants)+i for i in range(len(mutant["bertmutants"]))]
            bertinsertmutants.extend([item[1] for item in mutant["bertmutants"]])
            
            bertinsert_metamorphics.append(bertinsert_metamorphic)
    return bertinsert_metamorphics


def read_jsonl(file_path: str):
    data = []
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            json_data = json.loads(line)
            data.append(json_data)
    return data


# read lines in txt file
def read_lines_in_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines



# mutant, align, and judge
def make_src(phrase_mutant_path, output_path):

    # set logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(output_path+"/translate.log")
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


    # read mutants
    logger.info("read mutants phrase")
    phrase_mutants = read_jsonl(phrase_mutant_path)

    
    # prepare for translate
    logger.info("translate, align, and judge of mutants")
    metamorphic_items = []
    maxlen = len(phrase_mutants)
    phrase_infoinsertmutants = []
    phrase_bertinsertmutants = []
    originSentences = []
    phrase_marked_Sentences_refertrans = []
    
    # initialize metamorphic_items
    count_mutants = 0
    for i in range(maxlen):
        metamorphic_item = dict()
        phrase_mutant_data = phrase_mutants[i]
        phrase_mutant = phrase_mutant_data["mutantItems"][0]
        metamorphic_item["mutant_id"] = count_mutants
        count_mutants += 1
        metamorphic_item["abs_index"] = i
        phrase_marked_Sentence = phrase_mutant_data["marked_sentence"]
        phrase_marked_Sentence_refertrans = phrase_mutant_data["refer_trans"]
        metamorphic_item["term"] = phrase_mutant["term"]
        metamorphic_item["term_trans"] = phrase_mutant["term_translations"]
        metamorphic_item["phrase_marked_Sentence"] = phrase_marked_Sentence
        metamorphic_item["phrase_marked_Sentence_refertrans"] = phrase_marked_Sentence_refertrans
        originSentence = getOriginSentence(phrase_marked_Sentence)
        metamorphic_item["originSentence"] = originSentence

        originSentences.append(originSentence)
        phrase_marked_Sentences_refertrans.append(phrase_marked_Sentence_refertrans)
        metamorphic_item["origin_trans_id"] = len(originSentences)-1
        
        # get term id of sentence
        phrase_term_ids = get_term_ids_of_sentence(phrase_marked_Sentence)
        metamorphic_item["phrase_term_ids"] = phrase_term_ids


        # infinsert mutant of phrase
        phrase_infinsert_metamorphics = infinsert_metamorphics(phrase_mutant_data["mutantItems"], originSentence, phrase_term_ids, phrase_infoinsertmutants)
        metamorphic_item["phrase_infinsert_metamorphics"] = phrase_infinsert_metamorphics

        # bertInsert mutant of phrase
        phrase_bertinsert_metamorphics = bertinsert_metamorphics(phrase_mutant_data["mutantItems"], phrase_bertinsertmutants, phrase_term_ids)
        metamorphic_item["phrase_bertinsert_metamorphics"] = phrase_bertinsert_metamorphics
    
        metamorphic_items.append(metamorphic_item)
    

    
    # write metamorphic_items to file
    logger.info("write metamorphic_items to file")

    write_json_to_file(metamorphic_items, output_path+"/metamorphic_items.json")
    write_lst_to_file(phrase_infoinsertmutants, output_path, "phrase_infoinsertmutants.txt")
    write_lst_to_file(phrase_bertinsertmutants, output_path, "phrase_bertinsertmutants.txt")
    write_lst_to_file(originSentences, output_path, "originSentences.txt")
    write_json_to_file(phrase_marked_Sentences_refertrans, output_path+"/phrase_marked_Sentences_refertrans.json")
    


# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--phrase_mutant_path', type=str, help='path to phrase generalMutant.txt')
    parser.add_argument('--output_path', type=str, help='path to output file')
    args = parser.parse_args()

    phrase_mutant_path = args.phrase_mutant_path
    output_path = args.output_path
    make_src(phrase_mutant_path, output_path)