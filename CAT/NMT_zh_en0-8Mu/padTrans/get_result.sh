current_time=lcs60
model=mbart
metric=lcs

# default thereholds: 0.963, 0.963, 0.999, 0.906(lcs, ed, tfidf, bleu)
lcs_th=0.6
ed_th=0.963
tfidf_th=0.999
bleu_th=0.906

area=Subtitles

python3 read_human.py $area $model $current_time $lcs_th $ed_th $tfidf_th $bleu_th
python3 get_same.py $area $model $metric $current_time
area=Science

python3 read_human.py $area $model $current_time $lcs_th $ed_th $tfidf_th $bleu_th
python3 get_same.py $area $model $metric $current_time
area=Laws

python3 read_human.py $area $model $current_time $lcs_th $ed_th $tfidf_th $bleu_th
python3 get_same.py $area $model $metric $current_time
area=News

python3 read_human.py $area $model $current_time $lcs_th $ed_th $tfidf_th $bleu_th
python3 get_same.py $area $model $metric $current_time
area=Thesis

python3 read_human.py $area $model $current_time $lcs_th $ed_th $tfidf_th $bleu_th
python3 get_same.py $area $model $metric $current_time