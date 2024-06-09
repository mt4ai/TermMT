for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    current_time="detect"
    scripts_path=../scripts/translate
    for model in "mbart" "google" "bing"
    do
        for trans_file in "originSentences.txt" "phrase_infoinsertmutants.txt" "phrase_bertinsertmutants.txt"
        do

            python ${scripts_path}/translate.py \
                --area $area \
                --time $current_time \
                --model $model \
                --trans_file $trans_file
        done
    done
done