import csv
import json
import sys
import argparse
import logging
import os
from tqdm import tqdm
from datetime import datetime
# from pathlib import Path
# f = Path(__file__)
# sys.path.append(str(f.parent.parent))

import sbert_simi as sbert_simi
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

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

def get_similarity_score_termpair(term1, term2):
    result = sbert_simi.getSimilarity([term1], [term2])
    return float(result[0][0])
    # return 0.5

# judge
def make_judge(output_path, trans_model, threshold_sentence, threshold_term, threshold_phrase_no_larger, gpt_align_term_file=None, gpt_judge_meancorr_file=None):
    # set logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(output_path+f"/trans_filter_error_{trans_model}_sbert.log")
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"gpt_filter begin time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    with open(output_path+f"/error_{trans_model}_sbert/metamorphic_item_error.json", 'r') as f:
        metamorphic_items = json.load(f)
    
    gpt_judge_meancorr = dict()

    with open(gpt_judge_meancorr_file, 'r') as f:
        gpt_judge_meancorr = json.load(f)


    gpt_align_term = dict()

    with open(gpt_align_term_file, 'r') as f:
        gpt_align_term = json.load(f)

    # traverse error metamorphic_items to filter error
    logger.info("start to traverse metamorphic_items to filter error")
    metamorphic_item_error = []

    metamorphic_item_phrase_infinsert_error_term = []
    metamorphic_item_phrase_bertinsert_error_term = []
    metamorphic_item_phrase_infinsert_error_sentence = []

    
    for i in tqdm(range(len(metamorphic_items))):
        metamorphic_item = metamorphic_items[i]
        origin_sentence = metamorphic_item["originSentence"]
        if metamorphic_item["phrase_infinsert_error_term"] == 1 or metamorphic_item["phrase_infinsert_error_sentence"] == 1:
            if gpt_judge_meancorr.get(origin_sentence, None) is not None:
                gpt_meancorr_judge_label = gpt_judge_meancorr[origin_sentence]["gpt_meancorr_judge_label"]
                metamorphic_item["gpt_meancorr_judge_label"] = gpt_meancorr_judge_label
                if "NO" in gpt_meancorr_judge_label:
                    continue
        
        if metamorphic_item["phrase_infinsert_error_term"] == 1:
            if gpt_align_term.get(origin_sentence, None) is not None:
                gpt_trans_terms = gpt_align_term[origin_sentence]["gpt_trans_terms"]
                origin_trans_gpt = gpt_trans_terms[0]
                mutant_trans_gpt = gpt_trans_terms[1]
                origin_trans_gpt = origin_trans_gpt.replace("<", "").replace(">", "")
                mutant_trans_gpt = mutant_trans_gpt.replace("<", "").replace(">", "")
                origin_trans_sentence = metamorphic_item["origin_trans"]
                mutant_trans_sentence = metamorphic_item["phrase_infinsert_metamorphics"][0]["mutant_trans"]
                # gpt extracted translation must be in the sentence translation, otherwise it is a gpt error
                metamorphic_item["gpt_align_trans_terms_infinsert"] = gpt_trans_terms
                if origin_trans_gpt in origin_trans_sentence and mutant_trans_gpt in mutant_trans_sentence:
                    gpt_term_similarity = get_similarity_score_termpair(origin_trans_gpt, mutant_trans_gpt)
                    metamorphic_item["gpt_term_similarity_infinsert"] = gpt_term_similarity
                    if gpt_term_similarity >= threshold_term:
                        metamorphic_item["phrase_infinsert_error_term"] = 0

        

                        
        metamorphic_item["error"] = 0
        if  metamorphic_item["phrase_infinsert_error_term"] == 1 or metamorphic_item["phrase_bertinsert_error_term"] == 1\
            or metamorphic_item["phrase_infinsert_error_sentence"] == 1:
            metamorphic_item["error"] = 1
        if metamorphic_item["error"] == 1:
            metamorphic_item_error.append(metamorphic_item)
        if metamorphic_item["phrase_infinsert_error_term"] == 1:
            metamorphic_item_phrase_infinsert_error_term.append(metamorphic_item)
        if metamorphic_item["phrase_bertinsert_error_term"] == 1:
            metamorphic_item_phrase_bertinsert_error_term.append(metamorphic_item)
        if metamorphic_item["phrase_infinsert_error_sentence"] == 1:
            metamorphic_item_phrase_infinsert_error_sentence.append(metamorphic_item)

    error_output_path = output_path + f"/error_{trans_model}_sbert"
    if not os.path.exists(error_output_path):
        os.mkdir(error_output_path)
    write_json_to_file(metamorphic_item_error, error_output_path+"/metamorphic_item_error_gptfiltered.json")
    # write_lst_to_file(metamorphic_item_error, error_output_path, "metamorphic_item_error.txt")
    write_json_to_file(metamorphic_item_phrase_infinsert_error_term, error_output_path+"/metamorphic_item_phrase_infinsert_error_term_gptfiltered.json")
    # write_lst_to_file(metamorphic_item_phrase_infinsert_error_term, error_output_path, "metamorphic_item_phrase_infinsert_error_term.txt")
    write_json_to_file(metamorphic_item_phrase_bertinsert_error_term, error_output_path+"/metamorphic_item_phrase_bertinsert_error_term_gptfiltered.json")
    # write_lst_to_file(metamorphic_item_phrase_bertinsert_error_term, error_output_path, "metamorphic_item_phrase_bertinsert_error_term.txt")
    write_json_to_file(metamorphic_item_phrase_infinsert_error_sentence, error_output_path+"/metamorphic_item_phrase_infinsert_error_sentence_gptfiltered.json")
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
    write_lst_to_file(result_error_statis_lst, error_output_path, "result_error_statis_lst_gptfiltered.txt")

    logger.info(f"gpt_filter end time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        

# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='make csv file for src')
    parser.add_argument('--output_path', type=str, help='path to output file')
    parser.add_argument('--trans_model', type=str)
    parser.add_argument('--threshold_sentence', type=float, help='threshold_sentence')
    parser.add_argument('--threshold_term', type=float, help='threshold_term')
    parser.add_argument('--threshold_phrase_no_larger', type=float, help='threshold_phrase_no_larger')
    parser.add_argument('--gpt_align_term_file', type=str, default=None)
    parser.add_argument('--gpt_judge_meancorr_file', type=str, default=None)
    args = parser.parse_args()

    output_path = args.output_path
    trans_model = args.trans_model
    threshold_sentence = args.threshold_sentence
    threshold_term = args.threshold_term
    threshold_phrase_no_larger = args.threshold_phrase_no_larger
    gpt_align_term_file = args.gpt_align_term_file
    gpt_judge_meancorr_file = args.gpt_judge_meancorr_file
    make_judge(output_path, trans_model, threshold_sentence, threshold_term, threshold_phrase_no_larger, gpt_align_term_file, gpt_judge_meancorr_file)