import re

def processExplanation(text):
    pieces = text.split("\\n")
    text = pieces[0]
    pattern = r"\{\{initialism of\|en\|(.*?)\}\}"
    initialisms = re.findall(pattern,text )
    if len(initialisms) != 0:
        for initialism in initialisms:
            splitlst=""
            for splititem in initialism.split("|"):
                if "{{" in splititem:
                    continue
                else:
                    splitlst = splititem
                    break
            if splitlst == "":
                splitlst = initialism.split("|")[0]
                splitlst.replace("{{", "")
                splitlst.replace("}}", "")
            text = text.replace("{{initialism of|en|"+initialism+"}}", splitlst)

    # delete the text like {{lb|en|...}}
    text = re.sub(r'\{\{lb\|en\|[^}]+\}\}', '', text)
    
    text = text.replace("[[", "").replace("]]", "")
    text = text.replace("{{", "").replace("}}", "")
    
    # 去除<ref name=SOED/>与</ref>、<ref>标签
    text = text.replace("<ref name=SOED/>", "").replace("</ref>", "").replace("<ref>", "")
    return text



def getSynonyms(syntext):
    pattern = r"\{\{syn\|en\|([^{^}]+)\}\}"
    matches = re.findall(pattern, syntext)
    result = []
    for match in matches:
        words = match.split("|")
        for word in words:
            if ":" not in word and "=" not in word:
                result.append(word.strip())
    return result


def dealmeaningItem(text):
    result=[]
    pattern = r"n#+\s"
    matches = re.split(pattern, text)
    # skip the first meaningless item
    for i in range(1,len(matches)):
        meaning = matches[i]

        tempdict = dict()
        tempdict['meaning'] = processExplanation(meaning)
        if tempdict['meaning'].strip() == "" or len(tempdict['meaning'].strip()) == 1:
            continue
        tempdict['synonyms'] = getSynonyms(meaning)
        result.append(tempdict)
    return result
    



