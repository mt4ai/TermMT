for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    current_time="detect"
    scripts_path=../scripts/translate
    output_path=./results/$area-$current_time

    for trans_model in "mbart" "google" "bing"
    do
        gpt_bertins_judge_file=$output_path/gpt_results/$trans_model-gpt_judgebertsimi.json

        python ${scripts_path}/trans_judge.py \
            --output_path $output_path \
            --trans_model $trans_model \
            --threshold_sentence 0.7 \
            --threshold_term 0.5 \
            --threshold_phrase_no_larger 0.97 \
            --gpt_bertins_judge_file $gpt_bertins_judge_file 
    done
done