import sys
import os
import math
import collections
import json
import time

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

def tobool(s):
    if s == "True":
        return True
    else:
        return False

area = sys.argv[1]
model = sys.argv[2]
timenow = sys.argv[3]
lcs_threshold = float(sys.argv[4])
ed_threshold = float(sys.argv[5])
tfidf_threshold = float(sys.argv[6])
bleu_threshold = float(sys.argv[7])

print("lcs_threshold:", lcs_threshold)
print("ed_threshold:", ed_threshold)
print("tfidf_threshold:", tfidf_threshold)
print("bleu_threshold:", bleu_threshold)


# area = "Subtitles"
# model = "mbart"
data_folder = f"../../data/{area}"


output_folder = f"{data_folder}/{timenow}"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

filter_list = []
#with open("../../NMT_zh_en0/google/human_google/train.txt") as f:
#    lines = f.readlines()
#    f.close()
#    now_count_all = 0
#    for i in range(0, len(lines), 11):
#        now_count_all += 1
#        if now_count_all == 45:
#            continue
#        filter_list.append(lines[i + 6].strip())
#        if now_count_all >= 100:
#            break

t_out_list = [[] for t in range(4)]

ground_new = [{} for i in range(9)]

sum = [0] * 8

origin_items = read_json(f"{data_folder}/metamorphic_items_final_{model}.json")

id_lst = []
index2com = dict()
f = open(f"{data_folder}/en_mu.index", "r")
index_lines = f.readlines()
f.close()
for i in range(0, len(index_lines)):
    id = int(index_lines[i].strip())
    id_lst.append(id)
    index2com[id] = []

filter_count = 0
with open(f"{data_folder}/Com_ALL.txt", "r") as f:
    lines = f.readlines()
    count_data = len(lines) // 14
    for i in range(0, len(lines), 14):
        vote = 0
        com_item = dict()
        index = i//14
        id = id_lst[index]
        if lines[i + 9].strip() in filter_list:
            filter_count += 1
            continue
        for t in range(8):
            #ground_new[t][lines[i + 12].strip()] = (tobool(lines[i + t].strip().split()[-1]))
            length = 1#float(max(len(lines[i + 9].split()), len(lines[i + 11].split())))
            #length = math.sqrt(length)
            if t < 4:
                #continue
                delta = float(lines[i + t].strip().split()[1])
                sc1 = float(lines[i + t].strip().split()[2])
                sc2 = float(lines[i + t].strip().split()[3])
                if t != 3:
                    delta *= length
                    sc1 *= length
                    sc2 *= length
                #length = len()
                if delta >= max(sc1, sc2) * [0.05, 0.08, 0.06, 0.08][t]:
                    ground_new[t][lines[i + 9].strip()] = True#(tobool(lines[i + t].strip().split()[-1]))
                else:
                    ground_new[t][lines[i + 9].strip()] = False
                if ground_new[t][lines[i + 9].strip()] == False:
                    vote += 0.5
                sum[t] += float(delta)
            else:
                #sum[t] += 1 - float(lines[i + t].strip().split()[1])
                if t == 7:
                    score = float(lines[i + t].strip().split()[1])
                    com_item["score_bleu"] = score
                    if float(lines[i + t].strip().split()[1]) < bleu_threshold:
                        ground_new[t][lines[i + 9].strip()] = True
                        com_item["bug_bleu"] = True
                    else:
                        ground_new[t][lines[i + 9].strip()] = False
                        com_item["bug_bleu"] = False
                        vote += 1
                else:
                    score = float(lines[i + t].strip().split()[1]) * length
                    com_item["score_" + ["lcs", "ed", "tfidf"][t - 4]] = score
                    if score < [lcs_threshold, ed_threshold, tfidf_threshold][t - 4]:
                        ground_new[t][lines[i + 9].strip()] = True
                        com_item["bug_" + ["lcs", "ed", "tfidf"][t - 4]] = True
                    else:
                        ground_new[t][lines[i + 9].strip()] = False
                        com_item["bug_" + ["lcs", "ed", "tfidf"][t - 4]] = False
                        vote += 1
                sum[t] += 1 - score

        if vote >= 3:
            ground_new[8][lines[i + 9].strip()] = False
            com_item["vote_bug"] = False
        else:
            ground_new[8][lines[i + 9].strip()] = True
            com_item["vote_bug"] = True
        com_item["origin"] = lines[i + 9].strip()
        com_item["origin_trans"] = lines[i + 8].strip()
        com_item["mutant"] = lines[i + 11].strip()
        com_item["mutant_trans"] = lines[i + 10].strip()
        index2com[id].append(com_item)
write_json(index2com, f"{output_folder}/index2com.json")
for item in origin_items:
    mutant_id = item["mutant_id"]
    if mutant_id not in index2com:
        continue
    com_lst = index2com[mutant_id]
    cat_error_lcs = False
    cat_error_ed = False
    cat_error_tfidf = False
    cat_error_bleu = False
    cat_error_vote = False
    for com in com_lst:
        if com["bug_lcs"]:
            cat_error_lcs = True
        if com["bug_ed"]:
            cat_error_ed = True
        if com["bug_tfidf"]:
            cat_error_tfidf = True
        if com["bug_bleu"]:
            cat_error_bleu = True
        if com["vote_bug"]:
            cat_error_vote = True
    item["CAT_results"] = com_lst
    item["CAT_error_lcs"] = cat_error_lcs
    item["CAT_error_ed"] = cat_error_ed
    item["CAT_error_tfidf"] = cat_error_tfidf
    item["CAT_error_bleu"] = cat_error_bleu
    item["CAT_error_vote"] = cat_error_vote


write_json(origin_items, f"{output_folder}/metamorphic_items_final_{model}_CAT.json")
write_json(origin_items, f"{data_folder}/metamorphic_items_final_{model}_CAT.json")

#count_data = count
#print (count_data)
#print (count)
#assert count_data == count
#assert len(ground_new[0]) == len(ground)

index = ["LCS-O", "ED-O", "TF-O", "BLEU-O", "LCS", "ED", "TF", "BLEU", "Vote"]
out_list = [[] for i in range(9)]
dic = {}
dic[True] = "P"
dic[False] = "N"
#dic[tuple([False])] = "TN"
#dic[tuple([False])] = "FN"
#dic[tuple([True])] = "FP"
#dic[tuple([True])] = "TP"

count = [collections.Counter() for i in range(9)]
#sum = [0] * 8

print (filter_count)
#assert filter_count == 99

count_all = 0
for i in ground_new[0]:
    for t in range(9):
        tp = ground_new[t][i]#tuple([ground[i], ground_new[t][i]])
        out_list[t].append(tp)
        count[t][tp] += 1
        if t == 0:
            count_all += 1
#print (count_data)
#print (count_all)
#assert count_all == count_data
for item in dic:
    print (dic[item])
f = open(f"{output_folder}/out.answer", "w")
for i in range(9):
    f.write(index[i] + "")
    for item in dic:
        f.write(" & ")
        f.write(str(count[i][item]) + " (" + str(round(float(count[i][item]) / count_all * 100, 2)) + "\\%) ")
    f.write("\\\\\n")
f.close()

for s in sum:
    print (s / count_data)
