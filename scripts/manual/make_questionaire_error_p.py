import json
import csv
import os
import random
import argparse

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

def json_to_csv(json_lst, output_file):
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "原句", "术语", "原句翻译", "原句术语翻译",  \
                        "insert变异", "insert变异翻译", "insert术语翻译","原句术语翻译","insert和原句术语翻译相似度","(1)insert变异是否有术语不一致翻译错误",\
                        "insert变异翻译去括号", "原句翻译去括号", "insert和原句翻译去括号部分相似度", "(2)insert变异是否有句子翻译不一致错误（去括号）", \
                        "替换变异", "替换术语", "替换翻译", "替换术语翻译", "原句术语翻译", "替换术语和原句术语翻译相似度","(3)bert替换变异是否存在术语翻译一致错误",\
                        "CAT原句", "CAT变异", "CAT原句翻译", "CAT变异翻译","(4)CAT是否存在除替换词句子翻译不一致错误"])
        for index, item in enumerate(json_lst):
            item_termmt = item["google_item"]
            originSentence= item_termmt["originSentence"]
            term = item_termmt["term"]
            origin_trans = item_termmt["origin_trans"]
            origin_term_trans = item_termmt["origin_term_trans"]
            origin_trans_wobra = remove_parentheses_content(origin_trans)
            phrase_infinsert_metamorphic = item_termmt["phrase_infinsert_metamorphics"][0]
            infinsert_mutant = phrase_infinsert_metamorphic["infinsert_mutant"]
            inf_mutant_trans = phrase_infinsert_metamorphic["mutant_trans"]
            inf_mutant_term_trans = phrase_infinsert_metamorphic["mutant_term_trans"]
            inf_mutant_term_trans_simi = phrase_infinsert_metamorphic["phrase_similarities"]
            inf_mutant_trans_wobra = remove_parentheses_content(inf_mutant_trans)
            phrase_infinsert_origin_sentence_similarity = item_termmt["phrase_infinsert_origin_sentence_similarity"]


            phrase_bertinsert_metamorphics = item_termmt["phrase_bertinsert_metamorphics"][0]
            bert_mutant_terms = phrase_bertinsert_metamorphics["mutanted_terms"]
            bertmutants = phrase_bertinsert_metamorphics["bertmutants"]
            trans_of_bertmutants = phrase_bertinsert_metamorphics["trans_of_bertmutants"]
            term_trans_of_bertmutant = phrase_bertinsert_metamorphics["term_trans_of_bertmutant"]
            phrase_bertinsert_term_similarities = phrase_bertinsert_metamorphics["phrase_bertinsert_term_similarities"]

            item_CAT = item["mbart_cat_item"]
            cat_results = item_CAT["CAT_results"]
            cat_origin = cat_results[0]["ori"]
            cat_mutants = [result["mu"] for result in cat_results]
            cat_origin_trans = cat_results[0]["ori_trans"]
            cat_mutant_trans = [result["mu_trans"] for result in cat_results]
            writer.writerow([index, originSentence, term, origin_trans, origin_term_trans, \
                            infinsert_mutant, inf_mutant_trans, inf_mutant_term_trans, origin_term_trans, inf_mutant_term_trans_simi, "", \
                            inf_mutant_trans_wobra, origin_trans_wobra, phrase_infinsert_origin_sentence_similarity, "", \
                            bertmutants, bert_mutant_terms, trans_of_bertmutants, term_trans_of_bertmutant, origin_term_trans, phrase_bertinsert_term_similarities, "",\
                            cat_origin, cat_mutants, cat_origin_trans, cat_mutant_trans, ""])



            


    
        
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--input_path_Subtitles", type=str, required=True)
    parser.add_argument("--input_path_Science", type=str, required=True)
    parser.add_argument("--input_path_Laws", type=str, required=True)
    parser.add_argument("--input_path_News", type=str, required=True)
    parser.add_argument("--input_path_Thesis", type=str, required=True)
    # parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    # time = "2024-03-26_15-12-06"
    # floder_names = ["Subtitles-2024-03-25_14-46-32", "Science-2024-03-26_15-12-06", "Laws-2024-04-06_18-43-27", "News-2024-04-07_17-45-04", "Thesis-2024-04-07_18-57-26"]
    
    output_path = args.output_path
    input_path_Subtitles = args.input_path_Subtitles
    input_path_Science = args.input_path_Science
    input_path_Laws = args.input_path_Laws
    input_path_News = args.input_path_News
    input_path_Thesis = args.input_path_Thesis


    area_folders = [input_path_Subtitles, input_path_Science, input_path_Laws, input_path_News, input_path_Thesis]

    jsons_realistic = []
    for area_folder in area_folders:
        metamorphic_items = read_json(f"{area_folder}/metamorphic_items.json")
        filtered_metamorphic_items = []
        for item in metamorphic_items:
            if "phrase_bertinsert_metamorphics" not in item or len(item["phrase_bertinsert_metamorphics"]) == 0:
                continue
            filtered_metamorphic_items.append(item)

    
    
    
    # filter the json_lst, if "phrase_bertinsert_metamorphics" not in item_termmt or len(item["phrase_bertinsert_metamorphics"]) == 0, or "CAT_results" not in item_CAT or len(item["CAT_results"]) == 0, remove the item
    json_lst = []
    assert len(json_lst_termmt) == len(json_lst_CAT)
    for i in range(len(json_lst_termmt)):
        item_termmt = json_lst_termmt[i]
        item_CAT = json_lst_CAT[i]
        if "phrase_bertinsert_metamorphics" not in item_termmt or len(item_termmt["phrase_bertinsert_metamorphics"]) == 0 or "CAT_results" not in item_CAT or len(item_CAT["CAT_results"]) == 0:
            continue
        merged_item = dict()
        assert item_termmt["originSentence"] == item_CAT["originSentence"]
        merged_item["google_item"] = item_termmt
        merged_item["mbart_cat_item"] = item_CAT
        json_lst.append(merged_item)

    json_lst = rand_sample(json_lst, count, 123)
    json_to_csv(json_lst, output_path)
    write_json(json_lst, output_path.replace(".csv", "_questionaire_item.json"))