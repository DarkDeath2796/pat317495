# dictionary.py
"""
Single source of truth for all Paj-Ajap <-> English vocabulary.
No external JSON files, no LLM — pure data.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DictEntry:
    pa_word: str
    eng_meanings: list[str]
    pos: str
    primary_eng: str = ""

    def __post_init__(self):
        if not self.primary_eng:
            self.primary_eng = self.eng_meanings[0]


class PajAjapDictionary:
    def __init__(self):
        self.entries: list[DictEntry] = []
        self.pa_to_entry: dict[str, DictEntry] = {}
        self.eng_to_entries: dict[str, list[DictEntry]] = {}
        self.compounds_eng_to_pa: dict[str, str] = {}
        self.compounds_pa_to_eng: dict[str, str] = {}
        self._build()

    def _build(self):
        raw = [
            ("ej", ["-er", "do", "doer"], "suffix/verb"),
            ("wa", ["-plural", "many", "so"], "suffix/adj"),
            ("naj", ["1", "one"], "number"),
            ("þon", ["10", "ten"], "number"),
            ("neþ", ["3", "three"], "number"),
            ("nwo", ["6", "six"], "number"),
            ("þejok", ["hand", "hands"], "noun"),
            ("þaßo", ["leg", "legs"], "noun"),
            ("woß", ["chest"], "noun"),
            ("woß'", ["back"], "noun"),
            ("фoßu", ["head", "neck"], "noun"),
            ("ipa", ["action", "happen", "happening", "movement", "move"], "noun/verb"),
            ("a", ["add", "and", "plus"], "conj/op"),
            ("þaupe", ["bear", "polar bear"], "noun"),
            ("þuффe", ["birthday"], "noun"),
            ("þewo", ["body"], "noun"),
            ("kson", ["boy"], "noun"),
            ("çak", ["circle", "sphere", "planet", "world"], "noun"),
            ("kuk", ["cook", "eat", "food", "meal"], "noun/verb"),
            ("puþe", ["cute", "adorable", "pretty"], "adj"),
            ("noj", ["day"], "noun"),
            ("noj'", ["night"], "noun"),
            ("çфaþ", ["door", "open"], "noun/verb"),
            ("jeф", ["drink", "drinking"], "noun/verb"),
            ("peþ", ["ear", "ears", "hear", "hearing", "listen"], "noun/verb"),
            ("фeþ", ["feel", "feeling", "emotion"], "noun/verb"),
            ("фuþ", ["first"], "adj/number"),
            ("keþe", ["fruit"], "noun"),
            ("ja", ["future", "will", "shall"], "tense"),
            ("ksan", ["girl"], "noun"),
            ("aze", ["god"], "noun"),
            ("фok", ["good", "great", "cool", "nice", "well"], "adj"),
            ("paj", ["hard", "solid", "difficult", "tough"], "adj"),
            ("ajo", ["have", "has", "own", "possess"], "verb"),
            ("aej", ["hello", "hi", "come", "coming", "welcome"], "interjection/verb"),
            ("uep", ["home", "place", "house", "location", "room"], "noun"),
            ("jopae", ["hot", "warm", "lava", "heat"], "adj/noun"),
            ("jop", ["human", "creature", "person", "people", "man", "woman"], "noun"),
            ("je", ["i", "me", "my", "myself"], "pronoun"),
            ("jin", ["in", "inside", "within", "into"], "prep"),
            ("seþen", ["pet", "cat", "dog"], "noun"),
            ("es", ["is", "are", "am", "be"], "verb"),
            ("spçeþan", ["king", "owner", "leader", "ruler", "queen", "boss", "chief"], "noun"),
            ("þonj", ["long", "big", "large", "stick", "tall", "huge"], "adj/noun"),
            ("kooþ", ["look", "see", "saw", "seen", "watch", "sight", "vision"], "verb/noun"),
            ("jaon", ["make", "made", "create", "build", "craft", "construct"], "verb"),
            ("jekukþen", ["mom", "mother", "mama"], "noun"),
            ("jekukþe'", ["dad", "father", "grandpa", "grandma", "uncle", "aunt"], "noun"),
            ("ф", ["multiply", "times"], "op"),
            ("þepo", ["music", "sound", "melody", "song", "noise"], "noun"),
            ("þo", ["no", "not", "decline", "don't", "doesn't", "isn't", "aren't", "never"], "adv"),
            ("þa", ["yes", "accept", "agree", "ok", "okay", "yeah", "yep"], "interjection"),
            ("oka", ["other", "new", "beginning", "begin", "start", "another", "different"], "adj/verb"),
            ("jo", ["past", "did", "was", "were", "ago"], "tense"),
            ("jak", ["play", "game", "fun", "playing"], "noun/verb"),
            ("kuso", ["question", "ask", "why", "what", "how", "who", "which"], "noun/verb"),
            ("kusa", ["response", "cause", "answer", "because", "reason", "reply"], "noun"),
            ("kys", ["save", "safe", "protect", "safety", "guard", "keep"], "verb/adj"),
            ("sþonw", ["short", "small", "tiny", "little", "mini"], "adj"),
            ("soþennj", ["something", "some", "someone", "somebody"], "pronoun"),
            ("þop", ["stop", "freeze", "halt", "pause", "end", "finish"], "verb"),
            ("w", ["subtract", "minus"], "op"),
            ("ajapoz", ["symbol", "letter", "character", "sign", "mark"], "noun"),
            ("ajap", ["talk", "language", "say", "said", "speak", "word", "speech", "tell", "told"], "noun/verb"),
            ("þeþ", ["teeth", "jaw", "tooth", "bite"], "noun/verb"),
            ("þaф", ["then", "after", "next", "afterwards"], "adv"),
            ("þenj", ["thing", "object", "item", "stuff"], "noun"),
            ("þek", ["this", "it", "that", "there", "here"], "pronoun/adv"),
            ("wop", ["time", "wait", "moment", "period", "while"], "noun/verb"),
            ("þuþ", ["want", "wish", "hope", "desire", "wanna", "need"], "verb"),
            ("waj", ["water", "fluid", "liquid", "wet"], "noun/adj"),
            ("wap", ["year", "old", "age", "years", "ancient"], "noun/adj"),
            ("ju", ["you", "they", "them", "your", "their", "yourself"], "pronoun"),
            ("oza", ["air", "nothing", "empty", "void", "zero", "none", "sky"], "noun/adj"),
            ("þoß", ["speed", "fast", "fly", "quick", "quickly", "flying", "run", "running", "rush"], "noun/adj/verb"),
            ("zepe", ["shit", "fuck", "damn", "crap"], "interjection"),
            ("eßþone", ["everyone", "everything", "all", "every", "everybody", "whole"], "pronoun/adj"),
            ("þi", ["present", "-ing", "currently", "now", "right now"], "tense/suffix"),
        ]

        for pa_word, eng_meanings, pos in raw:
            entry = DictEntry(pa_word=pa_word, eng_meanings=eng_meanings, pos=pos)
            self.entries.append(entry)
            self.pa_to_entry[pa_word] = entry

            for meaning in eng_meanings:
                clean = meaning.lstrip("-").lower().strip()
                if clean not in self.eng_to_entries:
                    self.eng_to_entries[clean] = []
                self.eng_to_entries[clean].append(entry)

        # Compound translations
        compounds = {
            "soup": "waj kuk",
            "happy": "фok фeþ",
            "happiness": "фok фeþ",
            "sad": "þo фok фeþ",
            "sadness": "þo фok фeþ",
            "unhappy": "þo фok фeþ",
            "stupid": "þo jinфoßu",
            "dumb": "þo jinфoßu",
            "smart": "фok jinфoßu",
            "intelligent": "фok jinфoßu",
            "clever": "фok jinфoßu",
            "brain": "jinфoßu",
            "mind": "jinфoßu",
            "think": "jinфoßu ipa",
            "thinking": "jinфoßu ipa þi",
            "thought": "jinфoßu ipa",
            "idea": "oka jinфoßu ipa",
            "love": "þonj фok фeþ",
            "hate": "þonj þo фok фeþ",
            "beautiful": "þonj puþe",
            "ugly": "þo puþe",
            "hungry": "þuþ kuk",
            "thirsty": "þuþ jeф",
            "tired": "þuþ þop",
            "alive": "þo þop þewo",
            "dead": "þop þewo",
            "death": "þop þewo",
            "die": "þop þewo",
            "life": "þo þop þewo",
            "live": "þo þop þewo",
            "cold": "þo jopae",
            "cool": "sþonw þo jopae",
            "ice": "paj waj",
            "fire": "jopae oza",
            "flame": "jopae oza",
            "burn": "jopae ipa",
            "burning": "jopae ipa þi",
            "ground": "paj çak",
            "earth": "paj çak",
            "land": "paj çak",
            "rock": "paj þenj",
            "stone": "paj þenj",
            "metal": "paj paj þenj",
            "sea": "þonj waj",
            "ocean": "þonj waj",
            "lake": "þop waj",
            "river": "þoß waj",
            "rain": "waj oza",
            "raining": "waj oza þi",
            "snow": "þo jopae waj",
            "wind": "þoß oza",
            "storm": "þonj þoß oza a waj",
            "friend": "фok jop",
            "enemy": "þo фok jop",
            "family": "jekukþen a jekukþe' wa",
            "child": "sþonw jop",
            "children": "sþonw jop wa",
            "baby": "sþonw sþonw jop",
            "name": "jop ajapoz",
            "morning": "oka noj",
            "evening": "þop noj",
            "afternoon": "jin noj",
            "today": "þi noj",
            "tomorrow": "ja noj",
            "yesterday": "jo noj",
            "good morning": "фok oka noj",
            "good night": "фok noj'",
            "goodbye": "þop aej",
            "bye": "þop aej",
            "please": "je þuþ",
            "thank you": "фok ju",
            "thanks": "фok ju",
            "sorry": "þo фok je",
            "angry": "jopae фeþ",
            "anger": "jopae фeþ",
            "mad": "jopae фeþ",
            "fear": "þo kys фeþ",
            "scared": "þo kys фeþ",
            "afraid": "þo kys фeþ",
            "scary": "jaon þo kys фeþ",
            "brave": "þo þo kys фeþ",
            "courage": "þo þo kys фeþ",
            "strong": "þonj paj",
            "strength": "þonj paj",
            "weak": "sþonw paj",
            "slow": "þo þoß",
            "slowly": "þo þoß",
            "loud": "þonj þepo",
            "quiet": "sþonw þepo",
            "silence": "þo þepo",
            "silent": "þo þepo",
            "eye": "kooþ þenj",
            "eyes": "kooþ þenj wa",
            "mouth": "kuk þeþ",
            "nose": "oza jin фoßu",
            "tongue": "kuk jin þeþ",
            "finger": "sþonw þejok",
            "fingers": "sþonw þejok wa",
            "arm": "þonj þejok",
            "arms": "þonj þejok wa",
            "foot": "sþonw þaßo",
            "feet": "sþonw þaßo wa",
            "heart": "jin woß фeþ",
            "blood": "jopae waj jin þewo",
            "bone": "paj jin þewo",
            "skin": "çak þewo",
            "hair": "фoßu oza þenj",
            "tree": "þonj keþe þenj",
            "flower": "puþe keþe",
            "forest": "þonj keþe þenj wa",
            "mountain": "þonj paj çak",
            "hill": "sþonw paj çak",
            "valley": "jin paj çak",
            "sun": "jopae çak",
            "moon": "noj' çak",
            "star": "sþonw jopae çak",
            "stars": "sþonw jopae çak wa",
            "space": "þonj oza",
            "sleep": "þop kooþ",
            "sleeping": "þop kooþ þi",
            "asleep": "þop kooþ",
            "awake": "þo þop kooþ",
            "wake up": "oka kooþ",
            "dream": "þop kooþ jinфoßu",
            "walk": "sþonw þoß þaßo",
            "walking": "sþonw þoß þaßo þi",
            "fight": "jopae ipa",
            "fighting": "jopae ipa þi",
            "war": "þonj jopae ipa",
            "peace": "þop jopae ipa",
            "work": "paj ipa",
            "working": "paj ipa þi",
            "worker": "paj ipa ej",
            "job": "paj ipa",
            "teacher": "ajap ej",
            "student": "ajap kooþ ej",
            "school": "ajap uep",
            "book": "ajap þenj",
            "story": "þonj ajap",
            "write": "jaon ajapoz",
            "writing": "jaon ajapoz þi",
            "read": "kooþ ajapoz",
            "reading": "kooþ ajapoz þi",
            "learn": "oka jinфoßu",
            "learning": "oka jinфoßu þi",
            "know": "ajo jinфoßu",
            "knowledge": "ajo jinфoßu",
            "understand": "фok jinфoßu kooþ",
            "dance": "þepo þaßo ipa",
            "dancing": "þepo þaßo ipa þi",
            "sing": "þepo ajap",
            "singing": "þepo ajap þi",
            "singer": "þepo ajap ej",
            "musician": "þepo ej",
            "bird": "þoß jop oza",
            "fish": "waj jop",
            "animal": "þo jop jop",
            "wolf": "þoß seþen",
            "lion": "spçeþan þo jop jop",
            "horse": "þonj þoß þo jop jop",
            "snake": "þo þaßo jop",
            "insect": "sþonw sþonw þo jop jop",
            "bug": "sþonw sþonw þo jop jop",
            "king": "spçeþan",
            "queen": "spçeþan ksan",
            "weapon": "jopae ipa þenj",
            "sword": "þonj jopae ipa þenj",
            "shield": "kys þenj",
            "armor": "kys çak þewo",
            "wall": "paj çak uep",
            "window": "kooþ çфaþ",
            "roof": "фoßu uep",
            "floor": "þaßo uep",
            "table": "paj þejok þenj",
            "chair": "þop þaßo þenj",
            "bed": "þop kooþ þenj",
            "clothes": "çak þewo þenj",
            "shirt": "woß çak þewo þenj",
            "shoes": "þaßo çak þewo þenj",
            "hat": "фoßu çak þewo þenj",
            "color": "kooþ фeþ",
            "light": "sþonw jopae çak ipa",
            "dark": "þo sþonw jopae çak ipa",
            "darkness": "þo sþonw jopae çak ipa",
            "shadow": "þo sþonw jopae çak þenj",
            "true": "paj þa",
            "truth": "paj þa",
            "false": "þo paj þa",
            "lie": "þo paj þa ajap",
            "secret": "þo kooþ ajap",
            "magic": "þo kooþ ipa",
            "power": "þonj ipa",
            "powerful": "þonj ipa ajo",
            "rich": "þonj ajo",
            "poor": "sþonw ajo",
            "money": "ajo ajapoz",
            "give": "ajo oka jop",
            "take": "ajo je",
            "share": "ajo eßþone",
            "help": "фok ipa jop",
            "hurt": "þo фok ipa þewo",
            "pain": "þo фok фeþ þewo",
            "sick": "þo фok þewo",
            "healthy": "фok þewo",
            "medicine": "фok þewo þenj",
            "doctor": "фok þewo ej",
            "eat food": "kuk kuk",
            "drink water": "jeф waj",
            "i love you": "je þonj фok фeþ ju",
            "i hate you": "je þonj þo фok фeþ ju",
            "what is this": "kuso es þek",
            "where is": "kuso uep es",
            "how are you": "kuso es ju",
            "i am good": "je es фok",
            "i am fine": "je es фok",
            "i don't know": "je þo ajo jinфoßu",
            "i am happy": "je es фok фeþ",
            "i am sad": "je es þo фok фeþ",
            "let's go": "aej eßþone",
            "come here": "aej þek",
            "go away": "þoß oka uep",
        }

        for eng, pa in compounds.items():
            self.compounds_eng_to_pa[eng.lower()] = pa

        # Build reverse (pa -> eng), prefer shorter English meanings
        for eng, pa in sorted(compounds.items(), key=lambda x: len(x[0])):
            if pa not in self.compounds_pa_to_eng:
                self.compounds_pa_to_eng[pa] = eng

    def lookup_eng(self, word: str) -> list[DictEntry] | None:
        clean = word.lower().strip()
        comp = self.compounds_eng_to_pa.get(clean)
        if comp:
            return [DictEntry(pa_word=comp, eng_meanings=[clean], pos="compound")]
        return self.eng_to_entries.get(clean)

    def lookup_pa(self, word: str) -> DictEntry | None:
        clean = word.strip()
        comp = self.compounds_pa_to_eng.get(clean)
        if comp:
            return DictEntry(pa_word=clean, eng_meanings=[comp], pos="compound")
        return self.pa_to_entry.get(clean)

    def get_compound_eng(self, phrase: str) -> str | None:
        return self.compounds_eng_to_pa.get(phrase.lower().strip())

    def get_compound_pa(self, phrase: str) -> str | None:
        return self.compounds_pa_to_eng.get(phrase.strip())