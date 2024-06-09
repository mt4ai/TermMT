# TermMT: Metamorphic Testing for Terminology Translation

This is the source code for the paper "Evaluating Terminology Translation in Machine Translation Systems via Metamorphic Testing".

## Dependencies
First, you need to install the dependencies:

```bash
pip install -r requirements.txt
```

Codes in this repository are tested under the environment of `Python 3.7.16`. When calling the "gpt-3.5-turbo-0125" api, `openai==0.28.1` is required under `Python 3.8.18`.

## Prepare dataset
For terminology corpus, please download from the following links:
* IATE: https://iate.europa.eu/download-iate
* Wiktionary: https://dumps.wikimedia.org/enwiktionary/

Download datasets to the path `data` named `IATE_export.csv` and `wikiarticles.xml`.

For sentence corpus, due to the licenses of the original NLP datasets, we do not provide download links here, please submit applications and download from the following projects.

The list of datasets:
* UM-Corpus

Unzip datasets to the path `data`.

## Prepare models
For the required models, we provide their download URLs. The list of models:
* BERT: https://huggingface.co/google-bert/bert-base-cased
* flair: https://huggingface.co/flair/pos-english
* BGE: (en) https://huggingface.co/BAAI/bge-base-en-v1.5 (zh) https://huggingface.co/BAAI/bge-base-zh-v1.5
* mBART: https://huggingface.co/facebook/mbart-large-50-many-to-many-mmt

Please put the downloaded model into the folder `models`

## Proprecess
First, we need to construct term dictionary and annotate sentences. Enter the folder `preprocess-1-sth` and run:
```bash
bash datadeal.sh
```
To ensure grammatical consistency, the dictionary needs to be grammatically checked. In particular, we placed our generated and manually checked dictionary files in `data/meaningdict_filtered.jsonl`.
 
## Mutant
Second, we mutate the original sentences. Enter the folder `mutant-1-sth` and run the bash file mutant.sh:
```bash
bash mutant.sh
```
The mutation results are in the `results` folder.

## Translate
Enter the folder `detect-1-sth`. Before starting the translation process, first initialize:
```bash
bash initialize.sh
```
Then, translate the original sentences and mutated sentence:
```bash
bash translate.sh
```

## Alignment
For the alignment step, please follow the steps in https://github.com/neulab/awesome-align to prepare the required model, then go to the folder `detect-1-sth` and run the following command:
```bash
bash align.sh
```

## Error Detect
Go to the folder `detect-1-sth` and run the following command to get bug reports:
```bash
# under python 3.8 with gpt api
bash gpt_bert.sh
# under python 3.7
bash detect.sh
# under python 3.8 with gpt api
bash gpt_ask.sh
# under python 3.7
bash detect_filter.sh
```


## Research Questions
Except for RQ4, which requires entering the `CAT` folder in the root directory when using CAT, the remaining RQ experiments are completed in the RQ folder.
RQ1: How correct is our mutated sentence generation?
The questionnaires are constructed by:
```bash
cd rq1
python realistic_make_questionaire.py
```
We put our results in `rq1/results/our_manual_result`, run the following code to get the results
```bash
cd rq1
cp -r results/our_manual_result/member1 results/manual_result
cp -r results/our_manual_result/member2 results/manual_result
python realistic_static.py
cp -r results/our_manual_result/realistic_result results/manual_result
python realistic_getresult.py
```

RQ2: How effectively does our method TermMT find translation errors?

Run following to get error count:
```bash
cd rq2
python statis_error.py
```
The questionnaires are constructed by:
```bash
cd rq2
python make_questionaire.py
```
We put our results in `rq2/results/our_manual_result`, run the following code to get the results
```bash
cd rq1
cp -r results/our_manual_result/member1 results/manual_result
cp -r results/our_manual_result/member2 results/manual_result
python precision_static.py
cp -r results/our_manual_result/precision results/manual_result
python precison_getresult.py
```
RQ3: How does the similarity threshold impact our approach?
The questionnaires are constructed by:
```bash
cd rq3
python make_questionaire_parasearch.py
```
We put our results in `rq3/results/our_manual_result`, run the following code to get the results
```bash
cd rq3
cp -r results/our_manual_result/member1_termmt results
cp -r results/our_manual_result/member2_termmt results
python para_merge_termmt.py
cp -r results/our_manual_result/statistics-termmt results
python para_search_termmt.py
```

RQ4: How does TermMT compare with the SOTA method?
For the use of CAT, you can go to https://github.com/zysszy/CAT to view the specific usage.

Enter the folder `CAT` in the root directory. Then, run the following code to generate mutations:
```bash
cd ./CAT/NewThres/TestGenerator-NMT
bash gentest.sh
```
After getting the translation using code similar to the one above, run the following code to generate CAT error reports and comparative experimental results:
```bash
cd ./CAT/NMT_zh_en0-8Mu/padTrans
bash desp.sh
bash cal_metric.sh
bash get_result.sh
python draw_overlap.py
```
For the threshold search part, you need to go to the `rq/rq4` folder. First, generate the questionnaire:
```bash
cd rq/rq4
bash manual_parasearch_questionaire.sh
```
Then run the following code to generate the results. We put our questionnaire results in the `results/our_manual_result` folder.
```bash
cp -r results/our_manual_result/member1 results
cp -r results/our_manual_result/member2 results
python para_merge.py
cp -r results/our_manual_result/statistics results
python para_search.py
```

## Discussions
Discussion 2:
```bash
cd overlap
python get_overlap.py
```

Discussion 3:
First, select the sample, and then perform error detection. The error detection step is similar to the previous: 
```bash
python sample_mutants.py
bash initialize.sh
bash translate_gpt.sh
bash align.sh
bash gpt_judge_bert.sh
bash judge.sh
bash gpt_judge_filter_gen.sh
bash gpt_judge_filter.sh
```
Our manual result is in folder `gpt-test/results/our_manual_result` 

Discussion 4:
See the folder `cases` for screenshots of the errors.