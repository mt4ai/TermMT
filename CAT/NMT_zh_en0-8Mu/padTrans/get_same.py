import sys
import json
import os
import time

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

def write_text(string_text, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(string_text)

if __name__ == "__main__":
    area = sys.argv[1]
    model = sys.argv[2]
    metric = sys.argv[3]
    timenow = sys.argv[4]
    # area = "Subtitles_4"
    # model = "mbart"

    data_folder = f"../../data/{area}"
    output_folder = f"{data_folder}/{timenow}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cat_items = read_json(f"{data_folder}/{timenow}/metamorphic_items_final_{model}_CAT.json")
    termmt_items = read_json(f"{data_folder}/metamorphic_item_error_gptfiltered.json")

    same_num = 0
    cat_error_ids = []
    error_key = "CAT_error_" + metric
    for cat in cat_items:
        if error_key in cat and cat[error_key]:
            cat_error_ids.append(cat["mutant_id"])
    
    for termmt in termmt_items:
        if termmt["mutant_id"] in cat_error_ids:
            same_num += 1

    result_str = "error_num_of_CAT:" + str(len(cat_error_ids)) + "\n"\
                + "error_num_of_ours:" + str(len(termmt_items))+ "\n"\
                +"same_errors:"+str(same_num)+" special_errors:"+str(len(termmt_items)-same_num)+"\n"
    write_text(result_str, f"{output_folder}/same_num.txt")

        