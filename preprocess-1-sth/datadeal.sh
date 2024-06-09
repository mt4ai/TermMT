#!/bin/bash

# make dir
folder_name="results/preprocess"
mkdir "$folder_name"

# get iate terms
dict_script_path="../scripts/dictdeal"
iate_path="../data/IATE_export.csv"
iateout_path="$folder_name/iateterms"
mkdir "$iateout_path"

python "$dict_script_path"/getIateTerm_only_phrase.py "$iate_path" "$iateout_path"


# make dictionary
data_path="../data"
dict_script_path="../scripts/dictdeal"
iate_terms_path="../data/iateterms/iate_phrase_term.txt"
python "$dict_script_path"/dealjson.py \
    --data_path "$data_path" \
    --result_content "$folder_name" \
    --iate_terms_path "$iate_terms_path"


# filter the meaningdict.json
python "$dict_script_path"/filterate.py "$folder_name/meaningdict.jsonl" "$folder_name"

# sentence marking data

# dict_path="./$folder_name/meaningdict_filtered.jsonl"
dict_path="../data/meaningdict_filtered.jsonl"

# iate terms mark
mark_script_path="../scripts/mark"
for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    iate_mark_output_path="$folder_name/iatemark/$area/"
    corpuspath="../data/Bilingual/$area/Bi-$area.txt"
    mkdir "$folder_name/iatemark"
    mkdir "$folder_name/iatemark/$area"
    if_statis_term=True

    python "$mark_script_path"/phrasemarkv3.py "$corpuspath" "$iate_mark_output_path" "$dict_path" "$if_statis_term" "$area"
done

cp -r "$folder_name/iatemark" "../data/iatemark"
