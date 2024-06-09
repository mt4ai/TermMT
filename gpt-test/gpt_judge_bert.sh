area="sampled"
current_time="detect"
model=gpt
scripts_path="../scripts/translate"
sentence_info_folder="./results/$area-$current_time"
sentence_info_filename="metamorphic_items_aligned_$model.json"
output_filename="$model-gpt_judgebertsimi.json"

python ${scripts_path}/llm_judge_bert.py \
    --sentence_info_folder $sentence_info_folder \
    --sentence_info_filename $sentence_info_filename \
    --output_filename $output_filename 