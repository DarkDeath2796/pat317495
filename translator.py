# translator.py
"""
Hybrid translator: deterministic first, LLM fallback only for unknown words.
"""

import groq
import os
import json
import logging
from dotenv import load_dotenv
from deterministic_translator import DeterministicTranslator, TranslationResult

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

CONFIDENCE_THRESHOLD = 0.85


class PajAjapTranslator:
    def __init__(self, model="openai/gpt-oss-20b") -> None:
        self.model = model
        self.client = groq.Groq(api_key=GROQ_API_KEY)
        self.deterministic = DeterministicTranslator()
        self._llm_cache: dict[str, tuple[str, str]] = {}

        self.system_prompt = (
            "You are a Paj Ajap conlang translator. "
            "You receive a partial translation with [bracketed] unknown words. "
            "Replace each [word] with a creative Paj Ajap compound using ONLY "
            "these base words:\n"
            "je=i, ju=you, es=is, þo=no/not, þa=yes, þek=this/it, "
            "ajo=have, þuþ=want, kooþ=see, kuk=eat/food, jeф=drink, "
            "ajap=talk/say, jaon=make, ipa=action/move, þoß=fast/fly, "
            "þop=stop, oka=new/begin, фok=good, paj=hard, puþe=cute, "
            "þonj=big, sþonw=small, jopae=hot, waj=water, oza=air/nothing, "
            "jin=inside, фoßu=head, þewo=body, woß=chest, þaßo=leg, "
            "þejok=hand, peþ=ear, þeþ=teeth, фeþ=feel, þenj=thing, "
            "uep=home/place, jop=human, çak=circle/planet, wop=time, "
            "noj=day, wap=year, þepo=music/sound, seþen=pet, keþe=fruit, "
            "spçeþan=king/leader, zepe=shit/damn, eßþone=all/everyone, "
            "kuso=question/ask, kusa=response/cause, kys=safe/save, "
            "ajapoz=symbol/letter, çфaþ=door/open, soþennj=something\n"
            "Suffixes: wa=plural, ej=-er/doer, '=opposite\n"
            "Tense: þi=present/-ing, jo=past, ja=future/will\n"
            "SVO order. Respond ONLY with JSON: "
            '{"translated": "...", "explanation": "..."}'
        )

    def translate(self, text: str) -> tuple[str, str, str] | str:
        key = text.strip().lower()
        if key in self._llm_cache:
            t, e = self._llm_cache[key]
            return json.dumps({"translated": t, "explanation": e}), t, e

        det: TranslationResult = self.deterministic.translate(text)

        if det.confidence >= CONFIDENCE_THRESHOLD and not det.unknown_words:
            self._llm_cache[key] = (det.translated, det.explanation)
            return (
                json.dumps({"translated": det.translated, "explanation": det.explanation}),
                det.translated,
                det.explanation,
            )

        logging.info("LLM fallback: conf=%.2f unknowns=%s", det.confidence, det.unknown_words)
        return self._llm_fallback(text, det, key)

    def _llm_fallback(self, text: str, det: TranslationResult, cache_key: str) -> tuple[str, str, str] | str:
        try:
            user_msg = (
                f"Original: {text}\n"
                f"Direction: {det.direction}\n"
                f"Partial: {det.translated}\n"
                f"Unknown: {det.unknown_words}\n"
                f"Complete the translation."
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.4,
                max_tokens=512,
                stream=False,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or ""
            parsed = json.loads(content)
            t = parsed["translated"]
            e = parsed.get("explanation", "")
            self._llm_cache[cache_key] = (t, e)
            return content, t, e

        except Exception as e:
            logging.error("LLM error: %s", e)
            return (
                json.dumps(det.to_dict()),
                det.translated,
                det.explanation,
            )


def main():
    translator = PajAjapTranslator()
    while True:
        text = input("Translate (or 'exit'): ")
        if text.lower() in {"exit", "quit"}:
            break
        result = translator.translate(text)
        if isinstance(result, tuple):
            print(f"→ {result[1]}")
            print(f"  ({result[2]})")
        else:
            print(result)


if __name__ == "__main__":
    main()
