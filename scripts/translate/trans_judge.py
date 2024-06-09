import csv
import json
import sys
import argparse
import logging
import os
from tqdm import tqdm
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
# berttokenizer = BertTokenizer.from_pretrained('../models/bert-large-cased')

# write lst to the file
def write_lst_to_file(lst, output_path, filename):
    with open(output_path+"/"+filename, 'w', encoding='utf-8') as file:
        for item in lst:
            file.write(str(item)+"\n")

# write json lst to file
def write_json_to_file(json_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)


# read lines in txt file
def read_lines_in_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines

def read_json(file_path: str):
    with open(file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data

def make_gpt_item_to_string(gpt_bert_judge_item):
    result = dict()
    for key, value in gpt_bert_judge_item.items():
        result[key] = value["gpt_exam_label"]
    return result

# judge
def make_judge(output_path, trans_model, threshold_sentence, threshold_term, threshold_phrase_no_larger, gpt_bertins_judge_file=None):
    # set logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(output_path+f"/judge_{trans_model}.log")
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


    with open(output_path+f"/metamorphic_items_aligned_{trans_model}.json", 'r') as f:
        metamorphic_items = json.load(f)
    
    gpt_bertins_judge_dict = dict()
    if gpt_bertins_judge_file is not None and os.path.exists(gpt_bertins_judge_file):
        gpt_bertins_judge_dict = read_json(gpt_bertins_judge_file)

    # traverse metamorphic_items to determine error
    logger.info("start to traverse metamorphic_items to determine error")
    logger.info(f"start to judge, time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    metamorphic_items_final = []
    metamorphic_item_error = []

    metamorphic_item_phrase_infinsert_error_term = []
    metamorphic_item_phrase_bertinsert_error_term = []
    metamorphic_item_phrase_infinsert_error_sentence = []

    
    for i in tqdm(range(len(metamorphic_items))):
        metamorphic_item = metamorphic_items[i]
        if metamorphic_item == {}:
            metamorphic_items_final.append(metamorphic_item)
            continue
        marked_sentence = metamorphic_item["phrase_marked_Sentence"]

    # determination of infoinsert mutants
        # phrase level
        metamorphic_item["phrase_infinsert_error_term"] = 0
        metamorphic_item["phrase_infinsert_error_sentence"] = 0
        if "phrase_infinsert_metamorphics" in metamorphic_item.keys() and len(metamorphic_item["phrase_infinsert_metamorphics"])!=0:
            for phrase_infinsert_metamorphic in metamorphic_item["phrase_infinsert_metamorphics"]:
                # judge
                phrase_infinsert_metamorphic["error"] = 0
                
                phrase_similarities = phrase_infinsert_metamorphic["phrase_similarities"]
                if min(phrase_similarities) <= threshold_term:
                    phrase_infinsert_metamorphic["error"] = 1
                    metamorphic_item["phrase_infinsert_error_term"] = 1
            phrase_infinsert_origin_sentence_similarity = metamorphic_item["phrase_infinsert_origin_sentence_similarity"] 
            
            if min(phrase_infinsert_origin_sentence_similarity) <= threshold_sentence:
                metamorphic_item["phrase_infinsert_error_sentence"] = 1
        
        # determination of bertinsert mutants
        metamorphic_item["phrase_bertinsert_error_term"] = 0
        if "phrase_bertinsert_metamorphics" in metamorphic_item.keys() and len(metamorphic_item["phrase_bertinsert_metamorphics"])!=0:
            for phrase_bertinsert_metamorphic in metamorphic_item["phrase_bertinsert_metamorphics"]:
                phrase_bertinsert_metamorphic["error"] = 0
                # # if origin term is not translated, continue
                # if origin_term_trans_within_term_range[0].strip() == "":
                #     continue
                if gpt_bertins_judge_dict.get(marked_sentence) is not None:
                    gpt_bert_judge_item = gpt_bertins_judge_dict[marked_sentence]["same_trans_terms"]
                else:
                    gpt_bert_judge_item = dict()
                phrase_bertinsert_metamorphic["gpt_bert_judge_item"] = make_gpt_item_to_string(gpt_bert_judge_item)
                phrase_bertinsert_term_similarities = phrase_bertinsert_metamorphic["phrase_bertinsert_term_similarities"]
                mutanted_terms = phrase_bertinsert_metamorphic["mutanted_terms"]
                # judge
                error_mutants = []
                error_mutant_trans = []
                error_mutant_terms = []
                for mutantindex in range(len(phrase_bertinsert_term_similarities)):
                    similarity = phrase_bertinsert_term_similarities[mutantindex]
                    mutanted_term = mutanted_terms[mutantindex]
                    bertmutant = phrase_bertinsert_metamorphic["bertmutants"][mutantindex]
                    mutant_trans = phrase_bertinsert_metamorphic["trans_of_bertmutants"][mutantindex]
                    if gpt_bert_judge_item.get(mutanted_term) is not None:
                        gpt_exam_label = gpt_bert_judge_item[mutanted_term]["gpt_exam_label"]
                        if "YES" in gpt_exam_label:
                            continue
                    if similarity >= threshold_phrase_no_larger :
                        phrase_bertinsert_metamorphic["error"] = 1
                        metamorphic_item["phrase_bertinsert_error_term"] = 1
                        error_mutants.append(bertmutant)
                        error_mutant_trans.append(mutant_trans)
                        error_mutant_terms.append(mutanted_term)
                if len(error_mutants) != 0:
                    phrase_bertinsert_metamorphic["error_mutants"] = error_mutants
                    phrase_bertinsert_metamorphic["error_mutant_trans"] = error_mutant_trans
                    phrase_bertinsert_metamorphic["error_mutant_terms"] = error_mutant_terms

                    

                        
        metamorphic_item["error"] = 0
        if  metamorphic_item["phrase_infinsert_error_term"] == 1 or metamorphic_item["phrase_bertinsert_error_term"] == 1\
            or metamorphic_item["phrase_infinsert_error_sentence"] == 1:
            metamorphic_item["error"] = 1
        metamorphic_items_final.append(metamorphic_item)
        if metamorphic_item["error"] == 1:
            metamorphic_item_error.append(metamorphic_item)
        if metamorphic_item["phrase_infinsert_error_term"] == 1:
            metamorphic_item_phrase_infinsert_error_term.append(metamorphic_item)
        if metamorphic_item["phrase_bertinsert_error_term"] == 1:
            metamorphic_item_phrase_bertinsert_error_term.append(metamorphic_item)
        if metamorphic_item["phrase_infinsert_error_sentence"] == 1:
            metamorphic_item_phrase_infinsert_error_sentence.append(metamorphic_item)

    write_json_to_file(metamorphic_items_final, output_path+f"/metamorphic_items_final_{trans_model}.json")
    error_output_path = output_path + f"/error_{trans_model}"
    if not os.path.exists(error_output_path):
        os.mkdir(error_output_path)
    write_json_to_file(metamorphic_item_error, error_output_path+"/metamorphic_item_error.json")
    # write_lst_to_file(metamorphic_item_error, error_output_path, "metamorphic_item_error.txt")
    write_json_to_file(metamorphic_item_phrase_infinsert_error_term, error_output_path+"/metamorphic_item_phrase_infinsert_error_term.json")
    # write_lst_to_file(metamorphic_item_phrase_infinsert_error_term, error_output_path, "metamorphic_item_phrase_infinsert_error_term.txt")
    write_json_to_file(metamorphic_item_phrase_bertinsert_error_term, error_output_path+"/metamorphic_item_phrase_bertinsert_error_term.json")
    # write_lst_to_file(metamorphic_item_phrase_bertinsert_error_term, error_output_path, "metamorphic_item_phrase_bertinsert_error_term.txt")
    write_json_to_file(metamorphic_item_phrase_infinsert_error_sentence, error_output_path+"/metamorphic_item_phrase_infinsert_error_sentence.json")
    # write_lst_to_file(metamorphic_item_phrase_infinsert_error_sentence, error_output_path, "metamorphic_item_phrase_infinsert_error_sentence.txt")


    count_error = len(metamorphic_item_error)
    count_phrase_infinsert_error_term = len(metamorphic_item_phrase_infinsert_error_term)
    count_phrase_bertinsert_error_term = len(metamorphic_item_phrase_bertinsert_error_term)
    count_phrase_infinsert_error_sentence = len(metamorphic_item_phrase_infinsert_error_sentence)
    result_error_statis_lst = []
    result_error_statis_lst.append("count_error: {}".format(count_error))
    result_error_statis_lst.append("count_phrase_infinsert_error_term: {}".format(count_phrase_infinsert_error_term))
    result_error_statis_lst.append("count_phrase_bertinsert_error_term: {}".format(count_phrase_bertinsert_error_term))
    result_error_statis_lst.append("count_phrase_infinsert_error_sentence: {}".format(count_phrase_infinsert_error_sentence))
    write_lst_to_file(result_error_statis_lst, error_output_path, "result_error_statis_lst.txt")

    logger.info(f"end to judge, time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        

# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='make csv file for src')
    parser.add_argument('--output_path', type=str, help='path to output file')
    parser.add_argument('--trans_model', type=str)
    parser.add_argument('--threshold_sentence', type=float, help='threshold_sentence')
    parser.add_argument('--threshold_term', type=float, help='threshold_term')
    parser.add_argument('--threshold_phrase_no_larger', type=float, help='threshold_phrase_no_larger')
    parser.add_argument('--gpt_bertins_judge_file', type=str, default=None)
    args = parser.parse_args()

    output_path = args.output_path
    trans_model = args.trans_model
    threshold_sentence = args.threshold_sentence
    threshold_term = args.threshold_term
    threshold_phrase_no_larger = args.threshold_phrase_no_larger
    gpt_bertins_judge_file = args.gpt_bertins_judge_file
    make_judge(output_path, trans_model, threshold_sentence, threshold_term, threshold_phrase_no_larger, gpt_bertins_judge_file)