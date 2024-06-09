for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    current_time="detect"
    for model in "google" "bing" "mbart"
    do
        scripts_path="../scripts/translate"
        sentence_info_folder="./results/$area-$current_time"
        sentence_info_filename="metamorphic_items_aligned_$model.json"
        output_filename="$model-gpt_judgebertsimi.json"
        python ${scripts_path}/llm_judge_bert.py \
            --sentence_info_folder $sentence_info_folder \
            --sentence_info_filename $sentence_info_filename \
            --output_filename $output_filename
    done
done