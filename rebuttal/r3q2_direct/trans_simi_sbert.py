import csv
import json
import sys
import argparse
import logging
import re
# import opus
import os
import subprocess
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


# write lst to file
def write_lst_to_file(lst, output_path, filename):
    with open(output_path+"/"+filename, 'w', encoding='utf-8') as file:
        for item in lst:
            file.write(str(item)+"\n")

# write json lst to file
def write_json_to_file(json_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)



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

    
    # get metamorphic_items
    with open(output_path+f"/metamorphic_items_aligned_{trans_model}.json", 'r') as file:
        metamorphic_items = json.load(file)

    # prepare metamorphic_items for judge
    logger.info("start to prepare metamorphic_items for judge")
    logger.info(f"start to get sbert similarities of sentences, time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    metamorphic_items_sbertsimi = []

    
    for i in tqdm(range(len(metamorphic_items))):
        metamorphic_item = metamorphic_items[i]
        origin_trans = metamorphic_item["origin_trans"]
        

        metamorphic_items_sbertsimi.append(metamorphic_item)

    write_json_to_file(metamorphic_items_sbertsimi, output_path+f"/metamorphic_items_aligned_{trans_model}_sbert.json")
    logger.info(f"metamorphic_items_aligned saved, time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

# main
if __name__ == "__main__":
    json_folder = "../results/refer_label/precision"
    error_types = ["info_term", "info_sentence", "bert_replace"]
    models = ["google"]
    real_errors = []
    real_corrects = []
    for error_type in error_types:
        for model in models:
            input_json = f"{json_folder}/{error_type}_{model}_conflict_solved.json"
            with open(input_json, 'r') as f:
                data = json.load(f)
            for key, value in data.items():
                value["trans_model"] = model
                if value["final_result"] == 1:
                    real_errors.append(value)
                elif value["final_result"] == 0:
                    real_corrects.append(value)
                else:
                    raise ValueError("error in final_result")

    error_sbert_simis = []
    correct_sbert_simis = []


    for i in tqdm(range(len(real_errors))):
        error = real_errors[i]
        origin = error["原句"]
        trans = error["原句翻译"]
        error["sbert_simi_ot"] = float(sbert_simi.getSimilarity(origin, trans))
        error_sbert_simis.append(error["sbert_simi_ot"])


    for j in tqdm(range(len(real_corrects))):
        correct = real_corrects[j]
        origin = correct["原句"]
        trans = correct["原句翻译"]
        correct["sbert_simi_ot"] = float(sbert_simi.getSimilarity(origin, trans))
        correct_sbert_simis.append(correct["sbert_simi_ot"])


    write_json_to_file(real_errors, f"./errors_sbert_simi.json")
    write_json_to_file(real_corrects, f"./corrects_sbert_simi.json")

    # write_json_to_file(data4boxplot, f"./data4boxplot.json")