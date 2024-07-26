import pandas as pd
import json
from sklearn.metrics import f1_score, accuracy_score, recall_score
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

# draw the f1 score, accuracy, recall picture and savethem, and give the best parameters with best accuracy
def draw_f1_accuracy_recall(f1_lst, accuracy_lst, recall_lst, count_errors , parameters_lst, pic_name, pic_path, legend_name):
    plt.figure()
    # print(parameters_lst)
    # plt.plot(parameters_lst, f1_lst, label="f1 score")
    # plt.plot(parameters_lst, accuracy_lst, label="accuracy")
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
    ax1.plot(parameters_lst, accuracy_lst, label="Accuracy", color=(231/255, 56/255, 71/255))
    ax1.set_xlabel('Similarity Theshold for '+legend_name, fontsize=font_size)
    ax1.set_ylabel('Score', fontsize=font_size)

    # 创建第二个子图，并共享x轴
    y_paddding = 1.01
    x_padding = 1.01
    ax1.set_xlim(0*x_padding, 1*x_padding)
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
    
    # plt.axhline(y=249, color='g', linestyle='--')
    plt.tight_layout()
    plt.savefig(pic_path)



# search the best parameters for the metamorphic testing
def search_best_parameters(pred_similaritys, refer_labels, file_floder, pic_name, bg_similarity, ed_similarity, step, legend_name, type="no smaller than"):
    f1_lst = []
    accuracy_lst = []
    recall_lst = []
    count_errors_lst = []
    bst_accuracy = -1
    bst_f1 = -1
    bst_tp_mult_accuracy = -1
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
        accuracy = accuracy_score(refer_labels, pred_labels)
        recall = recall_score(refer_labels, pred_labels)
        tp = tp_measure(pred_labels, refer_labels)    
        count_errors = pred_labels.count(1)

        f1_lst.append(f_score)
        accuracy_lst.append(accuracy)
        recall_lst.append(recall)
        count_errors_lst.append(count_errors)

        


        if accuracy > bst_accuracy:
            bst_accuracy = accuracy
            bst_metrics = [f_score, accuracy, recall, similarity, count_errors]
            candidate_thresholds = [[similarity, count_errors]]
        elif accuracy == bst_accuracy:
            candidate_thresholds.append([similarity, count_errors])
            if recall > bst_metrics[2]:
                bst_metrics = [f_score, accuracy, recall, similarity, count_errors]
        
        # if accuracy == bst_accuracy and f_score > bst_metrics[0]:
        #     bst_metrics = [f_score, accuracy, recall, similarity]
        # if f_score == bst_f1 and accuracy > bst_metrics[1]:
        #     bst_metrics = [f_score, accuracy, recall, similarity]
        similarity = similarity + step
        similarity = round(similarity, 3)
        
    draw_f1_accuracy_recall(f1_lst, accuracy_lst, recall_lst, count_errors_lst, similarities, pic_name, f"{file_floder}/{pic_name}.png", legend_name)
    bst_metrics.append(candidate_thresholds)
    return bst_metrics       


# main
def main():

    file = "data4boxplot.json"
    data = read_json(file)
    pred_similaritys = []
    refer_labels = []

    for item in data:
        pred_similaritys.append(item["Similarity"])
        if item["Type"] == "Error":
            refer_labels.append(1)
        else:
            refer_labels.append(0)
    bg_similarity = 0
    ed_similarity = 1
    step = 0.01
    bst_metrics = search_best_parameters(pred_similaritys, refer_labels, "./results", "Accuracy_trend", bg_similarity, ed_similarity, step, "sentence bert")

    # write into txt
    with open("./results/best_parameters.txt", "w") as f:
        f.write(f"best similarity: {bst_metrics[3]}, count_error:{bst_metrics[4]}, f1: {bst_metrics[0]}, accuracy: {bst_metrics[1]}, recall: {bst_metrics[2]}, candidate_thresholds: {bst_metrics[5]}")




if __name__ == "__main__":
    main()