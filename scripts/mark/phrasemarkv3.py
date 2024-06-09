import re
from tqdm import tqdm
import sys
import os
import json

def read_jsonl(file_path: str):
    data = []
    # max_lines = 100000
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            # if len(data) >= max_lines:
            #     break
            json_data = json.loads(line)
            data.append(json_data)
    return data

def load_dictionary(dictpath):
    dictionary = set()
    if dictpath.endswith('.jsonl'):
        with open(dictpath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # create dict
            for line in tqdm(lines, desc="Processing lines", ncols=80):
                meaning = json.loads(line)
                if meaning['meanitems'] == []:
                    continue
                dictionary.add(meaning['term'])
    else:
        with open(dictpath, 'r', encoding='utf-8') as file:
            for line in file:

                term = line.strip()
                dictionary.add(term)
    return dictionary

def judge_sentence_bracket_right(sentence):
    bracket_mark = 0
    for i in range(len(sentence)):
        if sentence[i] == '(':
            bracket_mark += 1
        elif sentence[i] == ')':
            bracket_mark -= 1
        if bracket_mark < 0:
            return False
    return bracket_mark == 0

def annotate_terms(dictpath, corpuspath, outputpath, statis_term):
    dictionary = load_dictionary(dictpath)
    output_lines = []

    with open(corpuspath, 'r', encoding='utf-8') as corpus_file:
        lines = corpus_file.readlines()
        maxlen = lines.__len__()
        lineset = set()
        # maxlen = 100

        for i in tqdm(range(0,maxlen,2), desc='Processing'):
            # only process English part
            line = lines[i].strip()
            # avoid duplicate sentences
            if line in lineset:
                continue
            else:
                lineset.add(line)
            if not line.startswith(' '):  
                sentence = line.strip()
                if not judge_sentence_bracket_right(sentence):
                    continue
                annotated_sentence,haveterm, termset, termcount = annotate_sentence(sentence, dictionary)
                # only deal with sentences that contain and only contain 1 term
                if haveterm and termcount == 1:
                    output_lines.append(annotated_sentence)
                    output_lines.append(lines[i+1].strip())
                    for term in termset:
                        if term in statis_term:
                            statis_term[term] += 1
                        else:
                            statis_term[term] = 1
                # keep the original sentence if no term is found
                # else:
                #     output_lines.append(sentence)
                #     output_lines.append(lines[i+1].strip())
 

    with open(outputpath, 'w', encoding='utf-8') as output_file:
        output_file.write('\n'.join(output_lines))

def annotate_sentence(sentence, dictionary):
    words = re.split('(\w+)', sentence)
    bgword = 0
    endword = 0
    bgloaction = 0
    endlocation = bgloaction + len(words[bgword])
    markresult = ""
    haveterm = False
    termset = set()
    termcount = 0
    
    while bgword < len(words):
        endword = bgword
        endlocation = bgloaction + len(words[bgword])
        maxplocationend = endlocation
        maxwordend = endword
        if is_whitespace_string(words[bgword]):
            markresult = markresult + words[bgword]
            bgloaction = bgloaction + len(words[bgword])
            bgword = bgword + 1
            continue
        while endword < len(words)-1:
            endword = endword + 1
            endlocation = endlocation + len(words[endword])
            if is_whitespace_string(words[endword]):
                continue
            tphrase = sentence[bgloaction:endlocation]
            # if tphrase in dictionary or tphrase.lower() or tphrase lowercase initial letter in dictionary
            if tphrase in dictionary:
                maxplocationend = endlocation
                maxwordend = endword
                haveterm = True
                termset.add(tphrase)
                termcount = termcount + 1
            elif tphrase.lower() in dictionary:
                maxplocationend = endlocation
                maxwordend = endword
                haveterm = True
                termset.add(tphrase.lower())
                termcount = termcount + 1

        if maxwordend == bgword:
            markresult = markresult + words[bgword]
            bgloaction = bgloaction + len(words[bgword])
            bgword = bgword + 1
        else:
            markresult = markresult + '[|term:' + sentence[bgloaction:maxplocationend] + '|]'
            bgloaction = maxplocationend
            bgword = maxwordend + 1
    return markresult, haveterm, termset, termcount
    

def is_whitespace_string(text):
    # check if text is empty or contains only whitespaces
    return re.match(r'^\s*$', text) is not None
    
    


# main
if __name__ == '__main__':
    # areas = ["Education", "Laws", "Microblog", "News", "Science", "Spoken", "Subtitles", "Thesis"]
    corpuspath = sys.argv[1]
    output_folder_path = sys.argv[2]
    dictpath = sys.argv[3]
    if_statis_term = sys.argv[4]
    area = sys.argv[5]
    statis_term = dict()

    # for area in areas:
    outputpath = output_folder_path +'phrasemark.txt'
        

    # call function to annotate terms
    annotate_terms(dictpath, corpuspath, outputpath, statis_term)

    if if_statis_term == 'True':
        # sort the terms by frequency
        statis_term = sorted(statis_term.items(), key=lambda item:item[1], reverse=True)
        with open(output_folder_path +'statis_phrase_term.json', 'w', encoding='utf-8') as file:
            for term in statis_term:
                file.write(json.dumps(term, ensure_ascii=False) + '\n')