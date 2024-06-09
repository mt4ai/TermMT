# area="Science"
# current_time="2024-03-26_15-12-06" #$(date +"%Y-%m-%d_%H-%M-%S")
# area="Laws"
# current_time="2024-04-06_18-43-27"
# area=News
# current_time="2024-04-07_17-45-04"
# area="Thesis"
# current_time="2024-04-07_18-57-26"
# area="Subtitles"
# current_time="2024-03-25_14-46-32"
area="sampled"
current_time="detect"
# model=gpt
scripts_path=../scripts/translate
output_path=./results/$area-$current_time
trans_model=gpt
gpt_bertins_judge_file=$output_path/gpt_results/$trans_model-gpt_judgebertsimi.json

python ${scripts_path}/trans_judge.py \
    --output_path $output_path \
    --trans_model $trans_model \
    --threshold_sentence 0.7 \
    --threshold_term 0.5 \
    --threshold_phrase_no_larger 0.97 \
    --gpt_bertins_judge_file $gpt_bertins_judge_file 