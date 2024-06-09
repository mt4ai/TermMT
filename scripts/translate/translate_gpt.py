import sys
import os
from pathlib import Path

f = Path(__file__)
sys.path.append(str(f.parent.parent.parent))


import argparse
import json
import time
import datetime
from tenacity import retry, stop_after_attempt, wait_fixed

import pandas as pd
from tqdm import tqdm

# print(sys.path)

# from scripts.translate.google_trans import translate_text_with_google, translate_text_with_google_batch
# from scripts.translate.mbart import translate_mbart
# from scripts.translate.llama_trans import translate_openbuddy
# from scripts.translate.bing_translate import translate_text_with_bing, translate_text_with_bing_batch

from scripts.translate.gpt_trans import translate_text_with_gpt, translate_text_with_gpt_batch

from ast import Yield
from typing import Generator, Iterable, Iterator, List, TypeVar




PARALLEL_MODELS = ["opus", "google", "bing", "gpt"]
ONLINE_MODELS = ["google", "bing", "baidu"]

T = TypeVar('T')
def list_chunked(lst: List[T], n: int) -> Generator[List[T], None, None]:
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

T = TypeVar('T')
def chunked(generator: Iterator[T], n: int) -> Generator[List[T], None, None]:
    """Yield successive n-sized chunks from iterable."""
    while True:
        ret = []
        try:
            for i in range(n):
                ret.append(next(generator))
            yield ret
        except StopIteration as e:
            yield ret
            break


@retry(stop=stop_after_attempt(14))
def auto_translate(src: str, model: str) -> str:
    if src.strip() == "":
        return ""
    if model == "google":
        pass
        # tgt = translate_text_with_google(src)
    # elif model == "bing":
    #     tgt = translate_text_with_bing(src)
    # elif model == "mbart":
    #     tgt = translate_mbart(src, "en", "zh")
    # elif model == "llama":
    #     tgt = translate_openbuddy(src, "en", "zh")
    elif model == "gpt":
        tgt = translate_text_with_gpt(src, "English", "Chinese")
    else:
        raise ValueError("Unknown model: {}".format(model))
    return tgt

@retry(stop=stop_after_attempt(14))
def auto_translate_batch(src: List[str], model: str) -> List[str]:
    if len(src) == 0:
        return []
    if model == "google":
        # tgt = translate_text_with_google_batch(src)
        pass
    # elif model == "bing":
        # tgt = translate_text_with_bing_batch(src)
    elif model == "gpt":
        tgt = translate_text_with_gpt_batch(src, "English", "Chinese")
    else:
        raise ValueError("Unknown model: {}".format(model))
    return tgt

def sort_keys(key):
    try:
        return int(key)
    except ValueError:
        return key
    
def read_src_tgt_from_json(json_path: str) -> List[str]:
    sentence_dict = dict()
    with open(json_path, 'r', encoding='utf8') as jp:
        tmp_result = json.load(jp)
    for key in tmp_result.keys():
        if tmp_result[key].get("TGT", None) is not None:
            src = tmp_result[key]['SRC']
            tgt = tmp_result[key]['TGT']
            time_of_mt = tmp_result[key]['TIME']
            data_time = tmp_result[key]['Data_time']
            sentence_dict[src] = {"TGT": tgt, "TIME": time_of_mt, "Data_time": data_time}
    return sentence_dict

def translate(sentence_info_folder: str, sentence_info_filename: str, model: str, output_filename: str, already_file: str = None):
    # Save tmp result to a json file
    model_result_path = f"{sentence_info_folder}/translation/{model}"
    if not os.path.exists(model_result_path):
        os.makedirs(model_result_path)
    sentence_info_path = os.path.join(sentence_info_folder, sentence_info_filename)
    tmp_result_path = os.path.join(model_result_path, sentence_info_filename.split(".")[0] + '_' + model + '.json')
    output_path = os.path.join(model_result_path, f"{output_filename}.csv")
    output_path_txt = os.path.join(model_result_path, f"{output_filename}.txt")
    if already_file!=None and os.path.exists(already_file):
        sentence_dict = read_src_tgt_from_json(already_file)
    else:
        sentence_dict = dict()
    if os.path.exists(tmp_result_path):
        with open(tmp_result_path, 'r', encoding='utf8') as trp:
            tmp_result = json.load(trp)

                    
    else:
        sentence_lst = list()
        with open(sentence_info_path, 'r', encoding='utf8') as sip:
            for line in sip:
                sentence_lst.append(line.strip())
        tmp_result = dict()
        for index, src in enumerate(sentence_lst):
            tmp_result[str(index)] = dict()
            tmp_result[str(index)]['SRC'] = src
        with open(tmp_result_path, 'w', encoding='utf8') as trp:
            json.dump(tmp_result, trp, ensure_ascii=False, indent=3)
            # json.dump(tmp_result, trp, ensure_ascii=False, indent=3, sort_keys=True, default=convert_keys_to_int)
    CHUNK_SIZE = 10
    SAVE_INTERVAL = 1
    lst = sorted([int(k) for k in tmp_result.keys()])
    # lst = lst[0: 60]
    chunked_list = list(list_chunked(lst, CHUNK_SIZE))
    for (chunk_index, chunk_src) in tqdm(enumerate(chunked_list), total=len(chunked_list)):
        need_translated_chunk_src = []
        need_translated_chunk_id = []
        for index, id in enumerate(chunk_src):
            str_id = str(id)
            src = tmp_result[str_id]['SRC']
            if sentence_dict.get(src, None) is not None:
                tmp_result[str_id]["TGT"] = sentence_dict[src]["TGT"]
                tmp_result[str_id]["TIME"] = sentence_dict[src]["TIME"]
                tmp_result[str_id]["Data_time"] = sentence_dict[src]["Data_time"]
                continue
            if tmp_result[str_id].get("TGT", None) is not None:
                continue
            else:
                need_translated_chunk_id.append(str_id)
                need_translated_chunk_src.append(tmp_result[str_id]['SRC'])
        
        if model in PARALLEL_MODELS:
            tgts = auto_translate_batch(need_translated_chunk_src, model)

        for index, (str_id, src) in enumerate(zip(need_translated_chunk_id, need_translated_chunk_src)):
            if tmp_result[str_id].get("TGT", None) is not None:
                continue
            else:
                start = time.time()
                if model in PARALLEL_MODELS:
                    tgt = tgts[index]
                else:
                    tgt = auto_translate(src, model)
                tmp_result[str_id]["TGT"] = tgt
                tmp_result[str_id]["TIME"] = time.time() - start
                tmp_result[str_id]["Data_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if model in ["baidu"]:
                    time.sleep(1)

        if model in ["google"]:
            time.sleep(0.1)
        if len(need_translated_chunk_src) > 0 and chunk_index % SAVE_INTERVAL == 0:
            with open(tmp_result_path, 'w', encoding='utf8') as rp:
                json.dump(tmp_result, rp, ensure_ascii=False, indent=3)

    with open(tmp_result_path, 'w', encoding='utf8') as rp:
        json.dump(tmp_result, rp, ensure_ascii=False, indent=3)
    
    # Save tmp result to csv
    src_lines = list()
    tgt_lines = list()
    datatime_lines = list()
    total_time = 0.0
    for src_line in tmp_result.keys():
        if tmp_result[src_line].get("TGT", None) is None:
            continue
        if tmp_result[src_line].get("TIME", None) is None:
            continue
        if tmp_result[src_line].get("Data_time", None) is None:
            continue
        if tmp_result[src_line].get("TIME", None) is None:
            continue

        src_lines.append(tmp_result[src_line]['SRC'])
        tgt_lines.append(tmp_result[src_line]['TGT'])
        datatime_lines.append(tmp_result[src_line]['Data_time'])
        total_time += tmp_result[src_line]['TIME']

    print("Translation by {} cost {} (second)".format(model, total_time))
    result = pd.DataFrame({'src': src_lines, 'tgt': tgt_lines})
    result.to_csv(output_path, index=False)
    with open(output_path_txt, 'w', encoding='utf8') as op:
        for tgt in tgt_lines:
            # remove all of the \n in tgt
            tgt_clean = tgt.replace("\n", "")
            op.write(tgt_clean + "\n")

if __name__ == '__main__':
    # # parameters
    # area="Subtitles"
    # trans_time = "2024-03-13_19-11-20"
    # model = "google"
    parser = argparse.ArgumentParser()
    parser.add_argument("--area", type=str, required=True)
    parser.add_argument("--time", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--trans_file", type=str, required=True)
    parser.add_argument("--already_file", type=str, default=None)
    args = parser.parse_args()

    area = args.area
    trans_time = args.time
    model = args.model
    info_filename = args.trans_file
    already_file = args.already_file

    sentence_info_folder = f"./results/{area}-{trans_time}"


    if not os.path.exists(f"{sentence_info_folder}/translation"):
        os.makedirs(f"{sentence_info_folder}/translation")

    # translate
     #"originSentences.txt", "phrase_infoinsertmutants.txt", "phrase_bertinsertmutants.txt"]

    output_filename = info_filename.split(".")[0] + f"_translations"
    translate(sentence_info_folder, info_filename, model, output_filename, already_file)