import json
import csv
import os
import random
import argparse
import time

def read_json(file_path: str):
    with open(file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data

def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

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

def rand_sample(samplelist, count, seed):
    print(seed)
    random.seed(seed)
    sampleresult = random.sample(samplelist, count)
    return sampleresult


def json_to_csv_realistic(json_lst, output_file):
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "原句", "术语", "insert变异", "insert变异是否真实", "替换变异", "替换术语","替换变异是否真实"])
        for index, item in enumerate(json_lst):
            originSentence = item["originSentence"]
            term = item["term"]
            infinsert_mutant = item["phrase_infinsert_metamorphics"][0]["infinsert_mutant"]
            bertmutants = item["phrase_bertinsert_metamorphics"][0]["bertmutants"]
            mutanted_terms = item["phrase_bertinsert_metamorphics"][0]["mutanted_terms"]
            writer.writerow([index, originSentence, term, infinsert_mutant, "", bertmutants, mutanted_terms,""])

def json_to_csv_insert_term_error(json_list, output_file):
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "原句", "术语", "参考翻译", "原句翻译", "原句术语翻译", "insert变异", "insert变异翻译", "insert术语翻译", "原句术语翻译", "请问这组插入变异是否存在术语翻译不一致的错误"])
        for index, item in enumerate(json_list):
            originSentence = item["originSentence"]
            term = item["term"]
            term_trans_refer = item["term_trans"]
            origin_trans = item["origin_trans"]
            origin_term_trans = item["origin_term_trans"]
            phrase_infinsert_metamorphic = item["phrase_infinsert_metamorphics"][0]
            infinsert_mutant = phrase_infinsert_metamorphic["infinsert_mutant"]
            inf_mutant_trans = phrase_infinsert_metamorphic["mutant_trans"]
            inf_mutant_term_trans = phrase_infinsert_metamorphic["mutant_term_trans"]
            writer.writerow([index, originSentence, term, term_trans_refer, origin_trans, origin_term_trans, infinsert_mutant, inf_mutant_trans, \
                             inf_mutant_term_trans, origin_term_trans, ""])


def json_to_csv_insert_sentence_error(json_list, output_file):
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "原句", "原句翻译", "insert变异", "insert变异翻译","insert变异翻译去括号", "原句翻译去括号", "请问这组插入变异是否存在句子翻译(去除括号后)不一致的错误"])

        for index, item in enumerate(json_list):
            originSentence = item["originSentence"]
            origin_trans = item["origin_trans"]
            phrase_infinsert_metamorphic = item["phrase_infinsert_metamorphics"][0]
            infinsert_mutant = phrase_infinsert_metamorphic["infinsert_mutant"]
            inf_mutant_trans = phrase_infinsert_metamorphic["mutant_trans"]
            origin_trans_wobra = remove_parentheses_content(origin_trans)
            inf_mutant_trans_wobra = remove_parentheses_content(inf_mutant_trans)
            writer.writerow([index, originSentence, origin_trans, infinsert_mutant, inf_mutant_trans,\
                             inf_mutant_trans_wobra, origin_trans_wobra])


def json_to_csv_bert_replace_error(json_list, output_file):
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "原句", "术语", "原句翻译", "原句术语翻译", "bert替换变异", "替换术语", "替换翻译", "替换术语翻译", "原句术语翻译", "gpt建议", "请问这组替换变异是否存在术语翻译一致的错误"])
        for index, item in enumerate(json_list):
            originSentence = item["originSentence"]
            term = item["term"]
            origin_trans = item["origin_trans"]
            origin_term_trans = item["origin_term_trans"]
            phrase_bertinsert_metamorphics = item["phrase_bertinsert_metamorphics"][0]
            bert_mutant_terms = phrase_bertinsert_metamorphics["mutanted_terms"]
            bertmutants = phrase_bertinsert_metamorphics["bertmutants"]
            trans_of_bertmutants = phrase_bertinsert_metamorphics["trans_of_bertmutants"]
            term_trans_of_bertmutant = phrase_bertinsert_metamorphics["term_trans_of_bertmutant"]
            gpt_bert_judge_item = phrase_bertinsert_metamorphics["gpt_bert_judge_item"]
            writer.writerow([index, originSentence, term, origin_trans, origin_term_trans, bertmutants, bert_mutant_terms, trans_of_bertmutants, term_trans_of_bertmutant, origin_term_trans, gpt_bert_judge_item, "" ])

def sample_questionaire_item(json_lst, count, seed, output_file, error_type):
    sampled_json_lst = rand_sample(json_lst, count, seed)
    if error_type == "info_term":
        json_to_csv_insert_term_error(sampled_json_lst, output_file)
    elif error_type == "info_sentence":
        json_to_csv_insert_sentence_error(sampled_json_lst, output_file)
    elif error_type == "bert_replace":
        json_to_csv_bert_replace_error(sampled_json_lst, output_file)
    write_json(sampled_json_lst, output_file.replace(".csv", "_sampled.json"))


if __name__ == "__main__":

    area = "sampled"
    current_time = "detect"
    foler_name = f"./results/{area}-{current_time}/error_gpt"
    json_info_term_error_gpt = read_json(f"{foler_name}/metamorphic_item_phrase_infinsert_error_term_gptfiltered.json")
    json_info_sentence_error_gpt = read_json(f"{foler_name}/metamorphic_item_phrase_infinsert_error_sentence_gptfiltered.json")
    json_bert_replace_error_gpt = read_json(f"{foler_name}/metamorphic_item_phrase_bertinsert_error_term_gptfiltered.json")

    output_path = f"./results/questionaire/{current_time}"
    if not os.path.exists(f"./results/questionaire/"):
        os.makedirs(f"./results/questionaire/")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    json_to_csv_insert_term_error(json_info_term_error_gpt, os.path.join(output_path, "info_term_error_gpt.csv"))
    json_to_csv_insert_sentence_error(json_info_sentence_error_gpt, os.path.join(output_path, "info_sentence_error_gpt.csv"))
    json_to_csv_bert_replace_error(json_bert_replace_error_gpt, os.path.join(output_path, "bert_replace_error_gpt.csv"))

