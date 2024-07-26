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
    folder_path = "./results"
    team_folders = ["manual1", "manual2"]
    # get time now
    current_time = "precision"#time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    info_term = [[],[]]
    info_sentence = [[],[]]
    bert_replace = [[],[]]
    # realistic = [[],[]]
    mr_types = ["info_term", "info_sentence", "bert_replace"]
    general_labels = [[[],[]],[[],[]],[[],[]]]
    mt_systems = ["google"]
    output_folder = f"{folder_path}/{current_time}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


    

    for i in range(len(mr_types)):
        result = dict()
        for j in range(len(mt_systems)):
            data1 = read_xlsx(f"{folder_path}/{team_folders[0]}/{mr_types[i]}_error_{mt_systems[j]}.xlsx")
            data2 = read_xlsx(f"{folder_path}/{team_folders[1]}/{mr_types[i]}_error_{mt_systems[j]}.xlsx")
            assert len(data1) == len(data2)
            for k, row in data1.iterrows():
                if k == 0:
                    titles = row.values
                    continue
                index = int(row.values[0])
                originSentence = row.values[1]
                if row.values[-1] == "有错误":
                    manual_1_result = 1
                elif row.values[-1] == "无错误":
                    manual_1_result = 0
                else:
                    raise ValueError(f"error in {mr_types[i]}_error_{mt_systems[j]}.xlsx, team1")
                general_labels[i][0].append(manual_1_result)
                if originSentence not in result:
                    result[originSentence] = dict()
                    result[originSentence]["序号"] = row.values[0]
                    for title_id in range(1,len(titles)-1):
                        if titles[title_id] in ["原句术语翻译", "替换变异",\
                                            "替换术语", "替换翻译", "替换术语翻译"]:
                            result[originSentence][titles[title_id]] = eval(row.values[title_id])
                        else:
                            result[originSentence][titles[title_id]] = row.values[title_id]
                    result[originSentence]["manual_1_result"] = manual_1_result
                else:
                    result[originSentence]["manual_1_result"] = manual_1_result
            for k, row in data2.iterrows():
                if k == 0:
                    titles = row.values
                    continue
                index = int(row.values[0])
                originSentence = row.values[1]
                if row.values[-1] == "有错误":
                    manual_2_result = 1
                elif row.values[-1] == "无错误":
                    manual_2_result = 0
                else:
                    raise ValueError(f"error in {mr_types[i]}_error_{mt_systems[j]}.xlsx, team2")
                general_labels[i][1].append(manual_2_result)
                result[originSentence]["manual_2_result"] = manual_2_result
                if result[originSentence]["manual_1_result"] == result[originSentence]["manual_2_result"]:
                    result[originSentence]["final_result"] = result[originSentence]["manual_1_result"]
                else:
                    result[originSentence]["final_result"] = "futher check needed"
            write_json(result, f"{output_folder}/{mr_types[i]}_{mt_systems[j]}_general.json")
            write_json(result, f"{output_folder}/{mr_types[i]}_{mt_systems[j]}_conflict_solved.json")
            result.clear()
    # compute kappa score
    print(len(general_labels[0][0]), len(general_labels[0][1]))
    print(sum([1 for i in range(len(general_labels[0][0])) if general_labels[0][0][i] != general_labels[0][1][i]]) )
    info_term_kappa = compute_kappa_score(general_labels[0][0], general_labels[0][1])
    print(len(general_labels[1][0]), len(general_labels[1][1]))
    print(sum([1 for i in range(len(general_labels[1][0])) if general_labels[1][0][i] != general_labels[1][1][i]]) )
    info_sentence_kappa = compute_kappa_score(general_labels[1][0], general_labels[1][1])
    print(len(general_labels[2][0]), len(general_labels[2][1]))
    print(sum([1 for i in range(len(general_labels[2][0])) if general_labels[2][0][i] != general_labels[2][1][i]]) )
    bert_replace_kappa = compute_kappa_score(general_labels[2][0], general_labels[2][1])
    general_kappa = compute_kappa_score(general_labels[0][0]+general_labels[1][0]+general_labels[2][0], general_labels[0][1]+general_labels[1][1]+general_labels[2][1])
    # write to file
    with open(f"{output_folder}/kappa_score.txt", "w") as f:
        f.write(f"info_term_kappa: {info_term_kappa}\n")
        f.write(f"info_sentence_kappa: {info_sentence_kappa}\n")
        f.write(f"bert_replace_kappa: {bert_replace_kappa}\n")
        f.write(f"general_kappa: {general_kappa}\n")





            







    