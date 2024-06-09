#!/bin/bash

iate_input_path="../data/iatemark"
script_path="../scripts/mutant"
dict_path="../data/meaningdict_filtered.jsonl"
term_level="phrase"

area="Thesis"
mkdir "results"
for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do

    output_path="results/result_$area-mutant"
    mkdir "$output_path"
    iate_output_path="$output_path/iatemutant/Bilingual"
    mkdir "$output_path/iatemutant"
    mkdir "$iate_output_path"

    iatephrase_output_path="$iate_output_path/$term_level"
    mkdir "$iatephrase_output_path"
    python ${script_path}/mutant.py \
        --meaningdict $dict_path \
        --input_path $iate_input_path \
        --output_path $iatephrase_output_path \
        --term_level $term_level \
        --tgtarea $area
    cp -r "$iate_output_path/$term_level/$area" "../data/mutant_results_test"
done
