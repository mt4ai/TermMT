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

def json_to_csv(json_list, output_file):
    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "source sentence", "reference", "translate_result", "is error translated"])
        for index, item in enumerate(json_list):
            
            originSentence = item["originSentence"]
            term_trans_refer = item["phrase_marked_Sentence_refertrans"]
            origin_trans = item["origin_trans"]

            writer.writerow([index, originSentence, term_trans_refer, origin_trans,""])


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

    current_time = "refer_label"
    
    output_path = f"./results/questionaire/{current_time}"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    error_types = ["info_term", "info_sentence", "bert_replace"]

    for error_type in error_types:
        data = read_json(f"./results/precision/questionaire/{error_type}_error_google_sampled.json")
        output_path_csv = f"{output_path}/{error_type}_error_google.csv"
        json_to_csv(data, output_path_csv)