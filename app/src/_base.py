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


class BaseNLPService:
    # Stanza NLP 파이프라인 로드 (한 번만 실행)
    stanza_models: dict = {lang: stanza.Pipeline(lang=lang, processors="tokenize") for lang in languages}    
    
    def split_sentences(self, text: str):
        lang_id = detect_language(text)

        if lang_id not in self.stanza_models and lang_id != "ko":
            raise ValueError(f"지원하지 않는 언어 코드입니다: {lang_id}")

        match lang_id:
            case "ko": #한국어
                return kss.split_sentences(text)
            case "en"| "fr" | "es" | "de" | "it":
                stanza_models = self.stanza_models[lang_id]
                docs = stanza_models(text)
                return [sentence.text for sentence in docs.sentences]