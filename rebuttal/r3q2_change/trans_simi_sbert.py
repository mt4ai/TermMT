import csv
import json
import sys
import argparse
import logging
import re
# import opus
import os
import subprocess
import jieba
from pathlib import Path
from tqdm import tqdm
import time
from datetime import datetime
# f = Path(__file__)
# sys.path.append(str(f.parent.parent))
import sbert_simi as sbert_simi

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def lst2str(lst):
    return " ".join(lst)

def get_align_file(file, output_file, align_tool_path):
    script_path = align_tool_path+"/run_align.py"
    output_file = output_file
    model_name_or_path = align_tool_path+"/models/model_without_co"
    data_file = file
    extraction = 'softmax'
    batch_size = 32
    command = [
    "python",
    "{}".format(script_path),
    "--output_file={}".format(output_file),
    "--model_name_or_path={}".format(model_name_or_path),
    "--data_file={}".format(data_file),
    "--extraction={}".format(extraction),
    "--batch_size={}".format(batch_size)
    ]

    subprocess.call(command)
    with open(output_file, 'r', encoding='utf-8') as file:
        align = [line.strip() for line in file.readlines()]
    return align

def read_align_file(file):
    with open(file, 'r', encoding='utf-8') as file:
        align = [line.strip() for line in file.readlines()]
    return align

# align is text like "0-1 1-1"
def get_align_withinrange(aligntext, begin, end):
    alignlst = aligntext.split()
    alignlst = [align.split('-') for align in alignlst]
    alignlst = [[int(align[0]), int(align[1])] for align in alignlst]
    alignlst = [align[1] for align in alignlst if align[0] >= begin and align[0] <= end]
    # delete the repeated align
    alignlst = list(set(alignlst))
    # sort the align
    alignlst.sort()
    return alignlst

# get the translated word terms
def get_translate_terms(align, termids, cutedTranslationLst):
    term_translate_ids = [get_align_withinrange(align, termid[0], termid[1]) for termid in termids]
    term_translations = []
    for term_translate_ids in term_translate_ids:
        translated_term = "".join([cutedTranslationLst[i] for i in term_translate_ids])
        term_translations.append(translated_term)
    return term_translations

# write lst to file
def write_lst_to_file(lst, output_path, filename):
    with open(output_path+"/"+filename, 'w', encoding='utf-8') as file:
        for item in lst:
            file.write(str(item)+"\n")

# write json lst to file
def write_json_to_file(json_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

# get jieba cutted sentence
def get_jieba_cutted_sentence(sentence):
    # delete " " in sentence
    sentence = sentence.replace(" ", "")
    return lst2str(jieba.lcut(sentence))

def make_align_sentences(sentences, translations):
    align_sentences = []
    jieba_cutted_sentences = []
    for i in range(len(sentences)):
        jieba_cut = get_jieba_cutted_sentence(translations[i]).strip()
        jieba_cutted_sentences.append(jieba_cut.split())
        align_sentences.append(sentences[i] + " ||| " + jieba_cut)
    return align_sentences, jieba_cutted_sentences

def make_jieba_cutted_sentences(translations):
    jieba_cutted_sentences = []
    for i in range(len(translations)):
        jieba_cut = get_jieba_cutted_sentence(translations[i]).strip()
        jieba_cutted_sentences.append(jieba_cut.split())
    return jieba_cutted_sentences

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

# get term translations of sentences
def get_term_translations_of_sentences(sentences, jieba_cutted_translations, term_ids_of_sentences, align_results):
    term_translations_of_sentences = []
    for i in range(len(sentences)):
        term_ids = term_ids_of_sentences[i]
        align = align_results[i]
        term_translations = get_translate_terms(align, term_ids, jieba_cutted_translations[i])
        term_translations_of_sentences.append(term_translations)
    return term_translations_of_sentences

# get terms by ids
def get_terms_by_ids(sentence, termids):
    return [lst2str(sentence.split()[termid[0]:termid[1]+1]) for termid in termids]

# extract term from marked sentence
def extract_term(marked_sentence):
    pattern = r'(\[\|term:.*?\|\])'
    words = re.split(pattern, marked_sentence)
    result = []
    for part in words:
        if part.startswith("[|term:") and part.endswith("|]"):
            result.append(part[7:-2])
    return result

# get term ids of sentence
def get_str_split_id(sentence, s):
    sindex = sentence.find(s)
    if sindex == -1:
        return -1
    else:
        bef = sentence[:sindex]
        # if bef[-1]!=" ", s is connected to the previous word, so the index should -1
        if bef != "" and bef[-1] != " ": 
            return [len(bef.split())-1, len(bef.split()) + len(s.split())-2]
        else:
            return [len(bef.split()), len(bef.split()) + len(s.split())-1]

# terms similarity
def get_terms_trans_similarity(origins, targets):
    result = sbert_simi.getSimilarity(origins, targets)
    return [float(result[i][i]) for i in range(len(result))]



def remove_en_barckets_content(sentence):
    stack = []
    result_stack = []
    for i in range(len(sentence)):
        char = sentence[i]
        if char == "(":
            stack.append([])
        elif char == ")":
            if stack:
                stack.pop()
        elif stack:
            stack[-1].append(char)
        else:
            if char == " " and i+1 < len(sentence) and sentence[i+1] == "(":
                continue
            result_stack.append(char)
    for content in stack:
        result_stack.extend(content)
    return ''.join(result_stack)

def remove_cn_barckets_content(sentence):
    stack = []
    result_stack = []
    for i in range(len(sentence)):
        char = sentence[i]
        if char == "（":
            stack.append([])
        elif char == "）":
            if stack:
                stack.pop()
        elif stack:
            stack[-1].append(char)
        else:
            if char == " " and i+1 < len(sentence) and sentence[i+1] == "（":
                continue
            result_stack.append(char)
    for content in stack:
        result_stack.extend(content)
    return ''.join(result_stack)

# remove nested brackets content
def remove_parentheses_content(sentence):
    sentence = remove_en_barckets_content(sentence)
    sentence = remove_cn_barckets_content(sentence)
    return sentence



# read lines in txt file
def read_lines_in_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines

# align, get similarity
def align_process(output_path, align_tool_path, trans_model):
    # set logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(output_path+f"/sbert_simi_{trans_model}.log")
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # get origin sentences
    originSentences = read_lines_in_txt_file(output_path+"/originSentences.txt")
    phrase_infoinsertmutants = read_lines_in_txt_file(output_path+"/phrase_infoinsertmutants.txt")
    phrase_bertinsertmutants = read_lines_in_txt_file(output_path+"/phrase_bertinsertmutants.txt")

    # get translated sentences
    
    origin_translations = read_lines_in_txt_file(output_path+f"/translation/{trans_model}/originSentences_translations.txt")
    phrase_infoinsertmutants_translations = read_lines_in_txt_file(output_path+f"/translation/{trans_model}/phrase_infoinsertmutants_translations.txt")
    phrase_bertinsertmutants_translations = read_lines_in_txt_file(output_path+f"/translation/{trans_model}/phrase_bertinsertmutants_translations.txt")

    # delete the brackets content in infoinsertmutants
    phrase_infoinsertmutants_wobracket = [remove_en_barckets_content(sentence) for sentence in phrase_infoinsertmutants]
    phrase_infoinsertmutants_translations_wobracket = [remove_parentheses_content(sentence) for sentence in phrase_infoinsertmutants_translations]

    # get metamorphic_items
    with open(output_path+f"/metamorphic_items_aligned_{trans_model}.json", 'r') as file:
        metamorphic_items = json.load(file)

    # prepare metamorphic_items for judge
    logger.info("start to prepare metamorphic_items for judge")
    logger.info(f"start to get sbert similarities of sentences, time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    metamorphic_items_aligned = []

    
    for i in tqdm(range(len(metamorphic_items))):
        metamorphic_item = metamorphic_items[i]
        origin_trans = metamorphic_item["origin_trans"]
        # metamorphic_item["origin_id_range"] = get_terms_by_ids(origin_sentence, phrase_term_ids)
        marked_sentence = metamorphic_item["phrase_marked_Sentence"]
        
        origin_term = metamorphic_item["origin_term"]
        
        origin_term_trans = metamorphic_item["origin_term_trans"]

        # phrase level
        if "phrase_infinsert_metamorphics" in metamorphic_item.keys() and len(metamorphic_item["phrase_infinsert_metamorphics"])!=0:
            mutant_trans_s = []
            for phrase_infinsert_metamorphic in metamorphic_item["phrase_infinsert_metamorphics"]:
                mutant_trans_id = phrase_infinsert_metamorphic["mutant_trans_id"]

                mutant_trans_s.append(phrase_infoinsertmutants_translations_wobracket[mutant_trans_id])
                
                # get similarity of term
                phrase_similarities = get_terms_trans_similarity(origin_term_trans, phrase_infinsert_metamorphic["mutant_term_trans"])
                phrase_infinsert_metamorphic["phrase_similarities"] = phrase_similarities
            # mutant_trans_s = [remove_parentheses_content(trans) for trans in mutant_trans_s]

            phrase_infinsert_origin_sentence_similarity = sbert_simi.getSimilarity([remove_parentheses_content(origin_trans)], mutant_trans_s)[0]
            phrase_infinsert_origin_sentence_similarity = [float(similarity) for similarity in phrase_infinsert_origin_sentence_similarity]
            metamorphic_item["phrase_infinsert_origin_sentence_similarity"] = phrase_infinsert_origin_sentence_similarity
            

        # bert level
        if "phrase_bertinsert_metamorphics" in metamorphic_item.keys() and len(metamorphic_item["phrase_bertinsert_metamorphics"])!=0:
            for phrase_bertinsert_metamorphic in metamorphic_item["phrase_bertinsert_metamorphics"]:
                origin_term_trans_within_term_range = phrase_bertinsert_metamorphic["origin_term_trans_within_term_range"]
                term_trans_of_bertmutants = phrase_bertinsert_metamorphic["term_trans_of_bertmutant"]
                phrase_bertinsert_term_similarities = sbert_simi.getSimilarity(origin_term_trans_within_term_range, term_trans_of_bertmutants)[0]

                phrase_bertinsert_term_similarities = [float(similarity) for similarity in phrase_bertinsert_term_similarities]
                phrase_bertinsert_metamorphic["phrase_bertinsert_term_similarities"] = phrase_bertinsert_term_similarities

        metamorphic_items_aligned.append(metamorphic_item)

    write_json_to_file(metamorphic_items_aligned, output_path+f"/metamorphic_items_aligned_{trans_model}_sbert.json")
    logger.info(f"metamorphic_items_aligned saved, time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='make json file for src')
    parser.add_argument('--output_path', type=str, help='path to output file')
    parser.add_argument('--align_tool_path',type=str, help='path to align tool')
    parser.add_argument('--trans_model', type=str, help='path to translation model')
    args = parser.parse_args()


    output_path = args.output_path
    align_tool_path = args.align_tool_path
    trans_model = args.trans_model

    # output_path = "../results/Subtitles-detect"
    # align_tool_path = "../awesome-align"
    # trans_model = "google"
    align_process(output_path, align_tool_path, trans_model)