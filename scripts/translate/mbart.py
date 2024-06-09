import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from transformers import AutoModelForCausalLM, AutoTokenizer
import zhconv

device = "cuda:0"
MBART_MODEL_HF = None
MBART_TOKENIZER = None
model_path = "../models/mbart-large"

def translate_mbart(text: str, source: str, target: str):
    global MBART_MODEL_HF, MBART_TOKENIZER
    if MBART_MODEL_HF is None:
        MBART_MODEL_HF = MBartForConditionalGeneration.from_pretrained(model_path).to(device)
        MBART_TOKENIZER = MBart50TokenizerFast.from_pretrained(model_path)
    if source == "zh" or source == "zhs" or source == "zht":
        source_id = "zh_CN"
    elif source == "en":
        source_id = "en_XX"
    elif source == "ja":
        source_id = "ja_XX"
    else:
        print(source, target)
        raise Exception("Unsupported translation type")

    if target == "zh" or target == "zhs" or target == "zht":
        target_id = "zh_CN"
    elif target == "en":
        target_id = "en_XX"
    elif target == "ja":
        target_id = "ja_XX"
    else:
        print(source, target)
        raise Exception("Unsupported translation type")
    
    if source in ["zht"]:
        text = zhconv.convert(text, 'zh-cn')
    
    if source_id == target_id:
        if source == target:
            return text
        else:
            if target in ["zht"]:
                text = zhconv.convert(text, 'zh-tw')
            return text

    MBART_TOKENIZER.src_lang = source_id
    encoded_hi = MBART_TOKENIZER(text, return_tensors="pt", max_length=512, truncation=True).to(device)
    generated_tokens = MBART_MODEL_HF.generate(
        **encoded_hi,
        forced_bos_token_id=MBART_TOKENIZER.lang_code_to_id[target_id]
    )
    output = MBART_TOKENIZER.batch_decode(generated_tokens, skip_special_tokens=True)

    if target in ["zht"]:
        out = zhconv.convert(output[0], 'zh-tw')
    else:
        out = output[0]
    return out



# test en-zh
# print(translate_mbart("The English - Chinese parallel corpus in the domain of twitter of Tencent or Sina twitter from 2010 to March 2014 .", "en", "zh"))