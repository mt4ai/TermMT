scripts_path="../scripts/translate"area="sampled"
current_time="detect"
model=gpt
sentence_info_folder="./results/$area-$current_time"


sentence_info_filename="metamorphic_items_final_$model.json"
gpt_meancorr_output_filename="$model-gpt_judge_meancorr.json"
before_filename="./results/$area-$before_time/gpt_results/gpt-gpt_judge_meancorr.json"

python ${scripts_path}/llm_judge_mean_corr.py \
    --sentence_info_folder $sentence_info_folder \
    --sentence_info_filename $sentence_info_filename \
    --output_filename $gpt_meancorr_output_filename \


gpt_alignterm_output_filename="$model-gpt_align_term.json"

python ${scripts_path}/llm_gpt_alignterm.py \
    --sentence_info_folder $sentence_info_folder \
    --sentence_info_filename $sentence_info_filename \
    --output_filename $gpt_alignterm_output_filename \

threshold_sentence=0.7
threshold_term=0.5
threshold_phrase_no_larger=0.97

gpt_align_term_file=$sentence_info_folder/gpt_results/$gpt_alignterm_output_filename
gpt_judge_meancorr_file=$sentence_info_folder/gpt_results/$gpt_meancorr_output_filename
