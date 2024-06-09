for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    model=mbart

    translate_file=../../data/$area/translation/$model/en_mu_translations.txt

    # python3 jiebacut.py --file_path $translate_file
    python3 read2diff.py --area $area --model $model
    python3 read_diff.py $area $model
done
# python3 readbugs.py $area $model
# python3 read_human.py $area $model
# python3 get_same.py $area $model