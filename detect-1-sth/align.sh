for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    current_time="detect"
    scripts_path=../scripts/translate
    output_path=./results/$area-$current_time
    align_tool_path=../awesome-align
    for trans_model in "google" "bing" "mbart"
    do
        python ${scripts_path}/trans_align.py \
            --output_path $output_path \
            --align_tool_path $align_tool_path \
            --trans_model $trans_model 
    done
done
