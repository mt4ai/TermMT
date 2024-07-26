# Rebuttal Response Experiment

## Response
Before starting all experiments, you need to migrate the test results to the current directory
```bash
cp -r ../detect-1-sth/results ./
cp -r ./refer_label ./results
```

We provide our manual result in folder `refer_label`, you can also get your label result by running:

```bash
python label_trans.py
python precison_getresult.py
# after solve conflicts
python precison_getresult.py
```


R3Q1

The questionnaires are constructed by:
```bash
cd r3q1
python sample.py
```
Get the number of errors
```bash
python static_error.py
```
Get the precision (You need to finish the questionaire first. We provide our manual results in the `r3q1/results`)

```bash
python precision_static.py
python precision_getresult.py
```

R3Q2

Sentence BERT: https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2 

Comparision with directly using language model:

```bash
cd r3q2_direct
bash run.sh
```

Change BGE with Sentence BERT. To detect error:

```bash
cd r3q2_change
bash simi_sbert.sh
bash detect_sbert.sh
bash gpt_ask.sh
bash detect_filter.sh
```

To sample and get results:
```bash 
# get number of errors, 
cd r3q2_change
python sample.py
# After finished the questionaire, we provide our manual results in the `r3q2_change/results`
python precison_getresult.py
# after solve conflicts
python precison_getresult.py

```

R3Q3

UniTE: https://github.com/NLP2CT/UniTE

To get result: 
```bash 
# get number of errors
cd r3q3
python get_scores.py
python data4boxplot.py
# get images
python draw_boxplot.py
python accuracy_trend_unite.py

```
