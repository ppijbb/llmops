import os

from app.src.const import prompt
from app.enum.transcript import TargetLanguages
from app.enum.domain import SummaryDomain

def select_summary_domain(
    prompt_type: str, 
    language: str
) -> str:
    if prompt_type == SummaryDomain.DENTAL:    
        match language:
            case TargetLanguages.KOREAN:
                return prompt.DEFAULT_SUMMARY_SYSTEM_PROMPT
            case TargetLanguages.ENGLISH:
                return prompt.DEFAULT_SUMMARY_SYSTEM_PROMPT_EN
            case _:
                return prompt.DEFAULT_SUMMARY_SYSTEM_PROMPT_EN
    elif prompt_type == SummaryDomain.MENTAL:
        match language:
            case TargetLanguages.KOREAN:
                return prompt.DEFAULT_SUMMARY_BEAUTY_PROMPT.format(os.getenv("SYSTEM_NAME"))
            case TargetLanguages.ENGLISH:
                return prompt.DEFAULT_SUMMARY_BEAUTY_PROMPT_EN.format(os.getenv("SYSTEM_NAME"))
            case _:
                return prompt.DEFAULT_SUMMARY_BEAUTY_PROMPT.format(os.getenv("SYSTEM_NAME"))
    elif prompt_type == SummaryDomain.BEAUTY:
        match language:
            case TargetLanguages.KOREAN:
                return prompt.DEFAULT_SUMMARY_BEAUTY_PROMPT.format(os.getenv("SYSTEM_NAME"))
            case TargetLanguages.ENGLISH:
                return prompt.DEFAULT_SUMMARY_BEAUTY_PROMPT_EN.format(os.getenv("SYSTEM_NAME"))
            case _:
                return prompt.DEFAULT_SUMMARY_BEAUTY_PROMPT.format(os.getenv("SYSTEM_NAME"))
    elif prompt_type == SummaryDomain.TEST:
        return None
    else:
        return prompt.DEFAULT_SUMMARY_SYSTEM_PROMPT_EN