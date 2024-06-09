import time
from pathlib import Path
import sys
from typing import Any, List, Optional
f = Path(__file__)
sys.path.append(str(f.parent))

import csv
import json
from tqdm import tqdm
import re
import dealmeaningtext
import sys
import logging
import zhconv
import parse_wikitext as pw
import wikitextparser
from wikitextparser import remove_markup, parse, Template
import codecs
import argparse



# list of part of speech
part_of_speech =  [
    "Adjective",
    "Adverb",
    "Ambiposition",
    "Article",
    "Circumposition",
    "Classifier",
    "Conjunction",
    "Contraction",
    "Counter",
    "Determiner",
    "Ideophone",
    "Interjection",
    "Noun",
    "Numeral",
    "Participle",
    "Particle",
    "Postposition",
    "Preposition",
    "Pronoun",
    "Proper noun",
    "Verb"
]


def getTranslation(text):
# get the mandarin translation
    result = []
    pattern = r"Mandarin:([^*]+)\n\*"
    matchs = re.findall(pattern, text)
    for i in range(len(matchs)):
        for template in wikitextparser.parse(matchs[i]).templates:
            if len(template.arguments) > 1 :
                result.append(template.arguments[1].value)
    # Convert traditional characters to simplified characters
    result = [ zhconv.convert(word.replace("[",'').replace("]",''), 'zh-cn') for word in result]
    result = list(set(result))
    return result

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

def write_jsonl(file_path: str, data: List[Any]):
    with open(file_path, 'w', encoding="utf-8") as file:
        for item in data:
            json_line = json.dumps(item,ensure_ascii=False)
            file.write(json_line + '\n')

def write_txt(file_path: str, data: List[str]):
        # write the iate_phrase_terms to file
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(item+'\n')

def clean_slash_take_second(text: str) -> str:
    if '/' in text:
        return text.split('/')[1]
    else:
        return text

def clean_pipe_take_second(text: str) -> str:
    if '|' in text:
        return text.split('|')[1]
    else:
        return text

def clean_text(text: str) -> str:
    cleaned_text = re.sub(r'<<([^>]*)>>', lambda x: clean_slash_take_second(x.group(1)), text)
    cleaned_text = re.sub(r'\[\[([^]]*)\]\]', lambda x: clean_pipe_take_second(x.group(1)), cleaned_text)
    cleaned_text = re.sub(r'<ref>(.*?)</ref>', '', cleaned_text)
    cleaned_text = re.sub(r'<!--(.*?)-->', '', cleaned_text)
    cleaned_text = re.sub(r'<ref[^>]*>(.*?)</ref>', '', cleaned_text)
    return cleaned_text.strip()

def get_content_in_ref(text: str) -> str:
    content_lst = re.findall(r'<ref>(.*?)</ref>', text)
    content_lst.extend(re.findall(r'<ref[^>]*>(.*?)</ref>', text))
    content_lst = list(set(content_lst))
    return content_lst

def filter_emptyitem_in_list(lst: List[str]) -> List[str]:
    return [item for item in lst if item.strip() != ""]

def clean_text_lst(text_lst: List[str]) -> List[str]:
    return [clean_text(text) for text in text_lst]

def should_replace(template: Template) -> Optional[str]:
    if template.name == 'place' and len(template.arguments) > 1:
        place_type = clean_text(template.arguments[1].value)
        if '/' in place_type and len(place_type.split())<5:
            place_type = place_type.split('/')[0]
        area = []
        if len(template.arguments) > 2:
            for arg in template.arguments[2:]:
                arg_clean = clean_text(arg.value)
                if '/' in arg_clean and len(arg_clean.split())<5:
                    area.append( arg_clean.split('/')[1])
        if len(area) == 0:
            result = place_type
        if len(area) == 1:
            result = place_type + " in " + area[0]
        if len(area) > 1:
            result = place_type + " in " + area[0]
            # for area_item in area[1:]:
            #     result += ", " + area_item
        return result

    elif template.name == '1' and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'l' and len(template.arguments) > 1:
        return template.arguments[1].value
    elif template.name == 'n-g' and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'm' and len(template.arguments) > 1:
        return template.arguments[1].value
    elif 'taxlink' in template.name and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'taxfmt' and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'vern' and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'w' and len(template.arguments) > 1:
        if template.arguments[0].value == 'en':
            return template.arguments[1].value
    elif template.name == 'w' and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'cap' and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'chemf' and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'math' and len(template.arguments) > 0:
        return template.arguments[0].value
    elif template.name == 'll' and len(template.arguments) > 1:
        return template.arguments[1].value
    elif template.name == 'former name of' and len(template.arguments) > 1:
        return 'former name of ' + template.arguments[1].value
    elif template.name == 'clipping of' and len(template.arguments) > 1:
        return 'clipping of ' + template.arguments[1].value
    elif template.name == 'synonym of' and len(template.arguments) > 1:
        return 'synonym of ' + template.arguments[1].value
    elif template.name == 'short for' and len(template.arguments) > 1:
        return 'short for ' + template.arguments[1].value
    elif template.name == 'alternative form of' and len(template.arguments) > 1:
        return 'alternative form of ' + template.arguments[1].value
    elif template.name == 'ellipsis of' and len(template.arguments) > 1:
        return 'ellipsis of ' + template.arguments[1].value
    
    elif template.name == '&lit':
        result = None
        if len(template.arguments) > 1:
            contents = [arg.value for arg in template.arguments[1:]]
            result = ", ".join(contents)
            result = "see: "+result
        return result

    else:
        return None
    

def etract_syn_alter(template):
    result = []
    for argu in template.arguments[1:]:
        if "=" in argu.string:
            continue
        cleaned_value = clean_text(argu.value)
        if cleaned_value == "":
            break
        elif cleaned_value[0:10] == 'Thesaurus:':
            result.append(cleaned_value[10:])
        elif "=" in cleaned_value:
            continue
        else:
            result.append(cleaned_value)
    return result

def etract_sections(english_sections, term) -> List[str]:

    meaning_items = []
    alternative_forms_all  = []
    synonyms_all = []
    translations = []
    pos_set = set()
    if term in ['portmanteau word']:
        print(1)
    for sec in english_sections:
        if sec.title is None:
            continue
        # extract the meaning set
        if sec.title in part_of_speech:
            # extract the alternative forms, synonyms in meaning section
            alternative_forms = []
            synonyms = []
            for template in sec.templates:
                if template.name == "alternative form of" and len(template.arguments) > 1:
                    alternative_forms.append(template.arguments[1].value)
                elif template.name == "synonym of" and len(template.arguments) > 1:
                    synonyms.append(template.arguments[1].value)
                elif template.name == "syn" and len(template.arguments) > 1:
                    syn_extract = etract_syn_alter(template)
                    synonyms.extend(syn_extract)
                elif template.name == "synonyms" and len(template.arguments) > 1:
                    syn_extract = etract_syn_alter(template)
                    synonyms.extend(syn_extract)
                elif template.name == "alter" and len(template.arguments) > 1:
                    alt_extract = etract_syn_alter(template)
                    alternative_forms.extend(alt_extract)
                elif template.name == "alt" and len(template.arguments) > 1:
                    alt_extract = etract_syn_alter(template)
                    alternative_forms.extend(alt_extract)
            alternative_forms_all.extend(alternative_forms)
            synonyms_all.extend(synonyms)


            
            sections = sec.get_sections(include_subsections=False)
            clean_sections = []
            for section in sections:
                if section.plain_text(replace_templates = should_replace).strip() == "":
                    continue
                clean_sections.append(section)

            if len(clean_sections) == 0:
                continue
            meaning_section: wikitextparser.Section = clean_sections[0]
            meanings_list = meaning_section.get_lists(pattern = (r'\#', r'\*', '[:;]'))

            # clean meaning set
            clean_meanings_set = set()
            for l in meanings_list:
                # delete the reference in the meaning
                plain_text_with_tag = l.plain_text(replace_templates = should_replace, replace_tags=False)
                if "</ref>" in plain_text_with_tag:
                    content_in_ref_list = get_content_in_ref(plain_text_with_tag)
                    pt = l.plain_text(replace_templates = should_replace)
                    for content in content_in_ref_list:
                        if content in pt:
                            pt = pt.replace(content, '')
                else:
                    pt = l.plain_text(replace_templates = should_replace)

                lines = pt.splitlines(keepends=False)
                for line in lines:
                    if line.startswith("# "):
                        line = line[len("# "):]
                        clean_meaning = clean_text(line.strip())
                        if clean_meaning != "":
                            clean_meanings_set.add(clean_meaning)
                
            

            for meaning in clean_meanings_set:
                # if meaning don't contain any english character or only one character, skip it
                if not re.search(r'[a-zA-Z]', meaning) or len(meaning) == 1:
                    continue
                meaning_items.append({"pos": sec.title, "meaning": meaning})
                pos_set.add(sec.title)
        # extract the alternative forms, synonyms, translations
        if sec.title == "Alternative forms":
            alternative_templates = sec.templates
            alternative_forms = []
            for alternative_template in alternative_templates:
                if alternative_template.name == "alter" and len(alternative_template.arguments) > 1:
                    for argu in alternative_template.arguments[1:]:
                        if argu.value == "":
                            break
                        else:
                            alternative_forms.append(argu.value)
                elif alternative_template.name == "l" and len(alternative_template.arguments) > 1:
                    alternative_forms.append(alternative_template.arguments[1].value)
                elif alternative_template.name == "alt" and len(alternative_template.arguments) > 1:
                    for argu in alternative_template.arguments[1:]:
                        if argu.value == "":
                            break
                        else:
                            alternative_forms.append(argu.value)
            
            alternative_forms_all.extend(alternative_forms)
                
        if sec.title == "Synonyms":
            syn_templates = sec.templates
            synonyms = []
            for syn_template in syn_templates:
                if syn_template.name == "syn" and len(syn_template.arguments) > 1:
                    for argu in syn_template.arguments[1:]:
                        if argu.value == "":
                            break
                        else:
                            synonyms.append(argu.value)
                elif syn_template.name == "l" and len(syn_template.arguments) > 1:
                    synonyms.append(syn_template.arguments[1].value)
                elif syn_template.name == "synonyms" and len(syn_template.arguments) > 1:
                    for argu in syn_template.arguments[1:]:
                        if argu.value == "":
                            break
                        else:
                            synonyms.append(argu.value)
            synonyms_all.extend(synonyms)
        if sec.title == "See also":
            syn_templates = sec.templates
            synonyms = []
            for syn_template in syn_templates:
                if syn_template.name == "l" and len(syn_template.arguments) > 1:
                    synonyms.append(syn_template.arguments[1].value)
            synonyms_all.extend(synonyms)
        if sec.title == "Translations":
            # get chinese translation
            sec_content = sec.contents
            translation_lst = getTranslation(sec_content)
            translations.extend(translation_lst)
    alternative_forms_all = clean_text_lst(alternative_forms_all)
    alternative_forms_all = list(set(alternative_forms_all))

    alternative_forms_all = filter_emptyitem_in_list(alternative_forms_all)
    synonyms_all = clean_text_lst(synonyms_all)
    synonyms_all = list(set(synonyms_all))
    synonyms_all = filter_emptyitem_in_list(synonyms_all)
    translations = list(set(translations))
    translations = filter_emptyitem_in_list(translations)

            
    return meaning_items, alternative_forms_all, synonyms_all, translations, pos_set

    
# main
def main(data_path, result_content, iate_terms_path):


    json_file = data_path+"/enwiktionary.jsonl"
    output_file = result_content + '/meaningdict.jsonl'
    iate_terms = []

    # set the log file
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.INFO)
    handler = logging.FileHandler(result_content+'/log.txt')
    handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    # read the iate term file
    term_to_iate = {}
    with open(iate_terms_path, 'r', encoding='utf-8') as file:
        for line in file:
            item = json.loads(line)
            term_to_iate[item['term']] = item['domain']
            iate_terms.append(item['term'])
    iate_terms_set = set(iate_terms)


    filter_domains = ["Domain code not specified"]


    phrase_term_lst = []
    meaning_entries = []
    # read jsonl file
    wikidata = read_jsonl(json_file)

    # read and process each line of the input file
    for item in tqdm(wikidata):

        term = item['title']
        text = item['text']
        # only deal with phrase term
        if len(term.strip().split()) <= 1:
            continue

        # only deal with term in iate term list
        if term in iate_terms_set:
            domain = term_to_iate[term]
        elif term.lower() in iate_terms_set:
            domain = term_to_iate[term.lower()]
        else:
            continue
        
        # filter the domain and phrase
        if domain in filter_domains:
            continue

        # if term in ["death rate"]:
        #     print(1)
        
        data = wikitextparser.parse(text)
        english_sections = None
        for section in data.sections:
            if section.title == "English":
                english_sections = section.sections
                break
        if english_sections is None:
            continue
            

        meaningitems, alternative_forms, synonyms, translations, pos_set = etract_sections(english_sections, term)
        if len(meaningitems) == 0:
            continue
        # only deal with term with mandarin translations
        if len(translations) == 0:
            continue
        # only deal with term with Noun, Proper noun, Pronoun
        if "Noun" not in pos_set and "Proper noun" not in pos_set and "Pronoun" not in pos_set:
            continue

        entry = {'term': term,'domain': domain, 'meanitems': meaningitems, 'alternative_forms': alternative_forms, 'synonyms': synonyms, 'translations': translations}
        # entry = {'term': term, 'meanitems': meaningitems, 'alternative_forms': alternative_forms, 'synonyms': synonyms, 'translations': translations}

        meaning_entries.append(entry)            
        phrase_term_lst.append(term)
        

    # write the meaning_entries to file
    write_jsonl(output_file, meaning_entries)

    # write the iate_phrase_terms to file
    write_txt(result_content+'/phrase_term_final.txt', phrase_term_lst)

if __name__ == "__main__":
    # parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, required=True)
    parser.add_argument("--result_content", type=str, required=True)
    parser.add_argument("--iate_terms_path", type=str, required=True)
    args = parser.parse_args()
    data_path = args.data_path
    result_content = args.result_content
    iate_terms_path = args.iate_terms_path
    main(data_path, result_content, iate_terms_path)