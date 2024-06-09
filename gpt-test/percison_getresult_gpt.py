import json

def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    input_folder = "./results/manual_result/percision_gpt"
    mr_types = ["info_term", "info_sentence", "bert_replace"]
    mt_systems = ["gpt"]
    result_str = ""
    for i in range(len(mr_types)):
        for j in range(len(mt_systems)):
            mr_type = mr_types[i]
            mt_system = mt_systems[j]
            json_file = f"{input_folder}/{mr_type}_{mt_system}_conflict_solved.json"
            data = read_json(json_file)
            count_is_error = 0
            count_no_error = 0
            for key in data:
                item = data[key]
                if item["final_result"] == 1:
                    count_is_error += 1
                elif item["final_result"] == 0:
                    count_no_error += 1
                else:
                    raise ValueError(f"error in {json_file}")
            result_str += f"{mr_type}_{mt_system}: {count_is_error}/{count_no_error+count_is_error}\n"
    with open(f"{input_folder}/percision.txt", "w") as f:
        f.write(result_str)
            
