import json

def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    input_folder = "./results/manual_result/realistic_result"
    areas = ["Thesis", "Laws", "News", "Science", "Subtitles"]
    result_str = ""
    for i in range(len(areas)):
        area = areas[i]
        json_file = f"{input_folder}/{area}_conflict_solved.json"
        data = read_json(json_file)
        labels = ["真实", "语法错误", "反常识"]
        mt_types = ["info_insert", "bert_replace"]
        count_info_insert = dict()
        count_bert_replace = dict()
        for label in labels:
            count_info_insert[label] = 0
            count_bert_replace[label] = 0

        for key in data:
            item = data[key]
            final_result = item["final_result"]
            info_result = final_result["info_insert"]
            bert_result = final_result["bert_replace"]
            count_info_insert[info_result] += 1
            count_bert_replace[bert_result] += 1
            
        result_str += f"{area}: \n"
        result_str += f"info_insert: {count_info_insert}\n"
        result_str += f"bert_replace: {count_bert_replace}\n"
    with open(f"{input_folder}/percision.txt", "w") as f:
        f.write(result_str)
            
