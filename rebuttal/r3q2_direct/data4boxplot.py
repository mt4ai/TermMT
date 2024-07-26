from tqdm import tqdm
import json

def read_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

# write json lst to file
def write_json_to_file(json_data, file_path):
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    data4boxplot = []

    error_simi_data = read_json("./errors_sbert_simi.json")
    correct_simi_data = read_json("./corrects_sbert_simi.json")

    for i in tqdm(range(len(error_simi_data))):
        error = error_simi_data[i]
        item = {"Type": "Error", "Similarity": error["sbert_simi_ot"], "Model": "google"}
        data4boxplot.append(item)
    for j in tqdm(range(len(correct_simi_data))):
        correct = correct_simi_data[j]
        item = {"Type": "Correct", "Similarity": correct["sbert_simi_ot"], "Model": "google"}
        data4boxplot.append(item)
    write_json_to_file(data4boxplot, f"./data4boxplot.json")