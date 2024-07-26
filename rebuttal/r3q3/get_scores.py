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
import unite_score as unite_score


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





# read lines in txt file
def read_lines_in_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


# main
if __name__ == "__main__":
    json_folder = "../results/refer_label/precision"
    error_types = ["info_term", "info_sentence", "bert_replace"]
    models = ["google"]

    all_data = []
    for error_type in error_types:
        for model in models:
            input_json = f"{json_folder}/{error_type}_{model}_conflict_solved.json"
            questionaire = f"{json_folder}/questionaire/{error_type}_error_{model}_sampled.json"
            with open(input_json, 'r') as f:
                data = json.load(f)
            with open(questionaire, 'r') as f:
                questionaire_data = json.load(f)
            for key, value in data.items():
                id = value["序号"]
                questionaire_item = questionaire_data[id]
                assert value["source sentence"] == questionaire_item["originSentence"]

                value["trans_model"] = model
                if value["final_result"] == 1:
                    value["Type"] = "Error"
                elif value["final_result"] == 0:
                    value["Type"] = "Correct"
                else:
                    raise ValueError("final_result should be 0 or 1")
                all_data.append(value)


    for i in tqdm(range(len(all_data))):
        item = all_data[i]
        origin = item["source sentence"]
        trans = item["translate_result"]
        reference = item["reference"]
        item["unite_score"] = unite_score.get_unite_score(origin, trans, reference)

    write_json_to_file(all_data, f"./results/all_data.json")