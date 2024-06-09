scripts_path="../scripts/translate"

for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    current_time="detect"
    for model in "google" "bing" "mbart"
    do
        sentence_info_folder="./results/$area-$current_time"


        sentence_info_filename="metamorphic_items_final_$model.json"
        gpt_meancorr_output_filename="$model-gpt_judge_meancorr.json"



        gpt_alignterm_output_filename="$model-gpt_align_term.json"

        threshold_sentence=0.7
        threshold_term=0.5
        threshold_phrase_no_larger=0.97

        gpt_align_term_file=$sentence_info_folder/gpt_results/$gpt_alignterm_output_filename
        gpt_judge_meancorr_file=$sentence_info_folder/gpt_results/$gpt_meancorr_output_filename

        python ${scripts_path}/trans_filter_error.py \
            --output_path $sentence_info_folder \
            --trans_model $model \
            --threshold_sentence $threshold_sentence \
            --threshold_term $threshold_term \
            --threshold_phrase_no_larger $threshold_phrase_no_larger \
            --gpt_align_term_file $gpt_align_term_file \
            --gpt_judge_meancorr_file $gpt_judge_meancorr_file
    done
done