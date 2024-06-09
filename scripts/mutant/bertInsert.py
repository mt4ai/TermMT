import os
# os.environ["CUDA_VISIBLE_DEVICES"]="1"
import nltk
from tqdm import tqdm
import numpy as np
import string
import math
import torch
import sys
import torch.nn.functional as F
import re
import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import wordnet as wn
import time
import random
from copy import deepcopy
import mysplit


from transformers import BertConfig, BertTokenizer, BertModel, RobertaTokenizer, RobertaModel, BertForMaskedLM


nouns = {x.name().split('.', 1)[0] for x in wn.all_synsets('n')}
K_Number = 100
Max_Mutants = 5

ft = time.time()



berttokenizer = BertTokenizer.from_pretrained('../models/bert-base-cased')
bertmodel = BertForMaskedLM.from_pretrained("../models/bert-base-cased")
bertori = BertModel.from_pretrained("../models/bert-base-cased")

# berttokenizer = BertTokenizer.from_pretrained('../../models/bert-base-cased')
# bertmodel = BertForMaskedLM.from_pretrained("../../models/bert-base-cased")
# bertori = BertModel.from_pretrained("../../models/bert-base-cased")

bertmodel.eval().cuda()#.to(torch.device("cuda:0"))
bertori.eval().cuda()#.to(torch.device("cuda:1"))

wnl = WordNetLemmatizer()
stemmer = PorterStemmer()
# lemmatize the word
def lemmatize(word):
    return wnl.lemmatize(word).lower()

# lemmatize words
def lemmatize_words(text):
    words = text.lower().split()
    lem_words = [lemmatize(word) for word in words]
    return ' '.join(lem_words)

# stem words
def stem_words(text):
    words = text.lower().split()
    stem_words = [stemmer.stem(word) for word in words]
    return ' '.join(stem_words)

# get the origin term without []
def getOriginSentenceLst(sentencelst):
    originSentence = []
    for word in sentencelst:
        if word.startswith("[|term:") and word.endswith("|]") and len(word) > 2:
            originSentence.append(word[7:-2])
        else:
            originSentence.append(word)
    return originSentence

# get origin sentence without [ and ]
def getOriginSentence(sentence):
    return sentence.replace("[|term:", "").replace("|]", "")

# split sentence into words
def splitSentence(sentence):

    return mysplit.splitSentence(sentence)

def lst2str(lst):
    return " ".join(lst)



def BertM (bert, berttoken, bertori, inpori, termindex, limitlocations, originSentence):
    slst = inpori.copy()
    tokensbfterm = berttoken.tokenize(lst2str(slst[:termindex]))
    tokensofterm = berttoken.tokenize(slst[termindex])
    origin_term = slst[termindex]
    if termindex+1 < len(slst):
        tokensafterterm = berttoken.tokenize(lst2str(slst[termindex+1:]))
    else:
        tokensafterterm = []
    tokens = tokensbfterm + tokensofterm + tokensafterterm
    
    bgmskid = len(tokensbfterm)
    edmskid = bgmskid + len(tokensofterm)
    allowed_range = []
    limitlocationsset = set(limitlocations)
    splited_term = origin_term.split()
    # limit the locations of the term for mutation
    count = bgmskid
    for i in range(len(splited_term)):
        tokenized_word = berttoken.tokenize(splited_term[i])
        if i in limitlocationsset:
            allowed_range.append([count, count+len(tokenized_word)])
        count += len(tokenized_word)

    # tokens = berttoken.tokenize(sentence)
    batchsize = 1000 // len(tokens)
    gen = []
    ltokens = ["[CLS]"] + tokens + ["[SEP]"]
    try:
        encoding = [berttoken.convert_tokens_to_ids(ltokens[0:i] + ["[MASK]"] + ltokens[i + 1:]) for i in range(1, len(ltokens) - 1)]#.cuda()
    except:
        return " ".join(tokens), gen
    p = []
    for i in range(0, len(encoding), batchsize):
        tensor = torch.tensor(encoding[i: min(len(encoding), i + batchsize)]).cuda()
        pre = F.softmax(bert(tensor)[0], dim=-1).data.cpu()
        p.append(pre)
    pre = torch.cat(p, 0)
    tarl = [[tokens, -1]]

    for allowrange in allowed_range:
        for i in range(allowrange[0], allowrange[1]):
            if tokens[i] in string.punctuation:
                continue
            topk = torch.topk(pre[i][i + 1], K_Number)#.tolist()
            value = topk[0].numpy()
            topk = topk[1].numpy().tolist()

            topkTokens = berttoken.convert_ids_to_tokens(topk)

            for index in range(len(topkTokens)):
                if value[index] < 0.05:
                    break
                tt = topkTokens[index]
                if tt in string.punctuation:
                    continue
                if tt.strip() == tokens[i].strip():
                    continue
                l = deepcopy(tokens)
                l[i] = tt
                tarl.append([l, i, value[index]])
        
    if len(tarl) == 0:
        return " ".join(tokens), gen
        
    
    
    lDB = []
    for i in range(0, len(tarl), batchsize):
        lDB.append(bertori(torch.tensor([berttoken.convert_tokens_to_ids(["[CLS]"] + l[0] + ["[SEP]"]) for l in tarl[i: min(i + batchsize, len(tarl))]]).cuda())[0].data.cpu().numpy())
    lDB = np.concatenate(lDB, axis=0)
    lDA = lDB[0]
    
    assert len(lDB) == len(tarl)
    tarl = tarl[1:]
    lDB = lDB[1:]
    # print([tarl[i][1] for i in range(len(tarl))])
    for t in range(len(lDB)):
        DB = lDB[t][tarl[t][1]]
        DA = lDA[tarl[t][1]]
        cossim = np.sum(DA * DB) / (np.sqrt(np.sum(DA * DA)) * np.sqrt(np.sum(DB * DB)))
        # if sentences are too similar, will lead to overfitting mutation, if sentences are too different, will lead to meaningless mutation
        if cossim < 0.85 :
            continue
        insert_word = tarl[t][0][tarl[t][1]]
        if not insert_word in nouns:
            continue
        sen_term = berttoken.decode(berttoken.encode(tarl[t][0])[bgmskid+1:edmskid+1])
        # sen = lst2str(getOriginSentenceLst(splitSentence(sen)))
        if sen_term.lower() == origin_term.lower():
            continue
        # if delete all \W, the sentence is the same as origin sentence, continue
        if re.sub(r"\W", "", sen_term.lower()) == re.sub(r"\W", "", origin_term.lower()):
            continue
        lemmatize_sen_term = lemmatize_words(sen_term.lower())
        lemmatize_origin_term = lemmatize_words(origin_term.lower())
        # if lemmatize the sentence is the same as origin sentence, continue
        if lemmatize_sen_term == lemmatize_origin_term:
            continue
        # if stem the sentence is the same as origin sentence, continue
        if stem_words(sen_term.lower()) == stem_words(origin_term.lower()):
            continue
        if stem_words(lemmatize_sen_term) == stem_words(lemmatize_origin_term):
            continue



        # term_slst = slst.copy()
        if origin_term in originSentence:
            sen = originSentence.replace(origin_term, sen_term)
        else:
            # 抛出异常
            raise Exception("origin_term not in originSentence")
        gen.append([float(cossim), sen, sen_term])

    tarresult = originSentence


    return tarresult, gen


def get_insert_mutants(s,i, limitlocations, originSentence):
    tar, gen = BertM(bertmodel, berttokenizer, bertori, s, i, limitlocations, originSentence)
    return tar, gen

# l = "A Study of [|term:Part of Speech|] Classification of Mongolian Language for Information Processing"
# llst = getOriginSentenceLst(splitSentence(l))
# # print(llst)
# origin_s = getOriginSentence(l)
# index = llst.index("Part of Speech")
# print (get_insert_mutants(llst, index, [0,2], origin_s))
# print (berttokenizer.decode(berttokenizer.encode(l)))
