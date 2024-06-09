import openai
# from openai import OpenAI
import json
import os
import numpy
from tqdm import tqdm
import time
from typing import List, Any
from tenacity import retry, stop_after_attempt, wait_fixed
import argparse
import time
from datetime import datetime

openai.api_key = ""


temperature = 0

@retry(stop=stop_after_attempt(14))
def generate(input_text):
    chat_completion = openai.ChatCompletion.create(
        messages=[
            {
                "role": "user",
                "content": input_text,
            }
        ],
        model="gpt-3.5-turbo-0125",
        temperature=0,
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

def generate_prompt(term1, sentence1, term2, sentence2, translation):

    prompt = f"You are an English-Chinese Translation Expert, expert in checking whether two phrase terms should have the same translation in sentences. If not, please give the different translation of them.\n\
        Provide response only in following format:  <YES, NO or Not Sure>. Be as lenient as possible in judging. If you give \"NO\", give the different translations of them in following format: Different translations: <term1: translation1, term2: translation2>. Do not include anything else in response. \n\
        Can these two phrases <{term1}> and <{term2}> have the same Chinese translation: <{translation}> in the sentences <{sentence1}> and <{sentence2}>? \n\
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
        tmp_result_path_before = read_json(before_file_name)


    if os.path.exists(tmp_result_path):
        tmp_results = read_json(tmp_result_path)
    else:
        data = read_json(sentence_info_path)
        tmp_results = dict()
        for index, src in enumerate(data):
            if src.get("phrase_bertinsert_metamorphics", None) is None:
                continue
            phrase_bertinsert_metamorphics = src["phrase_bertinsert_metamorphics"]
            if len(phrase_bertinsert_metamorphics) != 1:
                continue
            phrase_bertinsert_metamorphic = phrase_bertinsert_metamorphics[0]
            mutanted_terms = phrase_bertinsert_metamorphic["mutanted_terms"]
            bert_mutants = phrase_bertinsert_metamorphic["bertmutants"]
            term = src["origin_term"]
            markedsentence = src["phrase_marked_Sentence"]
            judge_item = dict()
            same_trans_terms = dict()
            for j, term_trans_similarity in enumerate(phrase_bertinsert_metamorphic["phrase_bertinsert_term_similarities"]):
                
                if round(term_trans_similarity,3) >= 1.0:
                    same_term = mutanted_terms[j]
                    same_term_mutant = bert_mutants[j]
                    same_term_item = dict()
                    same_term_item["mutant_term"] = same_term
                    same_term_item["mutant_sentence"] = same_term_mutant
                    same_term_item["index"] = j
                    same_trans_terms[same_term] = same_term_item
            if same_trans_terms:
                judge_item["origin_term"] = term
                judge_item["originSentence"] = src["originSentence"]
                judge_item["same_trans_terms"] = same_trans_terms
                judge_item["origin_term_trans"] = src["origin_term_trans"]
                tmp_results[markedsentence] = judge_item

        write_json(tmp_result_path, tmp_results)
    
    for marked_sentence, judge_item in tqdm(tmp_results.items()):
        origin_term = judge_item["origin_term"]
        originSentence = judge_item["originSentence"]
        origin_term_trans = judge_item["origin_term_trans"]
        same_trans_terms = judge_item["same_trans_terms"]
        if tmp_result_path_before.get(marked_sentence, None) is not None:
            before_judge_item = tmp_result_path_before[marked_sentence]
            if before_judge_item.get("gpt_checked", None) is not None:
                tmp_results[marked_sentence] = before_judge_item
                write_json(tmp_result_path, tmp_results)
                continue
        for same_term, same_term_item in same_trans_terms.items():
            if same_term_item.get("gpt_exam_label", None) is not None:
                continue
            else:
                mutant_term = same_term_item["mutant_term"]
                mutant_sentence = same_term_item["mutant_sentence"]
                prompt = generate_prompt(origin_term, originSentence, mutant_term, mutant_sentence, origin_term_trans)
                gpt_exam_label = generate(prompt)
                same_term_item["gpt_exam_label"] = gpt_exam_label
                same_term_item["Data_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                if judge_item.get("gpt_checked", None) is None:
                    judge_item["gpt_checked"] = 1
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
    if not os.path.exists(sentence_info_folder):
        os.makedirs(sentence_info_folder)
    ask_gpt(sentence_info_folder, sentence_info_filename, output_filename, before_file)

