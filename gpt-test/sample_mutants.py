import json
import random
from typing import Any, List
import os

def rand_sample(samplelist, count, seed):
    print(seed)
    random.seed(seed)
    sampleresult = random.sample(samplelist, count)
    return sampleresult

def read_jsonl(file_path: str):
    data = []
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            json_data = json.loads(line)
            data.append(json_data)
    return data

def write_jsonl(file_path: str, data: List[Any]):
    with open(file_path, 'w', encoding="utf-8") as file:
        for item in data:
            json_line = json.dumps(item,ensure_ascii=False)
            file.write(json_line + '\n')

if __name__ == '__main__':
    areas = ["Subtitles", "Science", "News", "Laws", "Thesis"]
    mutant_data_path = "../data/mutant_results"
    result_samples = []
    general_data = []
    for area in areas:
        file = f"{mutant_data_path}/{area}/generalMutant.jsonl"
        data = read_jsonl(file)
        for item in data:
            item["data_area"] = area
        general_data.extend(data)
    result_samples = rand_sample(general_data, 3000, 123)
    if not os.path.exists(f"{mutant_data_path}/sampled"):
        os.makedirs(f"{mutant_data_path}/sampled")
    write_jsonl(f"{mutant_data_path}/sampled/generalMutant.jsonl", result_samples)
        
    