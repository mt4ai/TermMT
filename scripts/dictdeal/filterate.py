import json
import re
import sys
from typing import Any, List

tolow_first = ["A","To","An","The", "This", "As","In","On","At","By","For","Of","With","To","From","And","Or","But","Nor", "Any",\
                "Something" ,"Substitution", "Unrefined", "Region", "Regions", "Former", "Inflation", "Federal", "That", "Such", "One",\
                "Three", "Island", "Country", "Until", "Sometimes", "Capital:", "It", "They", "When", "Usually", "Methods", 'Part']

# lower the first word of the meaning
def lower_first_word(meaning):
    return meaning[0].lower() + meaning[1:]

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

# remove nested brackets content
def remove_nested_parentheses_content(s):
    stack = []
    result = ''

    for i, char in enumerate(s):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                stack.pop()
        elif not stack:
            # if char is space and next char is bracket, skip the space
            if char == ' ' and i + 1 < len(s) and s[i + 1] == '(':
                continue
            result += char

    return result

# deal with error fixed matched phrase
def deal_error_fixed_phrase(meaning):
    if "western suburb in Derby" in meaning:
        meaning = meaning.replace("western suburb in Derby", "western suburb of Derby")
    if "archipelago in France"  in meaning:
        meaning = meaning.replace("archipelago in France", "archipelago of France")
    if "city in Los Angeles County" in meaning:
        meaning = meaning.replace("city in Los Angeles County", "city of Los Angeles County")
    for word in tolow_first:
        if f". {word} " in meaning:
            meaning = meaning.replace(f". {word} ", f", {word.lower()} ")
        if f" {word} " in meaning:
            meaning = meaning.replace(f" {word} ", f" {word.lower()} ")
        if f": {word} " in meaning:
            meaning = meaning.replace(f": {word} ", f": {word.lower()} ")
    if "archipelago in United Kingdom" in meaning:
        meaning = meaning.replace("archipelago in United Kingdom", "archipelago of United Kingdom")
    if "city in Middlesex County" in meaning:
        meaning = meaning.replace("city in Middlesex County", "city of Middlesex County")
    if "autonomous territory in Pakistan" in meaning:
        meaning = meaning.replace("autonomous territory in Pakistan", "autonomous territory of Pakistan")
    if "dept in Bolivia" in meaning:
        meaning = meaning.replace("dept in Bolivia", "department in Bolivia")
    if 'former colony in' in meaning:
        meaning = meaning.replace('former colony in', 'former colony of')
    if '()' in meaning:
        meaning = meaning.replace('()', '')
    if ". supporting " in meaning:
        meaning = meaning.replace(". supporting ", ", supporting ")
    if " . " in meaning:
        meaning = meaning.replace(" . ", ", ")
    if "sea in Mediterranean Sea" in meaning:
        meaning = meaning.replace("sea in Mediterranean Sea", "a sea and arm of the Mediterranean Sea")
    if "city in Duval County" in meaning:
        meaning = meaning.replace("city in Duval County", "city of Duval County")
    if "a in California" in meaning:
        meaning = meaning.replace("a in California", "a city in California")
    if " In more detail" in meaning:
        meaning = meaning.replace(" In more detail", "")
    if "settlement in Saipan" in meaning:
        meaning = meaning.replace("settlement in Saipan", "settlement on Saipan")
    if "country in Balkan Peninsula" in meaning:
        meaning = meaning.replace("country in Balkan Peninsula", "country on the Balkan Peninsula")
    if "capital city in" in meaning:
        meaning = meaning.replace("capital city in", "capital city of")
    if "neighbourhood in Keene" in meaning:
        meaning = meaning.replace("neighbourhood in Keene", "neighbourhood of Keene")
    if "largest city in New York" in meaning:
        meaning = meaning.replace("largest city in New York", "largest city in the state of New York")
    

    return meaning
    
    # if "Spain|Spanish" in meaning:
    #     meaning = meaning.replace("Spain|Spanish", "Spanish")
    # if "occupation|occupied" in meaning:
    #     meaning = meaning.replace("occupation|occupied", "occupied")
    # if "goose|geese" in meaning:
    #     meaning = meaning.replace("goose|geese", "geese")
    # if "justify|justified" in meaning:
    #     meaning = meaning.replace("justify|justified", "justified")
    # if "Atlantic Ocean|Atlantic Coast" in meaning:
    #     meaning = meaning.replace("Atlantic Ocean|Atlantic Coast", "Atlantic Coast")
    

def filter_meaning(meaning):
    # make the mutliple spaces to one space
    replaced_string = re.sub(r'\s+', ' ', meaning)
    replaced_string = re.sub(r'\[\[([^]]*)\]\]', r'\1', replaced_string)
    replaced_string = re.sub(r'\{\{gloss\|([^}]*)\}\}', r'\1', replaced_string)
    replaced_string = re.sub(r'\{\{w\|([^}|]*)\|[^}]*\}\}', r'\1', replaced_string)
    replaced_string = re.sub(r'\{\{w\|([^}]*)\}\}', r'\1', replaced_string)

    # # delete the content in the brackets
    # replaced_string = remove_nested_parentheses_content(replaced_string)

    record_sentence = False
    record_word = False
    words = [word for word in re.split(r'\W+', replaced_string) if word]

    nottolow_first = ["Caribbean", "Oceania","France", "Australia", "Canada", "IndianaUSA", "Melanesia", "Atlantic", "India",\
                      "Malaysia", "Asio", "Grus", "Alaska", "Ethiopia", "Bolivia", "Keene", "North","England","Rotherham","Hartwith",\
                        "DonetskUkraine","Panama", "Israel", "PenangMalaysia", "Scotland", "ScotlandUK", "Germany", "Cambodia",\
                        "Dumfries", "Kentucky", "Indian","Mexico", "Pakistan", "Spain", "Haliaeetus","Europe","Kiritimati",\
                        "Guatemala", "Brunei", "Trinidad", "Crohn", "Gavia", "Ohm", "Africa", "Russia", "Solenopsis", "Spain",\
                        "Mauritius","Vulpes","Tanzania","Argentina","Chinese", "American", "Crimea", "Denver", "Seattle", "China",\
                        "Queensland","Capsicum", "Tursiops", "Aframomum", "ParisFrance", "VictoriaAustralia", "ThailandLaosMyanmar", \
                        "Egypt","Ecuador", "Greece","Tringa", "Loxia", "Chroicocephalus", "Loxia", "AlbertaCanada", "Budjak", "Territory",\
                        "DnipropetrovskUkraine", "Ichthyaetus", "Ardea", "Polygonia", "Varanus","Mathematics", "Anser", "Chlidonias", \
                        "Neophocaena", "Eriocheir", "Calendula", "Melia", "Compton", "Elaphurus", "Phylloscopus", "Taxus", "Buteo", \
                        "Hibiscus", "Elaeis", "Plegadis", "Lophophanes", "Phragmites", "Araucaria", "Combretum", "Motacilla", "Ceiba", \
                        "Terminalia", "Onychoprion", "Coturnix", "Nelumbo", "Leopardus", "Dryopteris", "Panax", "Dioscorea", "Malva", "Lumbar", \
                        "Melospiza", "Phoenicopterus", "Hirundo", "Quercus", "Bassia", "Periparus", "Rumex", "Pithecophaga", "Rhodostethia", \
                        "Melanitta", "Carassius", "Threskiornis", "Aythya", "Canis", "Otitis", "Gulosus", "Platanus", "Anthus"]
    if len(words) != 0:
        first_word = words[0]
        
        if first_word in tolow_first:
            # words[0] = first_word.lower()
            # a = replaced_string[0].lower()
            # b = replaced_string[1:]
            replaced_string = replaced_string[0].lower() + replaced_string[1:]
        elif len(first_word) == 1:
            pass
        elif replaced_string[0] == "'" or replaced_string[0] == "\'":
            pass
        elif replaced_string[0] == "\"":
            pass
        elif len(words) == 1 and first_word[0].isupper() and first_word[1].islower():
            if first_word not in nottolow_first:
                replaced_string = replaced_string[:1].lower()+replaced_string[1:]
                record_word = first_word
        elif first_word[0].isupper() and first_word[1].islower() and words[1][0].islower() and first_word not in nottolow_first:
            replaced_string = replaced_string[:1].lower()+replaced_string[1:]
            record_word  = first_word

        elif first_word[0].isupper():
            record_sentence = True
            



    replaced_string = replaced_string.strip()


    # deal with the error fixed matched phrase
    replaced_string = deal_error_fixed_phrase(replaced_string)

    # delete the pun

    replaced_string = replaced_string.strip()
    punctuations = [',', '.', '!', '?', ':', ';']
    while replaced_string[-1] in punctuations:
        if replaced_string[-5:] == " etc.":
            break
        replaced_string = replaced_string[:-1]
        replaced_string = replaced_string.strip()
    while replaced_string[0] in punctuations:
        replaced_string = replaced_string[1:]
        replaced_string = replaced_string.strip()
    replaced_string = replaced_string.strip()
    replaced_string = re.sub(r'\s+', ' ', replaced_string)

    return replaced_string



def read_jsonl(file_path: str):
    data = []
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            json_data = json.loads(line)
            data.append(json_data)
    return data

def write_jsonl(file_path: str, data: List[Any]):
    with open(file_path, 'w', encoding="utf-8") as file:
        for item in data:
            json_line = json.dumps(item, ensure_ascii=False)
            file.write(json_line + '\n')

def write_txt(file_path: str, data: List[Any]):
    with open(file_path, 'w', encoding="utf-8") as file:
        for item in data:
            file.write(item + '\n')

def clean_at_sy(phrases: List[str]):
    result = []
    for phrase in phrases:
        if "{{qualifier" in phrase:
            phrase = re.sub(r"\{\{qualifier\|.*\}\}", "", phrase)
        if "{{vern" in phrase:
            phrase = re.sub(r"\{\{vern\|(.*)\}\}", r"\1", phrase)
        if "{{l|en" in phrase:
            phrase = re.sub(r"\{\{l\|en\|(.*)\}\}", r"\1", phrase)
        if "{{!}} {{!}}" in phrase:
            phrase = phrase.replace("{{!}} {{!}}", "||")
        result.append(phrase.strip())
    return result
        
# main
def main( input_file, output_folder):
    output_file = output_folder + "/meaningdict_filtered.jsonl"
    term_lst = []
    record_sentences = []
    record_words = []
    data = read_jsonl(input_file)
    for term in data:
        filtered_meanitems = []
        for meanitem in term["meanitems"]:
            meaning = meanitem["meaning"]
            filtered_meaning = filter_meaning(meaning)
            if not judge_sentence_bracket_right(filtered_meaning):
                continue
            if filtered_meaning != "":
                meanitem["meaning"] = filtered_meaning
                filtered_meanitems.append(meanitem)
        term["meanitems"] = filtered_meanitems
        if len(term["alternative_forms"]) > 0:
            alternative_forms = term["alternative_forms"]
            cleaned_alternative_forms = clean_at_sy(alternative_forms)
            term["alternative_forms"] = cleaned_alternative_forms
        if len(term["synonyms"]) > 0:
            synonyms = term["synonyms"]
            cleaned_synonyms = clean_at_sy(synonyms)
            term["synonyms"] = cleaned_synonyms
        if len(filtered_meanitems) > 0:
            term_lst.append(term)
    record_words = list(set(record_words))
    # print(record_words)

    write_jsonl(output_file, term_lst)
    # write_txt(output_folder + "/capitalize_sentences.txt", record_sentences)
    # write_txt(output_folder + "/lowered_words.txt", record_words)





if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
    # print(filter_meaning("C5< sub>H11< sub>NO2< sub> of"))
