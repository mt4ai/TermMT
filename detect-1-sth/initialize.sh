
for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    scripts_path=../scripts/translate
    phrase_mutant_path=../data/mutant_results/$area/generalMutant.jsonl
    output_path=./results/$area-detect
    mkdir "results"
    mkdir "$output_path"

    python ${scripts_path}/trans_initialize.py \
        --phrase_mutant_path $phrase_mutant_path \
        --output_path $output_path
done

