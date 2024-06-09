import re

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