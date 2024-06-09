scripts_path="../scripts/translate"

for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    current_time="detect"
    for model in "mbart" "google" "bing"
    do
        sentence_info_folder="./results/$area-$current_time"


        sentence_info_filename="metamorphic_items_final_$model.json"
        gpt_meancorr_output_filename="$model-gpt_judge_meancorr.json"

        python ${scripts_path}/llm_judge_mean_corr.py \
            --sentence_info_folder $sentence_info_folder \
            --sentence_info_filename $sentence_info_filename \
            --output_filename $gpt_meancorr_output_filename


        gpt_alignterm_output_filename="$model-gpt_align_term.json"

        python ${scripts_path}/llm_gpt_alignterm.py \
            --sentence_info_folder $sentence_info_folder \
            --sentence_info_filename $sentence_info_filename \
            --output_filename $gpt_alignterm_output_filename
    done
done

