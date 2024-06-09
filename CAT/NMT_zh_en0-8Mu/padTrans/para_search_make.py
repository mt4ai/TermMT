import sys
import json
import os
import csv

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

def read_csv(file):
    with open(file, "r", encoding="utf-8") as f:
        return list(csv.reader(f))

if __name__ == "__main__":
    # area = sys.argv[1]
    # model = sys.argv[2]
    area = "Subtitles"
    model = "mbart"


    data_folder = f"../../data/{area}"


    origin_items = read_json(f"{data_folder}/metamorphic_items_final_mbart_CAT.json")

    questionaire = read_csv(f"../../data/para_search/{area}.csv")

    tgt_lines = []
    for i in range(1, len(questionaire)):
        tgt_lines.append(questionaire[i][1])



    selected_sentences = []