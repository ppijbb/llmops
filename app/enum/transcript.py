from enum import Enum

class TargetLanguages(Enum):
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    DUTCH = "nl"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    CHINESE = "zh"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    TURKISH = "tr"
    POLISH = "pl"
    SWEDISH = "sv"
    DANISH = "da"
    NORWEGIAN = "no"
    FINNISH = "fi"
    CZECH = "cs"
    SLOVAK = "sk"
    GREEK = "el"
    HUNGARIAN = "hu"
    ROMANIAN = "ro"
    UKRAINIAN = "uk"
    BULGARIAN = "bg"
    CROATIAN = "hr"
    SERBIAN = "sr"
    SLOVENIAN = "sl"
    ESTONIAN = "et"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    VIETNAMESE = "vi"
    THAI = "th"
    INDONESIAN = "id"
    MALAY = "ms"
    FILIPINO = "fil"

    @classmethod
    def get_language_name(cls, code):
        language_names = {
            "en": "English",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "nl": "Dutch",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "zh": "Chinese",
            "ko": "Korean",
            "ar": "Arabic",
            "hi": "Hindi",
            "tr": "Turkish",
            "pl": "Polish",
            "sv": "Swedish",
            "da": "Danish",
            "no": "Norwegian",
            "fi": "Finnish",
            "cs": "Czech",
            "sk": "Slovak",
            "el": "Greek",
            "hu": "Hungarian",
            "ro": "Romanian",
            "uk": "Ukrainian",
            "bg": "Bulgarian",
            "hr": "Croatian",
            "sr": "Serbian",
            "sl": "Slovenian",
            "et": "Estonian",
            "lv": "Latvian",
            "lt": "Lithuanian",
            "vi": "Vietnamese",
            "th": "Thai",
            "id": "Indonesian",
            "ms": "Malay",
            "fil": "Filipino"
        }
        return language_names.get(code, "Unknown")
