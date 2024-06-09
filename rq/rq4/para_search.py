import pandas as pd
import json
from sklearn.metrics import f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import os
import time
import numpy as np

# measure the tp of pred_labels
def tp_measure(pred_labels, refer_labels):
    tp = 0
    for i in range(len(pred_labels)):
        if pred_labels[i] == 1 and refer_labels[i] == 1:
            tp += 1
    return tp

# measure the false positive rate of pred_labels
def fpr_measure(pred_labels, refer_labels):
    tn = sum([1 for i in range(len(pred_labels)) if pred_labels[i] == 0 and refer_labels[i] == 0])
    fp = sum([1 for i in range(len(pred_labels)) if pred_labels[i] == 1 and refer_labels[i] == 0])
    return fp/(fp+tn)



# read xlsx file
def read_xlsx(file_path):
    data = pd.read_excel(file_path, header=None)
    return data

# read txt file
def read_txt(file_path):
    with open(file_path, "r") as file:
        data = file.read()
    return data

# read json file
def read_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

# draw the f1 score, precision, recall picture and savethem, and give the best parameters with best precision
def draw_f1_precision_recall(f1_lst, precision_lst, recall_lst, count_errors , parameters_lst, pic_name, pic_path, legend_name):
    plt.figure()
    # print(parameters_lst)
    # plt.plot(parameters_lst, f1_lst, label="f1 score")
    # plt.plot(parameters_lst, precision_lst, label="precision")
    # plt.plot(parameters_lst, recall_lst, label="recall")
    # plt.plot(parameters_lst, count_errors, label="number of errors")
    
    # plt.xlabel("parameters")
    # plt.ylabel("score")
    # 创建第一个子图
    font_size = 16
    fig, ax1 = plt.subplots()
    ax1.spines['top'].set_color('none')
    ax1.spines['right'].set_color('none')
    ax1.grid(True, linestyle='--', alpha=0.5, zorder=0)
    ax1.set_axisbelow(True)


    # 绘制相似度数据
    ax1.plot(parameters_lst, precision_lst, label="precision", color=(231/255, 56/255, 71/255))
    ax1.set_xlabel('Similarity Theshold for '+legend_name, fontsize=font_size)
    ax1.set_ylabel('Score', fontsize=font_size)

    # 创建第二个子图，并共享x轴
    y_paddding = 1.01
    x_padding = 1.01
    ax1.set_xlim(0, 1*x_padding)
    ax2 = ax1.twinx()
    
    ax1.set_ylim(0, 1*y_paddding)
    ax2.set_ylim(0, 300*y_paddding)
    ax2.set_yticks(np.linspace(0, 300, num=6)) 
    ax2.spines['top'].set_color('none')
    ax2.spines['right'].set_color('none')


    # 绘制错误数目数据
    ax2.plot(parameters_lst, count_errors, label="number of errors", color=(69/255, 123/255, 157/255))
    ax2.set_ylabel('Number of Errors', fontsize=font_size)

    # 在第一个子图上设置图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', frameon=False, ncol=2, bbox_to_anchor=(0.5, 1.12), fontsize=font_size)
    ax1.tick_params(axis='both', which='major', labelsize=font_size-2)  # 设置主刻度的大小为12
    ax1.tick_params(axis='both', which='minor', labelsize=font_size-2)
    ax2.tick_params(axis='both', which='major', labelsize=font_size-2)  # 设置主刻度的大小为12
    ax2.tick_params(axis='both', which='minor', labelsize=font_size-2)
    
    plt.tight_layout()
    plt.savefig(pic_path)


# search the best parameters for the metamorphic testing
def search_best_parameters(pred_similaritys, refer_labels, file_floder, pic_name, bg_similarity, ed_similarity, step, legend_name, type="no smaller than"):
    f1_lst = []
    precision_lst = []
    recall_lst = []
    count_errors_lst = []
    bst_precision = -1
    bst_f1 = -1
    bst_tp_mult_precision = -1
    similarity = bg_similarity
    bst_metrics = []
    similarities = []
    candidate_thresholds = []
    
    
    while similarity <= ed_similarity+step/2:
        similarities.append(similarity)
        pred_labels = []
        for item in pred_similaritys:
            if type == "no smaller than":
                if item <= similarity:
                    pred_labels.append(1)
                else:
                    pred_labels.append(0)
            elif type == "no larger than":
                if item >= similarity:
                    pred_labels.append(1)
                else:
                    pred_labels.append(0)
        f_score = f1_score(refer_labels, pred_labels)
        precision = precision_score(refer_labels, pred_labels)
        recall = recall_score(refer_labels, pred_labels)
        tp = tp_measure(pred_labels, refer_labels)    
        count_errors = pred_labels.count(1)

        f1_lst.append(f_score)
        precision_lst.append(precision)
        recall_lst.append(recall)
        count_errors_lst.append(count_errors)

        


        if precision > bst_precision:
            bst_precision = precision
            bst_metrics = [f_score, precision, recall, similarity, count_errors]
            candidate_thresholds = [[similarity, count_errors]]
        elif precision == bst_precision:
            candidate_thresholds.append([similarity, count_errors])
            if recall > bst_metrics[2]:
                bst_metrics = [f_score, precision, recall, similarity, count_errors]
        
        # if precision == bst_precision and f_score > bst_metrics[0]:
        #     bst_metrics = [f_score, precision, recall, similarity]
        # if f_score == bst_f1 and precision > bst_metrics[1]:
        #     bst_metrics = [f_score, precision, recall, similarity]
        similarity = similarity + step
        similarity = round(similarity, 3)
        
    draw_f1_precision_recall(f1_lst, precision_lst, recall_lst, count_errors_lst, similarities, pic_name, f"{file_floder}/{pic_name}.png", legend_name)
    bst_metrics.append(candidate_thresholds)
    return bst_metrics       


# main
def main():
    file_floder = "./results"
    areas = ["Laws", "News", "Science", "Subtitles", "Thesis"]
    ques_time = "statistics"
    current_time = "pic_draw"# time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    cat_score = "lcs"

    
    infer_term_error_referlabels = []
    infer_sentence_error_referlabels = []
    bert_termerror_referlabels = []
    
    insert_term_similaritys = []
    insert_sentence_similaritys = []
    bert_term_similaritys = []
    refer_labels = []
    human_label_result_strs = []
    
    area_label_dict = {}
    for area in areas:
        area_label_dict[area] = []
        file_path = f"{file_floder}/{ques_time}/{area}_conflict_solved.json"
        data = read_json(file_path)
        
        insert_term_error = 0
        insert_sentence_error = 0
        replace_term_error = 0
        general_error = 0
        for key in data.keys():
            item = data[key]
            index = item["序号"]
            labels = item["final_result"]

            insert_term_error += labels[0]
            insert_sentence_error += labels[1]
            replace_term_error += labels[2]
            general_error += max(labels)

            infer_term_error_referlabels.append(labels[0])
            infer_sentence_error_referlabels.append(labels[1])
            bert_termerror_referlabels.append(labels[2])

            insert_term_similaritys.append(item["insert和原句术语翻译相似度"][0])
            insert_sentence_similaritys.append(item["insert和原句翻译去括号部分相似度"][0])
            bert_term_similaritys.append(max(item["替换术语和原句术语翻译相似度"]))

            area_label_dict[area].append([index, item["insert和原句术语翻译相似度"][0], item["insert和原句翻译去括号部分相似度"][0], max(item["替换术语和原句术语翻译相似度"])])

            # if any label is 1, then the refer label is 1, else 0
            if max(labels) not in [0, 1]:
                print(f"error label: {labels}")
            refer_labels.append(max(labels))
        s=f"area: {area}, insert_sentence_error: {insert_sentence_error}, insert_term_error: {insert_term_error}, replace_term_error: {replace_term_error}, general_error: {general_error}, effective_count: {len(data)}"
        human_label_result_strs.append(s)

        cat_error = 0
        cat_error_referlabels = []
        cat_similaritys = []
        human_label_result_strs_CAT = []
        cat_file_path = f"{file_floder}/{ques_time}/{area}_CAT_conflict_solved.json"
        cat_data = read_json(cat_file_path)
        for key in cat_data.keys():
            item = cat_data[key]
            labels = item["final_result"]
            cat_error += labels[0]
            cat_error_referlabels.append(labels[0])
            cat_similaritys.append(min([result[cat_score] for result in item["CAT_results"]]))
        s=f"area: {area}, cat_error: {cat_error}, effective_count: {len(cat_data)}"
        human_label_result_strs_CAT.append(s)




    output_folder = f"{file_floder}/{current_time}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(f"{output_folder}/human_label_result.txt", "w") as f:
        f.write("\n".join(human_label_result_strs))

    result_strs = []
    # search the best parameters for insert sentence error
    bg_similarity = 0 
    ed_similarity = 1
    step = 0.01
    bst_insert_term_similarity = 0
    bst_bert_term_similarity = 0

    # # search the best parameters for insert term error
    # legend_name = "MR1_insert_term"
    # bst_metrics = search_best_parameters(insert_term_similaritys, infer_term_error_referlabels, output_folder, "insert term similaritis", bg_similarity, ed_similarity, step, legend_name, type="no smaller than")
    # bst_insert_term_similarity = bst_metrics[3]
    # result_strs.append(f"insert term error best similarity: {bst_metrics[3]}, f1: {bst_metrics[0]}, precision: {bst_metrics[1]}, recall: {bst_metrics[2]}, candidate_thresholds: {bst_metrics[5]}")
  
    # # search the best parameters for insert sentence error
    # legend_name = "MR2_insert_sentence"
    # bst_metrics = search_best_parameters(insert_sentence_similaritys, infer_sentence_error_referlabels, output_folder, "insert sentence similaritis" , bg_similarity, ed_similarity, step, legend_name, type="no smaller than")
    # bst_insert_sentence_similarity = bst_metrics[3]

    # result_strs.append(f"insert sentence error best similarity: {bst_metrics[3]}, f1: {bst_metrics[0]}, precision: {bst_metrics[1]}, recall: {bst_metrics[2]}, candidate_thresholds: {bst_metrics[5]}")
    
  
    # # search the best parameters for bert term error
    # legend_name = "MR3_bert_replace"
    # bst_metrics = search_best_parameters(bert_term_similaritys, bert_termerror_referlabels, output_folder, "bert term similaritis", bg_similarity, ed_similarity, step, legend_name, type="no larger than")
    # bst_bert_term_similarity = bst_metrics[3]
    # result_strs.append(f"bert term error best similarity: {bst_metrics[3]}, f1: {bst_metrics[0]}, precision: {bst_metrics[1]}, recall: {bst_metrics[2]}, candidate_thresholds: {bst_metrics[5]}")

    # search the best parameters for cat error
    legend_name = "CAT"
    bst_metrics = search_best_parameters(cat_similaritys, cat_error_referlabels, output_folder, "cat similaritis", bg_similarity, ed_similarity, step, legend_name, type="no smaller than")
    bst_cat_similarity = bst_metrics[3]
    result_strs.append(f"cat error best similarity: {bst_metrics[3]}, f1: {bst_metrics[0]}, precision: {bst_metrics[1]}, recall: {bst_metrics[2]}, candidate_thresholds: {bst_metrics[5]}")


    bst_insert_term_similarity = 0.5
    bst_insert_sentence_similarity = 0.7
    bst_bert_term_similarity = 0.97

    # search error with bst parameters
    result_strs.append("error number with similarities")
    for area in areas:
        insert_sentence_error = 0
        insert_term_error = 0
        replace_term_error = 0
        general_error = 0
        for item in area_label_dict[area]:
            if item[1] <= bst_insert_term_similarity:
                insert_sentence_error += 1
            if item[2] <= bst_insert_sentence_similarity:
                insert_term_error += 1
            if item[3] >= bst_bert_term_similarity:
                replace_term_error += 1
            if item[1] <= bst_insert_term_similarity or item[2] <= bst_insert_sentence_similarity or item[3] >= bst_bert_term_similarity:
                general_error += 1
        result_strs.append(f"area: {area}, insert_sentence_error: {insert_sentence_error}, insert_term_error: {insert_term_error}, replace_term_error: {replace_term_error}, general_error: {general_error}")
    
    # caculate the false positive rate
    result_strs.append("false positive rate")
    
        
    with open(f"{output_folder}/search_result.txt", "w") as f:
        f.write("\n".join(result_strs))

if __name__ == "__main__":
    main()