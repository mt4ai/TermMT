import sys
import json
import os

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)
    
def write_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=3)

if __name__ == "__main__":
    area = sys.argv[1]
    model = sys.argv[2]
    # area = "Subtitles"
    # model = "mbart"

    data_folder = f"../../data/{area}"

    f = open(f"{data_folder}/Com_ALL.txt", "r")
    lines = f.readlines()
    f.close()

    origin_items = read_json(f"{data_folder}/metamorphic_items_final_mbart.json")

    id_lst = []
    index2com = dict()
    f = open(f"{data_folder}/en_mu.index", "r")
    index_lines = f.readlines()
    f.close()
    for i in range(0, len(index_lines)):
        id = int(index_lines[i].strip())
        id_lst.append(id)
        index2com[id] = []
    


    # flcs = open(f"{data_folder}/bugs_LCS.txt", "w")
    # fed = open(f"{data_folder}/bugs_ED.txt", "w")
    # ftfidf = open(f"{data_folder}/bugs_TFIDF.txt", "w")
    # fbleu = open(f"{data_folder}/bugs_BLEU.txt", "w")

    # 0.963, 0.963, 0.999, 0.906
    for i in range(0, len(lines), 14):
        lcs = float(lines[i + 4].strip().split()[-2])
        ed = float(lines[i + 5].strip().split()[-2])
        tfidf = float(lines[i + 6].strip().split()[-2])
        bleu = float(lines[i + 7].strip().split()[-2])
        
        ori_trans = lines[i + 8].strip()
        ori = lines[i + 9].strip()
        mu_trans = lines[i + 10].strip()
        mu = lines[i + 11].strip()
    
        index = i//14
        id = id_lst[index]
        com_item = dict()
        com_item["ori"] = ori
        com_item["mu"] = mu
        com_item["ori_trans"] = ori_trans
        com_item["mu_trans"] = mu_trans
        com_item["lcs"] = lcs
        com_item["ed"] = ed
        com_item["tfidf"] = tfidf
        com_item["bleu"] = bleu
        # com_item["bug_lcs"] = lcs < 0.963
        # com_item["bug_ed"] = ed < 0.963
        # com_item["bug_tfidf"] = tfidf < 0.999
        # com_item["bug_bleu"] = bleu < 0.906
        # com_item["is_bug"] = lcs < 0.963
        index2com[id].append(com_item)
        
        # if lcs < 0.963:
        #     flcs.write(mu + "\n")
        #     flcs.write(ori + "\n")
        # if ed < 0.963:
        #     fed.write(mu + "\n")
        #     fed.write(ori + "\n")
        # if tfidf < 0.999:
        #     ftfidf.write(mu + "\n")
        #     ftfidf.write(ori + "\n")
        # if bleu < 0.906:
        #     fbleu.write(mu + "\n")
        #     fbleu.write(ori + "\n")

    # flcs.close()
    # fed.close()
    # ftfidf.close()
    # fbleu.close()
    write_json(index2com, f"{data_folder}/index2com.json")

    for item in origin_items:
        mutant_id = item["mutant_id"]
        if mutant_id not in index2com:
            continue
        com_lst = index2com[mutant_id]
        # cat_error = False
        # for com in com_lst:
        #     if com["bug_bleu"]:
        #         cat_error = True
        #         break
        item["CAT_results"] = com_lst
        # item["CAT_error"] = cat_error

    write_json(origin_items, f"{data_folder}/metamorphic_items_final_{model}_with_CAT.json")

