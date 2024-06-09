
scripts_path=../../scripts/manual
for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    input_path_termmt="../../detect-1-sth/results/$area-detect/metamorphic_items_final_google.json"
    input_path_CAT="../../CAT/data/$area/metamorphic_items_final_mbart_with_CAT.json"
    output_path="./parasearch/init"

    mkdir $output_path
    output_path="$output_path/$area.csv"
    count=100

    python ${scripts_path}/make_questionaire_parasearch.py \
        --input_path_termmt $input_path_termmt \
        --input_path_CAT $input_path_CAT \
        --output_path $output_path \
        --count $count
done
