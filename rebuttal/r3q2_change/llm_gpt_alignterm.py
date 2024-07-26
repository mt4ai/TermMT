# import openai
from openai import OpenAI
import json
import os
import numpy
from tqdm import tqdm
import time
from datetime import datetime
from typing import List, Any
from tenacity import retry, stop_after_attempt, wait_fixed
import argparse

base_url = ""
gpt_api_key = ""
client = OpenAI(
    base_url = base_url,
    api_key=gpt_api_key,
)

temperature = 0

@retry(stop=stop_after_attempt(14))
def generate(input_text):
    

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": input_text,
            }
        ],
        model="gpt-3.5-turbo-0125",
    )

    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

# def generate(input_text):
#     return input_text

def read_json(file_path: str):
    with open(file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return data

def write_json(file_path: str, data: List[Any]):
    with open(file_path, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def read_jsonl(file_path: str):
    data = []
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            json_data = json.loads(line)
            data.append(json_data)
    return data

def write_jsonl(file_path: str, data: List[Any]):
    with open(file_path, 'w', encoding="utf-8") as file:
        for item in data:
            json_line = json.dumps(item, ensure_ascii=False)
            file.write(json_line + '\n')

def save(lst, path):
    with open(path, "w") as f:
        json.dump(lst, f, indent=2)

def sort_keys(key):
    try:
        return int(key)
    except ValueError:
        return key
    
# meaning added to sentence
def addedmeaning(meaning):
    meaning = meaning.strip()
    return "("+meaning+")"

def generate_prompt(term, sentence_en, sentence_zh):

    prompt = f"You are an English-Chinese Alignment Expert, expert in aligning phrases in English with their corresponding translations in Chinese. \n\
        Provide response only in following format: <中文> \n\
        Given the English sentence <{sentence_en}> and Chinese translated sentence of it <{sentence_zh}>, give the alignment of the phrase <{term}>. \n\
        Response:"
    return prompt


def ask_gpt(sentence_info_folder, sentence_info_filename, output_filename, before_file_name=None):
    # save tmp result to a json file
    model_result_path = sentence_info_folder + "/gpt_results"
    if not os.path.exists(model_result_path):
        os.makedirs(model_result_path)
    sentence_info_path = os.path.join(sentence_info_folder, sentence_info_filename)
    tmp_result_path = os.path.join(model_result_path, output_filename.split(".")[0] + '_tmp.json')
    tmp_result_path_before = dict()
    if before_file_name is not None and os.path.exists(os.path.join(model_result_path, before_file_name)):
        # tmp_result_path_before_file = os.path.join(model_result_path, before_file_name)
        tmp_result_path_before = read_json(os.path.join(model_result_path, before_file_name))


    if os.path.exists(tmp_result_path):
        tmp_results = read_json(tmp_result_path)
        data = read_json(sentence_info_path)
        for index, src in enumerate(data):
            if src.get("phrase_infinsert_metamorphics", None) is None:
                continue
            phrase_infoinsert_metamorphics = src["phrase_infinsert_metamorphics"]
            originSentence = src["originSentence"]
            phrase_infoinsert_metamorphic = phrase_infoinsert_metamorphics[0]
            if src["phrase_infinsert_error_term"] == 1:
                
                if tmp_results.get(originSentence, None) is None:
                    term = src["origin_term"]
                    originSentence = src["originSentence"]
                    origin_trans = src["origin_trans"]
                    infinsert_mutant = phrase_infoinsert_metamorphic["infinsert_mutant"]
                    mutant_trans = phrase_infoinsert_metamorphic["mutant_trans"]
                    judge_item = dict()
                    judge_item["term"] = term   
                    judge_item["originSentence"] = originSentence
                    judge_item["origin_trans"] = origin_trans
                    judge_item["infinsert_mutant"] = infinsert_mutant
                    judge_item["mutant_trans"] = mutant_trans
                    tmp_results[originSentence] = judge_item
    else:
        data = read_json(sentence_info_path)
        tmp_results = dict()
        for index, src in enumerate(data):
            if src.get("phrase_infinsert_metamorphics", None) is None:
                continue
            if src["phrase_infinsert_error_term"] != 1:
                continue
            phrase_infoinsert_metamorphics = src["phrase_infinsert_metamorphics"]
            phrase_infoinsert_metamorphic = phrase_infoinsert_metamorphics[0]
            infinsert_mutant = phrase_infoinsert_metamorphic["infinsert_mutant"]
            mutant_trans = phrase_infoinsert_metamorphic["mutant_trans"]
            term = src["origin_term"]
            originSentence = src["originSentence"]
            origin_trans = src["origin_trans"]
            judge_item = dict()
            if src["phrase_infinsert_error_term"] == 1:
                judge_item["term"] = term
                judge_item["originSentence"] = originSentence
                judge_item["origin_trans"] = origin_trans
                judge_item["infinsert_mutant"] = infinsert_mutant
                judge_item["mutant_trans"] = mutant_trans
                tmp_results[originSentence] = judge_item

        write_json(tmp_result_path, tmp_results)
    
    for originSentence, judge_item in tqdm(tmp_results.items()):
        term = judge_item["term"]
        origin_trans = judge_item["origin_trans"]
        infinsert_mutant = judge_item["infinsert_mutant"]
        mutant_trans = judge_item["mutant_trans"]

        if tmp_result_path_before.get(originSentence, None) is not None:
            before_judge_item = tmp_result_path_before[originSentence]
            if before_judge_item.get("gpt_trans_terms", None) is not None:
                tmp_results[originSentence] = before_judge_item
                write_json(tmp_result_path, tmp_results)
                continue
        
        if judge_item.get("gpt_trans_terms", None) is not None:
            continue
        else:
            
            prompt_origin = generate_prompt(term, originSentence, origin_trans)
            originsentence_term_trans = generate(prompt_origin)
            prompt_mutant = generate_prompt(term, infinsert_mutant, mutant_trans)
            infinsert_mutant_term_trans = generate(prompt_mutant)
            judge_item["gpt_trans_terms"] = [originsentence_term_trans, infinsert_mutant_term_trans]
            judge_item["data_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            write_json(tmp_result_path, tmp_results)

        
    
    output_path = os.path.join(model_result_path, output_filename)
    write_json(output_path, tmp_results)






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sentence_info_folder", type=str)
    parser.add_argument("--sentence_info_filename", type=str)
    parser.add_argument("--output_filename", type=str)
    parser.add_argument("--before_file", type=str, default=None, nargs='?')
    args = parser.parse_args()

    sentence_info_folder = args.sentence_info_folder 
    sentence_info_filename = args.sentence_info_filename
    output_filename = args.output_filename
    before_file = args.before_file

    # sentence_info_folder = "../results/Subtitles-detect"
    # sentence_info_filename = "metamorphic_items_final_google_sbert.json"
    # output_filename = "google-gpt_align_term_sbert.json"
    # before_file = "google-gpt_align_term.json"
    if not os.path.exists(sentence_info_folder):
        os.makedirs(sentence_info_folder)
    ask_gpt(sentence_info_folder, sentence_info_filename, output_filename, before_file)

