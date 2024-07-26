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
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--output_path", type=str, required=True)
    # parser.add_argument("--input_path_Subtitles", type=str, required=True)
    # parser.add_argument("--input_path_Science", type=str, required=True)
    # parser.add_argument("--input_path_Laws", type=str, required=True)
    # parser.add_argument("--input_path_News", type=str, required=True)
    # parser.add_argument("--input_path_Thesis", type=str, required=True)
    # # parser.add_argument("--seed", type=int, required=True)
    # args = parser.parse_args()

    # # time = "2024-03-26_15-12-06"
    floder_names = ["Subtitles-detect", "Science-detect", "Laws-detect", "News-detect", "Thesis-detect"]
    area_folders = [f"../results/{floder_name}" for floder_name in floder_names]
    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    
    output_path = f"./questionaire/{current_time}"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # output_path = args.output_path
    # input_path_Subtitles = args.input_path_Subtitles
    # input_path_Science = args.input_path_Science
    # input_path_Laws = args.input_path_Laws
    # input_path_News = args.input_path_News
    # input_path_Thesis = args.input_path_Thesis


    # area_folders = [input_path_Subtitles, input_path_Science, input_path_Laws, input_path_News, input_path_Thesis]
    areas = ["Subtitles", "Science", "Laws", "News", "Thesis"]
    jsons_info_term_error_google = []
    jsons_info_term_error_mbart = []
    jsons_info_term_error_bing = []
    jsons_info_sentence_error_google = []
    jsons_info_sentence_error_mbart = []
    jsons_info_sentence_error_bing = []
    jsons_bert_replace_error_google = []
    jsons_bert_replace_error_mbart = []
    jsons_bert_replace_error_bing = []
    for i in range(len(area_folders)):
        area_folder = area_folders[i]
        area = areas[i]
        metamorphic_items = read_json(f"{area_folder}/metamorphic_items.json")
        filtered_metamorphic_items = []
        for item in metamorphic_items:
            if "phrase_bertinsert_metamorphics" not in item or len(item["phrase_bertinsert_metamorphics"]) == 0:
                continue
            filtered_metamorphic_items.append(item)
        picked_items_real = rand_sample(filtered_metamorphic_items, 100, 1234)

        
        json_info_term_error_google = read_json(f"{area_folder}/error_google/metamorphic_item_phrase_infinsert_error_term.json")
        json_info_sentence_error_google = read_json(f"{area_folder}/error_google/metamorphic_item_phrase_infinsert_error_sentence.json")
        json_bert_replace_error_google = read_json(f"{area_folder}/error_google/metamorphic_item_phrase_bertinsert_error_term.json")
        jsons_info_term_error_google.extend(json_info_term_error_google)
        jsons_info_sentence_error_google.extend(json_info_sentence_error_google)
        jsons_bert_replace_error_google.extend(json_bert_replace_error_google)

    sample_questionaire_item(jsons_info_term_error_google, 100, 1234,  os.path.join(output_path, "info_term_error_google.csv"), "info_term")
    sample_questionaire_item(jsons_info_sentence_error_google, 100, 1234, os.path.join(output_path, "info_sentence_error_google.csv"), "info_sentence")
    sample_questionaire_item(jsons_bert_replace_error_google, 100, 1234,  os.path.join(output_path, "bert_replace_error_google.csv"), "bert_replace")
    

    
