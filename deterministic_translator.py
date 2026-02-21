# deterministic_translator.py
"""
Rule-based Paj Ajap <-> English translator.
Handles dictionary lookups, compounds, morphology, numbers, and grammar.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any

from dictionary import PajAjapDictionary
from pa_numbers import PajAjapNumbers


@dataclass
class TranslationResult:
    translated: str
    explanation: str
    confidence: float
    unknown_words: list[str]
    direction: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "translated": self.translated,
            "explanation": self.explanation,
            "confidence": self.confidence,
            "unknown_words": self.unknown_words,
            "direction": self.direction,
        }


class DeterministicTranslator:
    PA_SPECIAL = set("þфßç")

    SKIP_WORDS = frozenset({
        "a", "an", "the", "to", "of", "am", "be", "been", "being",
        "was", "were", "does", "very", "really", "just", "also",
        "at", "on", "for", "with", "from", "but", "or",
        "if", "when", "where", "while", "than", "about", "up",
        "down", "out", "into", "can", "could", "would", "should",
        "may", "might", "must", "shall",
    })

    CONTRACTIONS = {
        "i'm": "i am", "i'll": "i will", "i've": "i have", "i'd": "i did",
        "you're": "you are", "you'll": "you will", "you've": "you have",
        "we're": "we are", "we'll": "we will", "they're": "they are",
        "they'll": "they will", "it's": "it is", "that's": "that is",
        "there's": "there is", "don't": "do not", "doesn't": "does not",
        "didn't": "did not", "isn't": "is not", "aren't": "are not",
        "wasn't": "was not", "weren't": "were not", "won't": "will not",
        "can't": "can not", "couldn't": "could not", "shouldn't": "should not",
        "wouldn't": "would not", "haven't": "have not", "hasn't": "has not",
        "wanna": "want", "gonna": "will", "gotta": "need",
        "im": "i am", "dont": "do not", "doesnt": "does not",
        "didnt": "did not", "isnt": "is not", "arent": "are not",
        "cant": "can not", "wont": "will not",
    }

    def __init__(self):
        self.dict = PajAjapDictionary()
        self.nums = PajAjapNumbers()

    def translate(self, text: str) -> TranslationResult:
        lang = self.detect_language(text)
        if lang == "paj_ajap":
            return self._pa_to_eng(text)
        return self._eng_to_pa(text)

    def detect_language(self, text: str) -> str:
        if any(c in text for c in self.PA_SPECIAL):
            return "paj_ajap"
        words = text.lower().split()
        if not words:
            return "english"
        pa_hits = sum(1 for w in words if self.dict.lookup_pa(w) is not None)
        if pa_hits / len(words) > 0.5:
            return "paj_ajap"
        return "english"
    
    #  ENGLISH TO PAJ-AJAP
    def _eng_to_pa(self, text: str) -> TranslationResult:
        normalized = self._normalize(text.lower().strip())

        # Full-phrase compound
        comp = self.dict.get_compound_eng(normalized)
        if comp:
            return TranslationResult(comp, f"Compound: '{normalized}' → '{comp}'",
                                     1.0, [], "eng_to_pa")

        # Number
        try:
            num = int(normalized)
            pa = self.nums.to_paj_ajap(num)
            if pa:
                return TranslationResult(pa, f"Number: {num} → '{pa}'",
                                         1.0, [], "eng_to_pa")
        except ValueError:
            pass

        words = normalized.split()
        parts, explanations, unknowns = [], [], []
        total, matched = 0, 0

        i = 0
        while i < len(words):
            # Multi-word compound (longest match, up to 5 words)
            found = False
            for length in range(min(5, len(words) - i), 1, -1):
                phrase = " ".join(words[i:i + length])
                comp = self.dict.get_compound_eng(phrase)
                if comp:
                    parts.append(comp)
                    explanations.append(f"'{phrase}' → '{comp}'")
                    matched += length
                    total += length
                    i += length
                    found = True
                    break
            if found:
                continue

            word = words[i]
            total += 1
            i += 1

            if word in self.SKIP_WORDS:
                explanations.append(f"'{word}' (skipped)")
                total -= 1
                continue

            # Morphological analysis
            is_plural, singular = self._detect_plural(word)
            is_ing, stem_ing = self._detect_ing(word)
            is_ed, stem_ed = self._detect_ed(word)
            is_ly, stem_ly = self._detect_ly(word)
            is_er, stem_er = self._detect_er(word)

            # Try lookups in order of specificity
            result = self.dict.lookup_eng(word)
            used_form = word

            if not result and is_plural:
                result = self.dict.lookup_eng(singular)
                used_form = singular

            if not result and is_ing:
                result = self.dict.lookup_eng(stem_ing)
                used_form = stem_ing

            if not result and is_ed:
                result = self.dict.lookup_eng(stem_ed)
                used_form = stem_ed

            if not result and is_ly:
                result = self.dict.lookup_eng(stem_ly)
                used_form = stem_ly

            if not result and is_er:
                result = self.dict.lookup_eng(stem_er)
                used_form = stem_er

            if result:
                entry = result[0]
                pa = entry.pa_word

                # Apply Paj Ajap morphology
                if is_plural and "noun" in entry.pos and " " not in pa:
                    pa = f"{pa}wa"
                elif is_plural and " " in pa:
                    pa = f"{pa} wa"

                if is_ing and word != used_form:
                    pa = f"{pa} þi"

                if is_ed and word != used_form:
                    pa = f"jo {pa}"

                if is_er and word != used_form and "noun" not in entry.pos:
                    pa = f"{pa} ej"

                parts.append(pa)
                explanations.append(f"'{word}' → '{pa}'")
                matched += 1
            else:
                unknowns.append(word)
                parts.append(f"[{word}]")
                explanations.append(f"'{word}' → UNKNOWN")

        confidence = matched / max(total, 1)

        return TranslationResult(
            " ".join(parts), "; ".join(explanations),
            confidence, unknowns, "eng_to_pa",
        )
    
    #  PAJ-AJAP TO ENGLISH
    def _pa_to_eng(self, text: str) -> TranslationResult:
        text = text.strip()

        # Number expression
        if self.nums.is_number_text(text):
            val = self.nums.from_paj_ajap(text)
            if val is not None:
                return TranslationResult(str(val), f"Number: '{text}' → {val}",
                                         1.0, [], "pa_to_eng")

        # Full compound
        comp = self.dict.get_compound_pa(text)
        if comp:
            return TranslationResult(comp, f"Compound: '{text}' → '{comp}'",
                                     1.0, [], "pa_to_eng")

        words = text.split()
        parts, explanations, unknowns = [], [], []
        total, matched = 0, 0

        i = 0
        while i < len(words):
            # Multi-word compound (longest first, up to 6)
            found = False
            for length in range(min(6, len(words) - i), 1, -1):
                phrase = " ".join(words[i:i + length])
                comp = self.dict.get_compound_pa(phrase)
                if comp:
                    parts.append(comp)
                    explanations.append(f"'{phrase}' → '{comp}'")
                    matched += length
                    total += length
                    i += length
                    found = True
                    break
            if found:
                continue

            word = words[i]
            total += 1
            i += 1

            is_opposite = word.endswith("'") and word not in self.dict.pa_to_entry
            base = word.rstrip("'") if is_opposite else word

            is_plural = False
            if base.endswith("wa") and len(base) > 2:
                without_wa = base[:-2]
                if self.dict.lookup_pa(without_wa):
                    base = without_wa
                    is_plural = True

            entry = self.dict.lookup_pa(word) or self.dict.lookup_pa(base)
            if entry:
                meaning = entry.primary_eng
                if is_plural:
                    meaning = self._pluralize_english(meaning)
                if is_opposite:
                    meaning = f"not-{meaning}"
                parts.append(meaning)
                explanations.append(f"'{word}' → '{meaning}'")
                matched += 1
            else:
                unknowns.append(word)
                parts.append(f"[{word}]")
                explanations.append(f"'{word}' → UNKNOWN")

        confidence = matched / max(total, 1)
        return TranslationResult(
            " ".join(parts), "; ".join(explanations),
            confidence, unknowns, "pa_to_eng",
        )
    
    #  MORPHOLOGY HELPERS
    def _normalize(self, text: str) -> str:
        for contraction, expanded in self.CONTRACTIONS.items():
            text = re.sub(r'\b' + re.escape(contraction) + r'\b', expanded, text)
        text = re.sub(r"[^\w\s'-]", "", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _detect_plural(word: str) -> tuple[bool, str]:
        if len(word) <= 2:
            return False, word
        if word.endswith("ies") and len(word) > 4:
            return True, word[:-3] + "y"
        if word.endswith("ves") and len(word) > 4:
            return True, word[:-3] + "f"
        if word.endswith("ses") or word.endswith("xes") or word.endswith("zes"):
            return True, word[:-2]
        if word.endswith("shes") or word.endswith("ches"):
            return True, word[:-2]
        if word.endswith("s") and not word.endswith("ss") and not word.endswith("us"):
            return True, word[:-1]
        return False, word

    @staticmethod
    def _detect_ing(word: str) -> tuple[bool, str]:
        if not word.endswith("ing") or len(word) <= 4:
            return False, word
        stem = word[:-3]
        if len(stem) >= 2 and stem[-1] == stem[-2]:
            return True, stem[:-1]
        return True, stem + "e" if stem and stem[-1] not in "aeiou" else (True, stem)

    @staticmethod
    def _detect_ed(word: str) -> tuple[bool, str]:
        if not word.endswith("ed") or len(word) <= 3:
            return False, word
        stem = word[:-2]
        if word.endswith("ied"):
            return True, word[:-3] + "y"
        if len(stem) >= 2 and stem[-1] == stem[-2]:
            return True, stem[:-1]
        if word.endswith("ed") and not word.endswith("eed"):
            return True, stem + "e" if stem and stem[-1] not in "aeiou" else (True, stem)
        return True, stem

    @staticmethod
    def _detect_ly(word: str) -> tuple[bool, str]:
        if word.endswith("ly") and len(word) > 3:
            return True, word[:-2]
        return False, word

    @staticmethod
    def _detect_er(word: str) -> tuple[bool, str]:
        if word.endswith("er") and len(word) > 3:
            stem = word[:-2]
            if len(stem) >= 2 and stem[-1] == stem[-2]:
                return True, stem[:-1]
            return True, stem + "e" if stem and stem[-1] not in "aeiou" else (True, stem)
        return False, word

    @staticmethod
    def _pluralize_english(word: str) -> str:
        if word.endswith(("s", "x", "z", "ch", "sh")):
            return word + "es"
        if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
            return word[:-1] + "ies"
        return word + "s"