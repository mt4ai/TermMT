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
    json_path = "./questionaires"
    team_folders = ["member1_termmt", "member2_termmt"]
    # get time now
    current_time = "statistics-termmt" #time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    error_1 = [[],[]]
    error_2 = [[],[]]
    error_3 = [[],[]]
    systems = ["google", "bing", "mbart"]
    team1_filter_jsons = {"google": {"align_error": [1,14,30,42,48,51,61,71,77,80,86], "same_replace": [6,47,83]},\
                          "bing": {"align_error": [30,34,39,42,59,70,71,93], "same_replace": [20,97]},\
                          "mbart": {"align_error": [6,9,37,81], "same_replace": [10,13,24,28]}}
    team2_filter_jsons = {"google": {"align_error": [1, 2, 10, 30, 42, 45, 48, 51, 68, 86], "same_replace": [65, 70, 71, 83, 85]},\
                          "bing": {"align_error": [13, 21, 34, 41, 42, 49, 52, 54, 59, 61, 70, 71, 76, 87], "same_replace": [20, 30, 94, 97]},\
                          "mbart": {"align_error": [1, 3, 4, 20, 25, 27, 29, 31, 37, 42, 47, 63, 81, 88], "same_replace": [24, 28, 44, 82]}}
    filter_jsons = [team1_filter_jsons, team2_filter_jsons]
    
    error_index_json = dict()
    for system in systems:
        error_index_json[system] = dict()

    for i in range(len(systems)):
        result = dict()
        system = systems[i]
        area_json = read_json(f"{json_path}/{system}_questionaire.json")
        align_error = set(filter_jsons[0][system]["align_error"]) | set(filter_jsons[1][system]["align_error"])
        same_replace = set(filter_jsons[0][system]["same_replace"]) | set(filter_jsons[1][system]["same_replace"])
        data1 = read_xlsx(f"{folder_path}/{team_folders[0]}/{system}_questionaire.xlsx")
        data2 = read_xlsx(f"{folder_path}/{team_folders[1]}/{system}_questionaire.xlsx")
        

        assert len(data1) == len(data2)
        assert len(data1)-1 == len(area_json)
        index_error = []
        for i, row in data1.iterrows():
            if i == 0:
                titles = row.values
                continue
            index = int(row.values[0])
            originSentence = row.values[1]

            # generate result of termmt
            if index in align_error:
                continue
            if index in same_replace:
                continue
            # try:
            error_label_insert_term = int(row.values[10])
            error_label_insert_sentence = int(row.values[14])
            error_label_bert_term = int(row.values[21])
            # except:
            #     index_error.append(index)
            #     continue
            
            error_1[0].append(error_label_insert_term)
            error_2[0].append(error_label_insert_sentence)
            error_3[0].append(error_label_bert_term)
            

            if originSentence not in result:
                
                result[originSentence] = dict()
                result[originSentence]["序号"] = row.values[0]
                for title_id in range(1,22):
                    if title_id in [10, 14, 21]:
                        continue
                    if titles[title_id] in ["原句术语翻译", "insert术语翻译", "insert和原句术语翻译相似度", "insert和原句翻译去括号部分相似度", "替换变异",\
                                            "替换术语", "替换翻译", "替换术语翻译", "替换术语和原句术语翻译相似度"]:
                        result[originSentence][titles[title_id]] = eval(row.values[title_id])
                    else:
                        result[originSentence][titles[title_id]] = row.values[title_id]
                result[originSentence]["error_order"] = [titles[10], titles[14], titles[21]]
                result[originSentence]["manual_1_result"] = [error_label_insert_term, error_label_insert_sentence, error_label_bert_term]
            else:
                result[originSentence]["manual_1_result"] = [error_label_insert_term, error_label_insert_sentence, error_label_bert_term]
        error_index_json[system]["error_index_1"] = index_error
        index_error = []
        for i, row in data2.iterrows():
            if i == 0:
                titles = row.values
                continue
            index = int(row.values[0])
            originSentence = row.values[1]
            



            if index in align_error:
                continue
            if index in same_replace:
                continue
            # try:
            error_label_insert_term = int(row.values[10])
            error_label_insert_sentence = int(row.values[14])
            error_label_bert_term = int(row.values[21])
            # except:
            #     index_error.append(index)
            #     continue
            
            error_1[1].append(error_label_insert_term)
            error_2[1].append(error_label_insert_sentence)
            error_3[1].append(error_label_bert_term)
            

            
            result[originSentence]["manual_2_result"] = [error_label_insert_term, error_label_insert_sentence, error_label_bert_term]

            # judge if manual_1_result and manual_2_result are the same, otherwise, further check needed
            if result[originSentence]["manual_1_result"] == result[originSentence]["manual_2_result"]:
                result[originSentence]["final_result"] = result[originSentence]["manual_1_result"]
            else:
                result[originSentence]["final_result"] = "futher check needed"
        error_index_json[system]["error_index_2"] = index_error
        output_folder = f"{folder_path}/{current_time}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # if there is no error, write to file
        if len(error_index_json[system]["error_index_1"]) == 0 and len(error_index_json[system]["error_index_2"]) == 0:
            write_json(result, f"{output_folder}/{system}_origin.json")
            write_json(result, f"{output_folder}/{system}_conflict_solved.json")
        else:
            write_json(error_index_json, f"{output_folder}/{system}_error_index.json")
    
    # if there is no error, compute kappa score
    flag = 0
    for system in systems:
        if len(error_index_json[system]["error_index_1"]) != 0 or len(error_index_json[system]["error_index_2"]) != 0:
            flag = 1
            break
    if flag == 0:
        error_1_kappa = compute_kappa_score(error_1[0], error_1[1])
        error_2_kappa = compute_kappa_score(error_2[0], error_2[1])
        error_3_kappa = compute_kappa_score(error_3[0], error_3[1])
        general_kappa = compute_kappa_score(error_1[0]+error_2[0]+error_3[0], error_1[1]+error_2[1]+error_3[1])
        # write to file
        with open(f"{output_folder}/kappa_score.txt", "w") as f:
            f.write(f"error_1_kappa: {error_1_kappa}\n")
            f.write(f"error_2_kappa: {error_2_kappa}\n")
            f.write(f"error_3_kappa: {error_3_kappa}\n")
            f.write(f"general_kappa: {general_kappa}\n")


            







    