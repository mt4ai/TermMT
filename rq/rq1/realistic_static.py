import pandas as pd
import os
import json
from sklearn.metrics import cohen_kappa_score
import numpy as np
import time

def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# read xlsx file
def read_xlsx(file_path):
    data = pd.read_excel(file_path, header=None)
    return data

def compute_kappa_score(error1, error2):
    error1 = np.array(error1)
    error2 = np.array(error2)
    return cohen_kappa_score(error1, error2)

if __name__ == "__main__":
    folder_path = "./results/manual_result"
    team_folders = ["member1", "member2"]
    # get time now
    current_time = "realistic_result"#time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    info_insert_labels = [[],[]]
    bert_replace_labels = [[], []]
    # realistic = [[],[]]
    areas = ["Thesis", "Laws", "News", "Science", "Subtitles"]
    output_folder = f"{folder_path}/{current_time}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    labels = ["真实", "语法错误", "反常识"]
    label_to_index = {label: idx for idx, label in enumerate(labels)}
    

    for i in range(len(areas)):
        result = dict()
        area = areas[i]
        data1 = read_xlsx(f"{folder_path}/{team_folders[0]}/{area}_realistic.xlsx")
        data2 = read_xlsx(f"{folder_path}/{team_folders[1]}/{area}_realistic.xlsx")
        assert len(data1) == len(data2)
        for k, row in data1.iterrows():
            if k == 0:
                titles = row.values
                continue
            index = int(row.values[0])

            originSentence = row.values[1]
            manual1_result = dict()
            manual1_result["info_insert"] = row.values[4]
            manual1_result["bert_replace"] = row.values[7]
            info_insert_labels[0].append(label_to_index[manual1_result["info_insert"]])
            bert_replace_labels[0].append(label_to_index[manual1_result["bert_replace"]])
            
            if originSentence not in result:
                result[originSentence] = dict()
                result[originSentence]["序号"] = row.values[0]
                for title_id in range(1,len(titles)):
                    if titles[title_id] in ['insert变异是否真实','替换变异是否真实']:
                        continue
                    if titles[title_id] in ["替换变异","替换术语"]:
                        result[originSentence][titles[title_id]] = eval(row.values[title_id])
                    else:
                        result[originSentence][titles[title_id]] = row.values[title_id]

            result[originSentence]["manual_1_result"] = manual1_result
        for k, row in data2.iterrows():
            if k == 0:
                titles = row.values
                continue
            index = int(row.values[0])
            originSentence = row.values[1]
            manual2_result = dict()
            manual2_result["info_insert"] = row.values[4]
            manual2_result["bert_replace"] = row.values[7]
            info_insert_labels[1].append(label_to_index[manual2_result["info_insert"]])
            bert_replace_labels[1].append(label_to_index[manual2_result["bert_replace"]])
            result[originSentence]["manual_2_result"] = manual2_result

            # result[originSentence]["manual_2_result"] = manual_2_result
            if result[originSentence]["manual_1_result"] == result[originSentence]["manual_2_result"]:
                result[originSentence]["final_result"] = result[originSentence]["manual_1_result"]
            else:
                result[originSentence]["final_result"] = "futher check needed"
        write_json(result, f"{output_folder}/{areas[i]}_general.json")
        write_json(result, f"{output_folder}/{areas[i]}_conflict_solved.json")
        result.clear()
    # compute kappa score
    info_insert_kappa = compute_kappa_score(info_insert_labels[0], info_insert_labels[1])
    bert_replace_kappa = compute_kappa_score(bert_replace_labels[0], bert_replace_labels[1])
    general_kappa = compute_kappa_score(info_insert_labels[0]+bert_replace_labels[0], info_insert_labels[1]+bert_replace_labels[1])
    # write to file
    with open(f"{output_folder}/kappa_score.txt", "w") as f:
        f.write(f"info_insert_kappa: {info_insert_kappa}\n")
        f.write(f"bert_replace_kappa: {bert_replace_kappa}\n")
        f.write(f"general_kappa: {general_kappa}\n")
        # for i in range(len(areas)):
        #     info_insert_kappa = compute_kappa_score(info_insert_labels[0][i*100: (i+1)*100], info_insert_labels[1][i*100: (i+1)*100])
        #     bert_replace_kappa = compute_kappa_score(bert_replace_labels[0][i*100: (i+1)*100], bert_replace_labels[1][i*100: (i+1)*100])
        #     f.write(f"{areas[i]}:\n")
        #     f.write(f"info_insert_kappa: {info_insert_kappa}\n")
        #     f.write(f"bert_replace_kappa: {bert_replace_kappa}\n")
        #     f.write("\n")






            







    