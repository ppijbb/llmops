

def text_preprocess(text: str) -> str:
    return text.strip()
    # return f"[대화]\n{text}\n---\n[요약]\n" if "[대화]" not in text and "[요약]" not in text else text

def text_postprocess(text:str) -> str:
    # if not text.endswith("\n---"):
    #     text = "* " + "* ".join(text.split("* ")[:-1])
    #     if text.endswith("\n---"):
    #         "---"
    # text = text.replace("```json", "").replace("```", "")
    # return text.replace("* ", "").replace("---", "").strip()
    return (text.replace("```json", "")
                .replace("```", "")
                .replace("\ntrasncripted result:\n", "")
                .replace("*\n","")
                .replace("\n", " ").strip())
