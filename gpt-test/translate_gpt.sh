area=sampled
current_time="detect" #$(date +"%Y-%m-%d_%H-%M-%S")
scripts_path=../scripts/translate
model="gpt"
for trans_file in "originSentences.txt" "phrase_infoinsertmutants.txt" "phrase_bertinsertmutants.txt"
do
    python ${scripts_path}/translate_gpt.py \
        --area $area \
        --time $current_time \
        --model $model \
        --trans_file $trans_file
done