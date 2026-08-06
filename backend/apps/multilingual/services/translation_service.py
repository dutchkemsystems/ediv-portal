import json
import os
from pathlib import Path


class TranslationService:
    _cache = {}
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'yo': 'Yoruba',
        'pcm': 'Nigerian Pidgin',
        'fr': 'French',
    }

    @classmethod
    def _load_translations(cls, lang_code):
        if lang_code in cls._cache:
            return cls._cache[lang_code]
        translations_dir = Path(__file__).parent.parent / 'translations'
        file_path = translations_dir / f'{lang_code}.json'
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                cls._cache[lang_code] = json.load(f)
        else:
            cls._cache[lang_code] = {}
        return cls._cache[lang_code]

    @classmethod
    def translate(cls, key, lang_code='en', **kwargs):
        if lang_code == 'en':
            return kwargs.get('default', key)
        translations = cls._load_translations(lang_code)
        text = translations.get(key, key)
        if kwargs:
            for k, v in kwargs.items():
                text = text.replace(f'{{{k}}}', str(v))
        return text

    @classmethod
    def translate_batch(cls, keys, lang_code='en'):
        translations = cls._load_translations(lang_code)
        return {key: translations.get(key, key) for key in keys}

    @classmethod
    def get_all_keys(cls):
        base_keys = set()
        translations_dir = Path(__file__).parent.parent / 'translations'
        for file_path in translations_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                base_keys.update(data.keys())
        return sorted(base_keys)

    @classmethod
    def get_supported_languages(cls):
        return cls.SUPPORTED_LANGUAGES

    @classmethod
    def detect_language(cls, text):
        yoruba_markers = ['ẹ', 'ọ', 'ṣ', 'ń', 'à', 'è', 'ì', 'ò', 'ù']
        if any(c in text.lower() for c in yoruba_markers):
            return 'yo'
        pidgin_markers = ['dem', 'dey', 'na', 'wetin', 'abi', 'o', 'oh']
        if any(word in text.lower().split() for word in pidgin_markers):
            return 'pcm'
        french_markers = ['le', 'la', 'les', 'de', 'du', 'des', 'un', 'une']
        words = text.lower().split()
        if sum(1 for w in words if w in french_markers) >= 2:
            return 'fr'
        return 'en'
