for area in "Subtitles" "Science" "Laws" "News" "Thesis"
do
    output_path=../../data/$area

    python3 desp.py $output_path/f_en_mu.txt $output_path/en_mu.txt
    cp $output_path/en_mu.txt $output_path/f_en_mu.txt
done
