
from typing import List
import requests
import uuid
from tenacity import retry
from joblib import Parallel, delayed

import os
import json

BING_SUBSCRIPTION_KEY = ""

def translate_text_with_bing(text: str) -> str:
    '''
    Copied from: https://github.com/MicrosoftTranslator/Text-Translation-Code-Samples
    '''

    # Add your subscription key and endpoint
    subscription_key = BING_SUBSCRIPTION_KEY
    endpoint = "https://api.cognitive.microsofttranslator.com"

    if subscription_key == "YOUR_BING_TRANSLATION_KEY":
        raise Exception("Please replace the variable BING_SUBSCRIPTION_KEY as your KEY.")
    
    # Add your location, also known as region. The default is global.
    # This is required if using a Cognitive Services resource.
    location = "eastasia"
    path = '/translate'
    constructed_url = endpoint + path
    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': 'zh'
    }
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{'text': text}]
    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    return response[0]['translations'][0]['text']

def translate_text_with_bing_batch(text: List[str]) -> List[str]:
    ret = Parallel(n_jobs=16, backend="threading")(delayed(translate_text_with_bing)(t) for t in text)
    return ret

# print(translate_text_with_bing("Hi"))