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
    json_path = "./parasearch/init"
    team_folders = ["member1", "member2"]
    # get time now
    current_time = "statistics" #time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    error_1 = [[],[]]
    error_2 = [[],[]]
    error_3 = [[],[]]
    error_4 = [[],[]]
    areas = ["Laws", "News", "Science", "Subtitles", "Thesis"]
    team1_filter_jsons = {"Laws": {"align_error": [11,24,28,33,48,58,74,83], "same_replace": [18,21,25,34,64,65,68,76,91,99]},\
                          "News": {"align_error": [11,15,17,42,43,78], "same_replace": [18,52,54,61]},\
                          "Science": {"align_error": [0,9,13,17,19,27,31,39,48,53,55,98,99], "same_replace": [15,23,40,49,52,81,84]},\
                          "Subtitles": {"align_error": [64,76], "same_replace": [37,38,40,61,69,80,96]},\
                          "Thesis": {"align_error": [32,51], "same_replace": [40,65,75,84]}}
    team2_filter_jsons = {"Laws": {"align_error": [11, 24, 48, 58, 74, 83], "same_replace": [9, 19, 25, 31, 34, 91, 99]},\
                          "News": {"align_error": [5, 11, 15, 17, 42, 43, 54, 60, 65, 78], "same_replace": [2, 18, 48, 52, 61]},\
                          "Science": {"align_error": [0, 9, 13, 17, 19, 20, 25, 27, 31, 39, 48, 53, 56, 66, 70, 81, 85, 87, 94, 98], "same_replace": [15, 23, 40, 49, 52]},\
                          "Subtitles": {"align_error": [17, 24, 64], "same_replace": [23, 35, 44, 67]},\
                          "Thesis": {"align_error": [0, 7, 17, 19, 21, 51, 52, 71, 80, 86], "same_replace": [27, 60]}}
    filter_jsons = [team1_filter_jsons, team2_filter_jsons]
    
    for i in range(len(areas)):
        result = dict()
        result_CAT = dict()
        area = areas[i]
        area_json = read_json(f"{json_path}/{area}_questionaire_item.json")
        align_error = set(filter_jsons[0][area]["align_error"]) | set(filter_jsons[1][area]["align_error"])
        same_replace = set(filter_jsons[0][area]["same_replace"]) | set(filter_jsons[1][area]["same_replace"])
        data1 = read_xlsx(f"{folder_path}/{team_folders[0]}/{area}.xlsx")
        data2 = read_xlsx(f"{folder_path}/{team_folders[1]}/{area}.xlsx")
        assert len(data1) == len(data2)
        assert len(data1)-1 == len(area_json)
        for i, row in data1.iterrows():
            if i == 0:
                titles = row.values
                continue
            index = int(row.values[0])
            originSentence = row.values[1]

            # generate result of CAT
            CAT_json_item = area_json[index]["mbart_cat_item"]
            error_label_CAT = int(row.values[26])
            error_4[0].append(error_label_CAT)
            if originSentence not in result_CAT:
                assert CAT_json_item["originSentence"] == originSentence
                result_CAT[originSentence] = dict()
                result_CAT[originSentence]["序号"] = row.values[0]
                for title_id in range(22, 26):
                    if titles[title_id] in ["CAT变异", "CAT变异翻译"]:
                        result_CAT[originSentence][titles[title_id]] = eval(row.values[title_id])
                    else:
                        result_CAT[originSentence][titles[title_id]] = row.values[title_id]
                result_CAT[originSentence]["CAT_results"] = CAT_json_item["CAT_results"]
                result_CAT[originSentence]["error_order"] = [titles[26]]
                result_CAT[originSentence]["manual_1_result"] = [error_label_CAT]


            # generate result of termmt
            if index in align_error:
                continue
            if index in same_replace:
                continue
            
            error_label_insert_term = int(row.values[10])
            error_label_insert_sentence = int(row.values[14])
            error_label_bert_term = int(row.values[21])
            
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
        for i, row in data2.iterrows():
            if i == 0:
                titles = row.values
                continue
            index = int(row.values[0])
            originSentence = row.values[1]
            error_label_CAT = int(row.values[26])
            error_4[1].append(error_label_CAT)
            result_CAT[originSentence]["manual_2_result"] = [error_label_CAT]
            if result_CAT[originSentence]["manual_1_result"] == result_CAT[originSentence]["manual_2_result"]:
                result_CAT[originSentence]["final_result"] = result_CAT[originSentence]["manual_1_result"]
            else:
                result_CAT[originSentence]["final_result"] = "futher check needed"


            if index in align_error:
                continue
            if index in same_replace:
                continue
            
            error_label_insert_term = int(row.values[10])
            error_label_insert_sentence = int(row.values[14])
            error_label_bert_term = int(row.values[21])
            
            error_1[1].append(error_label_insert_term)
            error_2[1].append(error_label_insert_sentence)
            error_3[1].append(error_label_bert_term)
            

            
            result[originSentence]["manual_2_result"] = [error_label_insert_term, error_label_insert_sentence, error_label_bert_term]

            # judge if manual_1_result and manual_2_result are the same, otherwise, further check needed
            if result[originSentence]["manual_1_result"] == result[originSentence]["manual_2_result"]:
                result[originSentence]["final_result"] = result[originSentence]["manual_1_result"]
            else:
                result[originSentence]["final_result"] = "futher check needed"
            
        output_folder = f"{folder_path}/{current_time}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        write_json(result, f"{output_folder}/{area}_origin.json")
        write_json(result, f"{output_folder}/{area}_conflict_solved.json")
        write_json(result_CAT, f"{output_folder}/{area}_CAT_origin.json")
        write_json(result_CAT, f"{output_folder}/{area}_CAT_conflict_solved.json")
    error_1_kappa = compute_kappa_score(error_1[0], error_1[1])
    error_2_kappa = compute_kappa_score(error_2[0], error_2[1])
    error_3_kappa = compute_kappa_score(error_3[0], error_3[1])
    error_4_kappa = compute_kappa_score(error_4[0], error_4[1])
    general_kappa = (error_1_kappa + error_2_kappa + error_3_kappa + error_4_kappa) / 4
    # write to file
    with open(f"{output_folder}/kappa_score.txt", "w") as f:
        f.write(f"error_1_kappa: {error_1_kappa}\n")
        f.write(f"error_2_kappa: {error_2_kappa}\n")
        f.write(f"error_3_kappa: {error_3_kappa}\n")
        f.write(f"error_4_kappa: {error_4_kappa}\n")
        f.write(f"general_kappa: {general_kappa}\n")


            







    