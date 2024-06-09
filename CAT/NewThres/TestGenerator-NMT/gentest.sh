for area in "Subtitles" "Science" "News" "Laws" "Thesis"
do  
    cp -r ../../../detect-1-sth/results/$area-detect/metamorphic_items_final_mbart.json ../../data/$area/metamorphic_items_final_mbart.json
    input_path=../../data/$area/metamorphic_items_final_mbart.json
    output_path=../../data/$area

    python3 bertMuN.py $input_path $output_path/f_en_mu.txt $output_path/en_mu.index
done

