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


    data4boxplot_unite = []
    all_data = read_json("./results/all_data.json")

    for i in tqdm(range(len(all_data))):
        item = all_data[i]

        data4boxplot_unite.append({"Type": item["Type"], "Score": item["unite_score"], "Model": item["trans_model"]})
        

    write_json_to_file(data4boxplot_unite, f"./results/unite_scores.json")