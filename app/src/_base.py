import kss
import re
import os
import stanza
from app.utils.lang_detect import detect_language

languages = ["en", "de", "it", "fr", "es"]

def is_model_downloaded(lang):
    model_path = os.path.expanduser(f"~/.stanza_resources/{lang}_default")
    return os.path.exists(model_path)

# 모델이 없으면 다운로드
for lang in languages:
    if not is_model_downloaded(lang):
        print(f"{lang} 모델 다운로드 중")
        stanza.download(lang)
    else:
        print(f"{lang} 모델이 이미 다운로드됨.")

# Stanza NLP 파이프라인 로드 (한 번만 실행)
stanza_models = {lang: stanza.Pipeline(lang=lang, processors="tokenize") for lang in languages}

class BaseNLPService:
    def split_sentences(self, text: str):
        lang_id = detect_language(text)

        if lang_id not in stanza_models and lang_id != "ko":
            raise ValueError(f"지원하지 않는 언어 코드입니다: {lang_id}")

        match lang_id:
            case "ko": #한국어
                return kss.split_sentences(text)
            case "en"| "fr" | "es" | "de" | "it":
                stanza_models = stanza_model[lang_id]
                docs = stanza_models(text)
                return [sentence.text for sentence in doc.sentences]


        
        
        
        
        
        #match case로 변경하기, finally 영어
        # if lang_id == "ko":
        #     return kss.split_sentences(text)
        # elif lang_id == "en": #영어
        #     return stanza.split_sentences(text)
        # elif lang_id == "fr": #프랑스어
        #     return stanza.split_sentences(text)
        # elif lang_id == "es": #스페인어
        #     return stanza.split_sentences(text)
        # elif lang_id == "de": #독일어
        #     return stanza.split_sentences(text)
        # elif lang_id == "it": #이태리어
        #     return stanza.split_sentences(text)
      

    # def clean_json_string(json_bytes):
    #     json_string = json_bytes.decode("utf-8")
    #     return re.sub(r'[\x00-\x1F\x7F]', '', json_string)

# class BaseNLPService:
#     def split_sentences(self, text: str):
#         return kss.split_sentences(text)



