import jieba
import argparse
from tqdm import tqdm
import json
import os

def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

def lst2str(lst):
    return " ".join(lst)

def jiebacut(sentence):
    # delete " " in sentence
    sentence = sentence.replace(" ", "")
    return lst2str(jieba.lcut(sentence))

def jiebacut_file(file_path, json_path=None):
    cutted_dict = dict()
    save_step = 100
    output_file_path = file_path.replace(".txt", "_jiebacut.txt")
    tmp_json_path = file_path.replace(".txt", "_jiebacut.json")
    if json_path is not None and os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            cutted_dict = json.load(f)
    with open(file_path, "r") as f:
        lines = f.readlines()
    for i in tqdm(range(len(lines))):
        original_line = lines[i].strip()
        if original_line in cutted_dict:
            cutted_line = cutted_dict[original_line]
        else:
            cutted_line = jiebacut(original_line).strip()
            cutted_dict[original_line] = cutted_line
        lines[i] = cutted_line
        if i % save_step == 0:
            write_json(cutted_dict, tmp_json_path)
    
    with open(output_file_path, "w") as f:
        for line in lines:
            f.write(line + "\n")
    write_json(cutted_dict, tmp_json_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", type=str, required=True)
    args = parser.parse_args()
    file_path = args.file_path
    # area="Subtitles"
    # model="mbart"
    # file_path = f"../../data/{area}/translation/{model}/en_mu_translations.txt"
    jiebacut_file(file_path)