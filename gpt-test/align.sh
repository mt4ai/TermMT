area="sampled"
current_time="detect"
scripts_path=../scripts/translate
output_path=./results/$area-$current_time
align_tool_path=../awesome-align
trans_model=gpt

python ${scripts_path}/trans_align.py \
    --output_path $output_path \
    --align_tool_path $align_tool_path \
    --trans_model $trans_model \
