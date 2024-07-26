for area in "Science" "Laws" "News" "Thesis" #"Subtitles"
do
    current_time="detect"
    output_path=../results/$area-$current_time
    align_tool_path=../../awesome-align
    for trans_model in "google"
    do
        python trans_simi_sbert.py \
            --output_path $output_path \
            --align_tool_path $align_tool_path \
            --trans_model $trans_model 
    done
done
