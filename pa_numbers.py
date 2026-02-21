# numbers.py
"""
Algorithmic number conversion for Paj Ajap.
naj=1, neþ=3, nwo=6, þon=10
a=add, w=subtract, ф=multiply
"""


class PajAjapNumbers:
    DIGIT_TO_PA = {1: "naj", 3: "neþ", 6: "nwo", 10: "þon"}
    PA_TO_DIGIT = {"naj": 1, "neþ": 3, "nwo": 6, "þon": 10}
    SMALL = {
        0: "oza",
        1: "naj",
        2: "naj a naj",
        3: "neþ",
        4: "nwo w naj w naj",
        5: "nwo w naj",
        6: "nwo",
        7: "nwo a naj",
        8: "nwo a naj a naj",
        9: "þon w naj",
        10: "þon",
    }

    @classmethod
    def to_paj_ajap(cls, n: int) -> str | None:
        if n < 0:
            return None
        if n <= 10:
            return cls.SMALL.get(n, None)
        return cls._decompose(n)

    @classmethod
    def _decompose(cls, n: int) -> str:
        parts = []
        # Thousands
        if n >= 1000:
            t = n // 1000
            n %= 1000
            prefix = cls._small_or_decompose(t) + " ф " if t > 1 else ""
            parts.append(f"{prefix}þon ф þon ф þon")
        # Hundreds
        if n >= 100:
            h = n // 100
            n %= 100
            prefix = cls._small_or_decompose(h) + " ф " if h > 1 else ""
            parts.append(f"{prefix}þon ф þon")
        # Tens
        if n >= 10:
            t = n // 10
            n %= 10
            prefix = cls._small_or_decompose(t) + " ф " if t > 1 else ""
            parts.append(f"{prefix}þon")
        # Ones
        if n > 0:
            parts.append(cls._small_or_decompose(n))
        return " a ".join(parts) if parts else "oza"

    @classmethod
    def _small_or_decompose(cls, n: int) -> str:
        if n <= 10:
            return cls.SMALL.get(n, "oza")
        return cls._decompose(n)

    @classmethod
    def from_paj_ajap(cls, text: str) -> int | None:
        tokens = text.strip().split()
        if not tokens:
            return None
        if tokens == ["oza"]:
            return 0

        try:
            # Split into groups by a (add) and w (subtract)
            groups = []
            current_tokens = []
            current_sign = 1

            for token in tokens:
                if token == "a":
                    if current_tokens:
                        groups.append((current_sign, current_tokens))
                    current_tokens = []
                    current_sign = 1
                elif token == "w":
                    if current_tokens:
                        groups.append((current_sign, current_tokens))
                    current_tokens = []
                    current_sign = -1
                else:
                    current_tokens.append(token)

            if current_tokens:
                groups.append((current_sign, current_tokens))

            result = 0
            for sign, toks in groups:
                # Within a group, multiply all values (skip ф tokens)
                values = []
                for t in toks:
                    if t == "ф":
                        continue
                    if t in cls.PA_TO_DIGIT:
                        values.append(cls.PA_TO_DIGIT[t])
                    else:
                        return None

                product = 1
                for v in values:
                    product *= v
                result += sign * product

            return result
        except Exception:
            return None

    @classmethod
    def is_number_text(cls, text: str) -> bool:
        valid = set(cls.PA_TO_DIGIT.keys()) | {"a", "w", "ф", "oza"}
        tokens = text.strip().split()
        return len(tokens) > 0 and all(t in valid for t in tokens)