import openai
from typing import List
from joblib import Parallel, delayed

openai.api_key = ""

def trans_prompt(text: str, src: str, tgt: str) -> str:
    return f"Translate the following sentence from {src} to {tgt}:\n{text}"

def translate_text_with_gpt(text: str, src: str, tgt: str) -> str:
    prompt = trans_prompt(text, src, tgt)
    
    chat_completion = openai.ChatCompletion.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo-0125",
        temperature=0,
    )
    # print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

def translate_text_with_gpt_batch(texts: List[str], src: str, tgt: str) -> List[str]:
    ret = Parallel(n_jobs=16, backend="threading")(delayed(translate_text_with_gpt)(t, src=src, tgt=tgt) for t in texts)
    return ret