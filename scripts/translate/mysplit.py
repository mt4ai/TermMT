import re

def lst2str(lst):
    return " ".join(lst)

# split sentence into words
def splitSentence(sentence):
    pattern = r'(\[\|term:.*?\|\])'
    words = re.split(pattern, sentence)
    result = []
    for part in words:
        if part.startswith("[|term:") and part.endswith("|]"):
            result.append(part)
        else:
            # result += re.findall(r"[\w']+|[^\w\s]", part)
            result += part.split()
    return result

# combine word_mark and phrase_mark sentence
def combine_mark_sentences(word_mark_sentence, phrase_mark_sentence):
    # get the word level terms in word_mark_sentence

    pattern = r'(\[\|term:.*?\|\])'
    word_mark_terms = re.findall(pattern, word_mark_sentence)
    word_mark_terms = [word_mark_term[7:-2] for word_mark_term in word_mark_terms]
    # spilt phrase_mark_sentence into words, and mark words in word_mark_terms
    # target is to ignore the word level terms in phrase level terms
    split_pattern = r'(\[\|term:.*?\|\])'
    phrase_mark_words = re.split(split_pattern, phrase_mark_sentence)
    result = []
    for i in range(len(phrase_mark_words)):
        if phrase_mark_words[i].startswith("[|term:") and phrase_mark_words[i].endswith("|]"):
            result.append(phrase_mark_words[i])
        else:
            word_part_lst = phrase_mark_words[i].split()
            for word_part in word_part_lst:
                
                word_clean = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', word_part)
                if word_clean in word_mark_terms:
                    word_part = word_part.replace(word_clean, f'[|term:{word_clean}|]')
                    result.append(word_part)
                else:
                    result.append(word_part)
    return lst2str(result)