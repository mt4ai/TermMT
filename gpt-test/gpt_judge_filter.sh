scripts_path="../scripts/translate"
# area="Subtitles"
# current_time="2024-03-25_14-46-32"
# area="Science"
# current_time="2024-03-26_15-12-06"
# area="Laws"
# current_time="2024-04-06_18-43-27"
# area=News
# current_time="2024-04-07_17-45-04"
# area=Thesis
# current_time="2024-04-07_18-57-26"
area="sampled"
current_time="2024-05-10_19-19-18"
model=gpt
sentence_info_folder="./results/$area-$current_time"


sentence_info_filename="metamorphic_items_final_$model.json"
gpt_meancorr_output_filename="$model-gpt_judge_meancorr.json"
# before_filename="$model-gpt_judge_meancorr_1.json"

# python ${scripts_path}/llm_judge_mean_corr.py \
#     --sentence_info_folder $sentence_info_folder \
#     --sentence_info_filename $sentence_info_filename \
#     --output_filename $gpt_meancorr_output_filename \


gpt_alignterm_output_filename="$model-gpt_align_term.json"
# before_filename="$model-gpt_align_term_1.json"

# python ${scripts_path}/llm_gpt_alignterm.py \
#     --sentence_info_folder $sentence_info_folder \
#     --sentence_info_filename $sentence_info_filename \
#     --output_filename $gpt_alignterm_output_filename \

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
    --gpt_judge_meancorr_file $gpt_judge_meancorr_file \