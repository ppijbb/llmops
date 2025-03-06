import kss
import re
import os
import stanza
from app.utils.lang_detect import detect_language

languages = ["en", "de", "it", "fr", "es"]

def is_model_downloaded(lang):
    return os.path.exists(os.path.expanduser(f"~/stanza_resources/{lang}/"))

class BaseNLPService:
    # Stanza NLP 파이프라인 로드 (한 번만 실행)
    stanza_models: dict = {lang: stanza.Pipeline(lang=lang, processors="tokenize") for lang in languages}    
    # 모델이 없으면 다운로드
    for lang in languages:
        if not is_model_downloaded(lang):
            print(f"stanza {lang} model downloading...")
            stanza.download(lang)
        else:
            print(f"stanza {lang} model already downloaded.")
    
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