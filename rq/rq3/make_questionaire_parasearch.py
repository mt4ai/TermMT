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
                        "替换变异", "替换术语", "替换翻译", "替换术语翻译", "原句术语翻译", "替换术语和原句术语翻译相似度","(3)bert替换变异是否存在术语翻译一致错误"])
        for index, item_termmt in enumerate(json_lst):
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

            writer.writerow([index, originSentence, term, origin_trans, origin_term_trans, \
                infinsert_mutant, inf_mutant_trans, inf_mutant_term_trans, origin_term_trans, inf_mutant_term_trans_simi, "", \
                inf_mutant_trans_wobra, origin_trans_wobra, phrase_infinsert_origin_sentence_similarity, "", \
                bertmutants, bert_mutant_terms, trans_of_bertmutants, term_trans_of_bertmutant, origin_term_trans, phrase_bertinsert_term_similarities, ""])

def examine_bert_insert_mutant(item):
    if "phrase_bertinsert_metamorphics" not in item or len(item["phrase_bertinsert_metamorphics"]) == 0 :
        return False
    return True
            


    
        
        

if __name__ == "__main__":



    input_folder = "../../detect-1-sth/results/"
    floder_names = ["Subtitles-detect", "Science-detect", "Laws-detect", "News-detect", "Thesis-detect"]
    google_candis = []
    bing_candis = []
    mbart_candis = []
    for folder in floder_names:
        google_json = read_json(f"{input_folder}{folder}/metamorphic_items_final_google.json")
        bing_json = read_json(f"{input_folder}{folder}/metamorphic_items_final_bing.json")
        mbart_json = read_json(f"{input_folder}{folder}/metamorphic_items_final_mbart.json")
        assert len(google_json) == len(bing_json) == len(mbart_json)
        for i in range(len(google_json)):
            assert google_json[i]["originSentence"] == bing_json[i]["originSentence"]
            assert google_json[i]["originSentence"] == mbart_json[i]["originSentence"]
            if examine_bert_insert_mutant(google_json[i]) == False or examine_bert_insert_mutant(bing_json[i]) == False or examine_bert_insert_mutant(mbart_json[i]) == False:
                continue
            area = folder.split("-")[0]
            google_json[i]["area"] = area
            bing_json[i]["area"] = area
            mbart_json[i]["area"] = area
            google_candis.append(google_json[i])
            bing_candis.append(bing_json[i])
            mbart_candis.append(mbart_json[i])
    google_samples = rand_sample(google_candis, 100, 123)
    bing_samples = rand_sample(bing_candis, 100, 456)
    mbart_samples = rand_sample(mbart_candis, 100, 789)

        

    output_path = "./questionaires"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # write results to csv
    json_to_csv(google_samples, f"{output_path}/google_questionaire.csv")
    write_json(google_samples, f"{output_path}/google_questionaire.json")
    json_to_csv(bing_samples, f"{output_path}/bing_questionaire.csv")
    write_json(bing_samples, f"{output_path}/bing_questionaire.json")
    json_to_csv(mbart_samples, f"{output_path}/mbart_questionaire.csv")
    write_json(mbart_samples, f"{output_path}/mbart_questionaire.json")
    
    
