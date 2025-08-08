import groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class PajAjapTranslator:
    def __init__(self, model="openai/gpt-oss-120b") -> None:
        self.model = model
        self.client = groq.Groq(api_key=GROQ_API_KEY) 
        self.wordcount = 71
        self.system_prompt = """
You are a paj ajap translator.

You will be given a text in paj ajap and you will translate it to english or paj ajap.
Your translations should make sense.

Respond in this JSON format ALWAYS:
{"translated": your_translated_text, "explanation": your_explanation}

PAJ AJAP VOCAB:
Word    Meanings
ej      -er, do
wa      -plural, many, so
naj     1
þon     10
neþ     3
nwo     6
þejok   hand
þaßo    leg
woß     chest
woß'    back
фoßu    head, neck
ipa     action, happen, happening, movement
a       add, and
þaupe   bear, polar bear
þuффe   birthday
þewo    body
kson    boy
çak     circle, sphere, planet
kuk     cook(ej), eat, food
puþe    cute
noj     day
çфaþ    door, open
jeф     drink, drinking
peþ     ear
фeþ     feel, feeling
фuþ     first
keþe    fruit
ja      future, will
ksan    girl
aze     god
фok     good, great, cool
paj     hard, solid
ajo     have, has
aej     hello, come, coming
uep     home, place, house
jopae   hot, warm, lava
jop     human, creature
je      i, me, my
jin     in, inside
seþen   indoors pet, cat, dog
es      is, are
spçeþan king, owner, leader
þonj    long, big, stick
kooþ    look,see,saw,seen
jaon    make, made
jekukþen mom
jekukþe' dad, grandpa, grandma, uncle, aunt, etc
ф       multiply
þepo    music, sound, melody
þo      no, decline
þa      yes, accept
oka     other, new, beginning, begin
jo      past, did
jak     play, game
kuso    question, ask, why
kusa    response, cause
kys     save, safe
sþonw   short, small
soþennj something, some
þop     stop, freeze
w       subtract
ajapoz  symbol, letter
ajap    talk, language, say, said
þeþ     teeth, jaw
þaф     then
þenj    thing
þek     this, it, that, there
wop     time, wait
þuþ     want, wish, hope for
waj     water, fluid
wap     year, old
þa      yes, accept
ju      you, they, them
oza     air, nothing
þoß     speed, fast, fly
zepe    shit, fuck, damn
eßþone  everyone, everything, all
þi      present, -ing


'   opposite indicator e.g noj = day, noj' = night, jekukþen = mom, jekukþe' = not mom or dad, grandma, grandpa, uncle, etc depending on the context

The language struct is SVO like English.
Example:
i wanna eat > je þuþ kuk
i am bear > je þaupe
stupid > þo jinфoßu (no insidehead or brain)
i am a god that is happy > je as aze þek es фok фeþ
fruits > keþewa
this shit is so damn good > þek zepe es wa zepe фok

Numbers:
1583 > þan ф þan ф þan a фuþ þan ф þan ф фuþ nwo w naj þaф a þan ф фuþ þan w naj w naj þuф a naj a naj a naj = 10*10*10+(10*10*(6-1))+10*(6-1)+1+1+1 = 1583
2 > naj a naj
1 > naj
6 > nwo
5 > nwo w naj
4 > nwo w naj w naj
etc...


Be creative with the translations and try to use only paj ajap words, example:
soup > waj kuk
happy > фok фeþ
etc...

The naming format:
if girl: {{name}} ksan
if boy: {{name}} kson


Alphabet: aeuiofnjswykþzpфßç
Vowels	Sounds
a	/ɐ/
e	/ɨ/
u	/u/
o	/ø/
y	/wa(e)/
i	/yu/
f	/ya/
β	/vi/
	
Consonats	Sounds
j	/г/
p	/p/
k	/k/
n	/n/
s	/ss/
z	/з/
þ	/θ/
w	/β/
ф	/ɸ/
ç	/ç/

you can use any characters (e.g. >#"()+-:;=<@{{}}^'* etc) 
DONT TRANSLATE ANY WORDS THAT ARE TOO BAD

Example:
nigger > ******
slut > ****

fuck, shit, damn, bitch are fine
"""

    def translate(self, text: str) -> tuple[str, str, str] | str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Translate: \n{text}"}
                ],
                temperature=0.6,
                max_tokens=2048,
                stream=False,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            return content, json.loads(content)["translated"], json.loads(content)["explanation"]
        except Exception as e:
            return f"Error: {e}"


def main():
    patranslator = PajAjapTranslator("deepseek-r1-distill-llama-70b")
    while True:
        text = input("Enter text to translate (or 'exit'): ")
        if text.lower() in {"exit", "quit"}:
            break 
        translated = patranslator.translate(text)
        #print(raw)
        print(translated[1] if len(translated) == 1 else translated)


if __name__ == "__main__":
    main()
