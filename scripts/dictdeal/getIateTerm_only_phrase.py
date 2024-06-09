import csv
import sys
from tqdm import tqdm
import re
import json


def getterm(input_file):

    phrase_term_lst = []
    domain_set = set()

    for line in tqdm(csv.reader(open(input_file, 'r', encoding='utf-8'), delimiter='\t')):
        strlst = line[0].split('|')
        domain = strlst[1]
        domain_split = domain.split(';')
        domain_set.update(domain_split)
        term = strlst[3]
        term = term.strip()
        # only add phrase terms
        if len(term.split()) <= 1:
            continue

        phrase_term_lst.append({'term': term, 'domain': domain})

    domain_lst = list(domain_set)
    return  phrase_term_lst, domain_lst


# method to write list to file
def write_list_to_file(lst, output_path):
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for item in lst:
            json.dump(item, output_file, ensure_ascii=False)
            output_file.write('\n')



# main
if __name__ == '__main__':
    input_file = sys.argv[1]
    output_path = sys.argv[2]

    phrase_term_output_file = output_path + "/iate_phrase_term.txt"
    domain_output_file = output_path + "/iate_domain.txt"

    phrase_term_lst, domain_lst = getterm(input_file)

    write_list_to_file(phrase_term_lst, phrase_term_output_file)
    write_list_to_file(domain_lst, domain_output_file)

