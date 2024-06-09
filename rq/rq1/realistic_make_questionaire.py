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




if __name__ == "__main__":


    floder_names = ["Subtitles-detect", "Science-detect", "Laws-detect", "News-detect", "Thesis-detect"]
    area_folders = [f"../../detect-1-sth/results/{floder_name}" for floder_name in floder_names]
    # current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    
    output_path = f"./results/questionaire/questionaires"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    areas = ["Subtitles", "Science", "Laws", "News", "Thesis"]

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
        write_json(picked_items_real, os.path.join(output_path, f"{area}_realistic.json"))
        json_to_csv_realistic(picked_items_real, os.path.join(output_path, f"{area}_realistic.csv"))
        

    

    
