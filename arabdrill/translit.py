"""Transliterasi Latin OPSIONAL untuk teks Arab berharakat.

Transliterasi di proyek ini sengaja dimatikan secara bawaan. Pengguna sasaran
sudah bisa membaca tulisan Arab, dan penyangga Latin justru memperlambat
pembacaan. Nyalakan dengan bendera --translit hanya bila diperlukan, misalnya
untuk memastikan sebuah harakat terbaca benar.

Catatan penting: alih huruf di sini mengikuti TULISAN, bukan lafal. Kata هَذَا
menjadi "hadhā" (sesuai yang tertulis), padahal dilafalkan "hādhā". Hal yang
sama berlaku untuk ذَلِكَ dan أُولَئِكَ.
"""

from __future__ import annotations

from .arabic import (
    ALIF,
    ALIF_MADDA,
    ALIF_MAQSURA,
    DAMMA,
    DAMMATAN,
    FATHA,
    FATHATAN,
    KASRA,
    KASRATAN,
    LAM,
    LETTERS,
    MARKS,
    SHADDA,
    SUKUN,
    TEH_MARBUTA,
    WAW,
    YEH,
    letter_units,
    nfc,
)

CONSONANTS = {
    "ء": "ʾ",       # ء
    "آ": "ʾā",  # آ -> 'ā
    "أ": "ʾ",       # أ
    "ؤ": "ʾ",       # ؤ
    "إ": "ʾ",       # إ
    "ئ": "ʾ",       # ئ
    "ا": "",             # ا (pembawa vokal)
    "ب": "b",
    "ة": "h",            # ة saat tidak berharakat
    "ت": "t",
    "ث": "th",
    "ج": "j",
    "ح": "ḥ",       # ḥ
    "خ": "kh",
    "د": "d",
    "ذ": "dh",
    "ر": "r",
    "ز": "z",
    "س": "s",
    "ش": "sh",
    "ص": "ṣ",       # ṣ
    "ض": "ḍ",       # ḍ
    "ط": "ṭ",       # ṭ
    "ظ": "ẓ",       # ẓ
    "ع": "ʿ",       # ʿ
    "غ": "gh",
    "ف": "f",
    "ق": "q",
    "ك": "k",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "ه": "h",
    "و": "w",
    "ى": "ā",      # ى -> ā
    "ي": "y",
}

SHORT = {FATHA: "a", DAMMA: "u", KASRA: "i"}
TANWIN_MAP = {FATHATAN: "an", DAMMATAN: "un", KASRATAN: "in"}
LONG = {FATHA: "ā", DAMMA: "ū", KASRA: "ī"}


def _is_bare(unit: tuple[str, list[str]]) -> bool:
    return not unit[1]


def _consonant(letter: str, marks: list[str]) -> str:
    if letter == TEH_MARBUTA:
        return "t" if marks else "h"
    return CONSONANTS.get(letter, letter)


def _translit_word(word: str) -> str:
    units = letter_units(word)
    if not units:
        return ""
    out: list[str] = []
    i = 0

    # Kata sandang ال di awal kata.
    if (
        len(units) >= 3
        and units[0][0] == ALIF
        and units[1][0] == LAM
        and not any(m in SHORT or m in TANWIN_MAP for m in units[0][1])
    ):
        third_letter, third_marks = units[2]
        if SHADDA in third_marks:
            out.append("a" + _consonant(third_letter, third_marks) + "-")
            i = 2
            # Satu salinan huruf sudah dikeluarkan; jangan digandakan lagi.
            units = list(units)
            units[2] = (third_letter, [m for m in third_marks if m != SHADDA])
        else:
            out.append("al-")
            i = 2

    while i < len(units):
        letter, marks = units[i]
        cons = _consonant(letter, marks)
        if SHADDA in marks:
            cons = cons * 2
        vowel = next((m for m in marks if m in SHORT), None)
        tanwin = next((m for m in marks if m in TANWIN_MAP), None)
        nxt = units[i + 1] if i + 1 < len(units) else None

        if tanwin:
            out.append(cons + TANWIN_MAP[tanwin])
            i += 1
            # Alif penyangga pada tanwin fathatan tidak dibaca.
            if i < len(units) and units[i][0] in (ALIF, ALIF_MAQSURA) and _is_bare(units[i]):
                i += 1
            continue

        if vowel and nxt is not None and _is_bare(nxt):
            # Vokal panjang (mad).
            if vowel == FATHA and nxt[0] in (ALIF, ALIF_MAQSURA):
                out.append(cons + LONG[FATHA])
                i += 2
                continue
            if vowel == DAMMA and nxt[0] == WAW:
                out.append(cons + LONG[DAMMA])
                i += 2
                # Alif mati setelah waw jamak (كَتَبُوا) tidak dibaca.
                if i < len(units) and units[i][0] == ALIF and _is_bare(units[i]):
                    i += 1
                continue
            if vowel == KASRA and nxt[0] == YEH:
                out.append(cons + LONG[KASRA])
                i += 2
                continue

        if vowel == FATHA and nxt is not None and SUKUN in nxt[1]:
            # Diftong aw / ay.
            if nxt[0] == WAW:
                out.append(cons + "aw")
                i += 2
                continue
            if nxt[0] == YEH:
                out.append(cons + "ay")
                i += 2
                continue

        if vowel:
            out.append(cons + SHORT[vowel])
        else:
            out.append(cons)
        i += 1

    return "".join(out)


def translit(text: str) -> str:
    """Alih huruf satu teks Arab berharakat menjadi Latin.

    Karakter non-Arab (spasi, tanda baca) diteruskan apa adanya.
    """
    text = nfc(text)
    out: list[str] = []
    buf: list[str] = []
    for ch in text:
        if ch in LETTERS or ch in MARKS:
            buf.append(ch)
            continue
        if buf:
            out.append(_translit_word("".join(buf)))
            buf = []
        out.append(ch)
    if buf:
        out.append(_translit_word("".join(buf)))
    return "".join(out)


__all__ = ["translit"]
