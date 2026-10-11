"""Utilitas teks Arab: normalisasi, pelepasan harakat, dan validasi harakat.

Modul ini sengaja tidak memakai pustaka luar supaya hasilnya deterministik dan
bisa diuji. Semua aturan di sini bersifat ORTOGRAFIS (cara penulisan), bukan
penilaian isi bahasa. Kebenaran makna, gender, jamak, dan akar kata TIDAK bisa
diperiksa oleh mesin -- lihat data/NEEDS_REVIEW.md dan README.md.

Validator ini dipakai pada field data (lema, contoh kalimat, pilihan jawaban),
BUKAN pada field prosa (explanation, caveats, note, explain). Field prosa boleh
memuat akhiran yang ditulis dengan tatwil (misalnya ـكَ) dan contoh bentuk yang
sengaja salah untuk diperbandingkan; keduanya akan ditolak validator ini.
"""

from __future__ import annotations

import unicodedata

# ---------------------------------------------------------------- karakter ---

HAMZA = "ء"            # ء
ALIF_MADDA = "آ"       # آ
ALIF_HAMZA_ABOVE = "أ"  # أ
WAW_HAMZA = "ؤ"        # ؤ
ALIF_HAMZA_BELOW = "إ"  # إ
YEH_HAMZA = "ئ"        # ئ
ALIF = "ا"             # ا
TEH_MARBUTA = "ة"      # ة
LAM = "ل"              # ل
WAW = "و"              # و
ALIF_MAQSURA = "ى"     # ى
YEH = "ي"              # ي

LETTERS = set(
    "ءآأؤإئابةتث"
    "جحخدذرزسشصض"
    "طظعغفقكلمنه"
    "وىي"
)

FATHATAN = "ً"
DAMMATAN = "ٌ"
KASRATAN = "ٍ"
FATHA = "َ"
DAMMA = "ُ"
KASRA = "ِ"
SHADDA = "ّ"
SUKUN = "ْ"

TANWIN = {FATHATAN, DAMMATAN, KASRATAN}
SHORT_VOWELS = {FATHA, DAMMA, KASRA}
VOWELS = SHORT_VOWELS | TANWIN
MARKS = VOWELS | {SHADDA, SUKUN}

# Tanda baca yang diizinkan di dalam contoh kalimat.
PUNCT = set(" ،؛؟.!:—-")

TATWEEL = "ـ"

# Huruf yang boleh berdiri tanpa tanda apa pun karena memang tidak pernah
# memikul harakat dalam penulisan baku.
BARE_ALWAYS = {ALIF, ALIF_MAQSURA, ALIF_MADDA}

# Huruf syamsiyah: lam pada "ال" tidak diberi tanda bila huruf sesudahnya
# bersyaddah (الشَّمْس), sesuai kebiasaan penulisan mushaf dan buku berharakat.
SUN_LETTERS = set("تثدذرزسشص"
                  "ضطظلن")


# -------------------------------------------------------------- normalisasi ---

def nfc(text: str) -> str:
    """Normalisasi Unicode ke bentuk NFC."""
    return unicodedata.normalize("NFC", text)


def is_nfc(text: str) -> bool:
    return unicodedata.is_normalized("NFC", text)


def strip_harakat(text: str) -> str:
    """Buang semua tanda harakat, syaddah, sukun, dan tanwin.

    Catatan: tanwin fathatan di atas huruf sebelum alif ikut hilang sehingga
    "كِتَابًا" menjadi "كتابا" -- alifnya tetap, seperti tulisan Arab tanpa harakat
    pada umumnya.
    """
    return "".join(ch for ch in nfc(text) if ch not in MARKS)


def strip_harakat_keep_shadda(text: str) -> str:
    """Buang harakat tetapi pertahankan syaddah (dipakai pada Level 2)."""
    return "".join(ch for ch in nfc(text) if ch not in MARKS or ch == SHADDA)


def split_words(text: str) -> list[str]:
    """Pecah teks menjadi kata, dengan tanda baca dibuang."""
    out: list[str] = []
    cur: list[str] = []
    for ch in nfc(text):
        if ch in LETTERS or ch in MARKS:
            cur.append(ch)
        else:
            if cur:
                out.append("".join(cur))
                cur = []
    if cur:
        out.append("".join(cur))
    return out


def partial_harakat(text: str, keep: set[int]) -> str:
    """Render teks dengan harakat hanya pada kata yang indeksnya ada di `keep`.

    Indeks dihitung atas kata (dipisah spasi), mulai dari 0. Kata lain dilepas
    harakatnya tetapi syaddah dipertahankan karena syaddah mengubah identitas
    huruf, bukan sekadar vokal.
    """
    parts = nfc(text).split(" ")
    return " ".join(
        p if i in keep else strip_harakat_keep_shadda(p)
        for i, p in enumerate(parts)
    )


# ------------------------------------------------------------------ analisa ---

def letter_units(word: str) -> list[tuple[str, list[str]]]:
    """Pecah satu kata menjadi daftar (huruf, [tanda-tanda setelahnya])."""
    units: list[tuple[str, list[str]]] = []
    for ch in word:
        if ch in LETTERS:
            units.append((ch, []))
        elif ch in MARKS:
            if not units:
                units.append(("", []))
            units[-1][1].append(ch)
    return units


def consonant_skeleton(word: str) -> str:
    """Rangka huruf sebuah kata: tanpa harakat dan tanpa huruf tambahan ejaan."""
    return "".join(ch for ch in nfc(word) if ch in LETTERS)


# ------------------------------------------------------------------ validasi ---

class VocalizationError(str):
    """Pesan kesalahan; subclass str supaya mudah dibandingkan dan dicetak."""


def check_charset(text: str, *, allow_punct: bool) -> list[str]:
    problems: list[str] = []
    if not is_nfc(text):
        problems.append("teks belum dalam bentuk NFC")
    if TATWEEL in text:
        problems.append("memakai tatwil (U+0640), tidak diizinkan")
    for ch in text:
        if ch in LETTERS or ch in MARKS:
            continue
        if allow_punct and ch in PUNCT:
            continue
        problems.append(
            f"karakter tidak diizinkan: {ch!r} (U+{ord(ch):04X})"
        )
    return problems


def _check_marks_order(units: list[tuple[str, list[str]]], word: str) -> list[str]:
    problems: list[str] = []
    for i, (letter, marks) in enumerate(units):
        vowels = [m for m in marks if m in VOWELS]
        shaddas = [m for m in marks if m == SHADDA]
        sukuns = [m for m in marks if m == SUKUN]
        if len(vowels) > 1:
            problems.append(f"{word}: huruf ke-{i+1} ({letter}) punya lebih dari satu vokal")
        if len(shaddas) > 1:
            problems.append(f"{word}: huruf ke-{i+1} ({letter}) punya syaddah ganda")
        if sukuns and (vowels or shaddas):
            problems.append(f"{word}: huruf ke-{i+1} ({letter}) bersukun sekaligus berharakat")
        # Urutan tanda tidak diperiksa di sini: bentuk NFC sudah menetapkan
        # urutan kanonik (vokal lebih dulu, lalu syaddah, karena kelas
        # penggabungan kanoniknya 30-32 berbanding 33). Pemeriksaan is_nfc()
        # pada check_charset() sudah menjamin hal itu.
    return problems


def _tanwin_positions_ok(units: list[tuple[str, list[str]]]) -> bool:
    """Tanwin hanya sah pada huruf terakhir, atau huruf sebelum alif/alif maqshurah akhir."""
    last = len(units) - 1
    for i, (_letter, marks) in enumerate(units):
        if not any(m in TANWIN for m in marks):
            continue
        if i == last:
            continue
        if i == last - 1 and units[last][0] in (ALIF, ALIF_MAQSURA) and not units[last][1]:
            continue
        return False
    return True


def _letter_may_be_bare(units: list[tuple[str, list[str]]], i: int, *, final_free: bool) -> bool:
    letter, marks = units[i]
    if letter in BARE_ALWAYS:
        return True
    prev = units[i - 1] if i > 0 else None
    nxt = units[i + 1] if i + 1 < len(units) else None
    # Madd: waw setelah dhammah, ya' setelah kasrah.
    if letter == WAW and prev and DAMMA in prev[1]:
        return True
    if letter == YEH and prev and KASRA in prev[1]:
        return True
    # Lam pada "ال" sebelum huruf syamsiyah bersyaddah.
    if (
        letter == LAM
        and prev
        and prev[0] == ALIF
        and not prev[1]
        and nxt
        and SHADDA in nxt[1]
        and nxt[0] in SUN_LETTERS
    ):
        return True
    # Huruf terakhir pada bentuk lema (waqf).
    if final_free and i == len(units) - 1:
        return True
    return False


def validate_vocalization(
    text: str, *, mode: str = "sentence", allow_punct: bool | None = None
) -> list[str]:
    """Periksa kelengkapan harakat sebuah teks Arab.

    mode="sentence": setiap huruf setiap kata harus bertanda, termasuk huruf
        terakhir (i'rab ditulis). Dipakai untuk contoh kalimat dan teks latihan.
    mode="lemma": huruf terakhir setiap kata boleh tanpa tanda (bentuk waqf,
        seperti penulisan kamus). Dipakai untuk lema, jamak, bentuk mu'annats,
        dan bentuk mudhari'.

    allow_punct: secara bawaan tanda baca hanya diizinkan pada mode "sentence",
        supaya field lema satu kata terjaga dari karakter nyasar. Pilihan
        jawaban soal yang berupa frasa memakai mode="lemma" dengan
        allow_punct=True.

    Mengembalikan daftar pesan masalah; daftar kosong berarti lulus.
    """
    if mode not in ("sentence", "lemma"):
        raise ValueError("mode harus 'sentence' atau 'lemma'")
    if allow_punct is None:
        allow_punct = mode == "sentence"
    text = nfc(text)
    problems = check_charset(text, allow_punct=allow_punct)
    if problems:
        return problems

    final_free = mode == "lemma"
    for word in split_words(text):
        units = letter_units(word)
        if not units:
            continue
        problems += _check_marks_order(units, word)
        if not _tanwin_positions_ok(units):
            problems.append(f"{word}: tanwin berada di posisi yang tidak sah")
        for i, (letter, marks) in enumerate(units):
            is_last = i == len(units) - 1
            if not marks:
                if not _letter_may_be_bare(units, i, final_free=final_free):
                    problems.append(
                        f"{word}: huruf ke-{i+1} ({letter}) tidak berharakat"
                    )
                continue
            if marks == [SHADDA]:
                # Syaddah tanpa vokal hanya sah pada huruf terakhir bentuk waqf.
                if not (final_free and is_last):
                    problems.append(
                        f"{word}: huruf ke-{i+1} ({letter}) bersyaddah tanpa vokal"
                    )
    return problems


def validate_root(root: str) -> list[str]:
    """Akar ditulis sebagai huruf-huruf tanpa harakat dipisah satu spasi."""
    problems: list[str] = []
    if not is_nfc(root):
        problems.append("akar belum dalam bentuk NFC")
    parts = root.split(" ")
    if len(parts) < 3:
        problems.append(f"akar '{root}' kurang dari tiga huruf")
    for p in parts:
        if len(p) != 1 or p not in LETTERS:
            problems.append(f"akar '{root}': '{p}' bukan satu huruf Arab tanpa harakat")
    return problems


# ------------------------------------------------- kecocokan akar dan kata ---

#: Huruf akar yang sering tidak muncul di permukaan kata (akar lemah/mu'tall).
WEAK = {HAMZA, ALIF, WAW, YEH, ALIF_MADDA, ALIF_HAMZA_ABOVE,
        ALIF_HAMZA_BELOW, WAW_HAMZA, YEH_HAMZA, ALIF_MAQSURA}

#: Pemetaan huruf yang saling menggantikan dalam ejaan hamzah dan alif.
_EQUIV = {
    ALIF: {ALIF, ALIF_MADDA, ALIF_HAMZA_ABOVE, ALIF_HAMZA_BELOW, ALIF_MAQSURA, HAMZA},
    HAMZA: {HAMZA, ALIF_MADDA, ALIF_HAMZA_ABOVE, ALIF_HAMZA_BELOW, WAW_HAMZA, YEH_HAMZA, ALIF},
    WAW: {WAW, WAW_HAMZA},
    YEH: {YEH, YEH_HAMZA, ALIF_MAQSURA},
}


def _equiv(root_letter: str) -> set[str]:
    return _EQUIV.get(root_letter, {root_letter})


def root_letters_found(root: str, word: str) -> int:
    """Jumlah huruf akar yang muncul berurutan (subsequence) dalam kata.

    Bila satu huruf akar tidak ditemukan (lazim pada akar lemah: كَانَ dari
    ك و ن), penelusuran TIDAK dimajukan sehingga huruf akar berikutnya masih
    bisa dicocokkan dari posisi yang sama.
    """
    skeleton = consonant_skeleton(word)
    pos = 0
    found = 0
    for rl in root.split(" "):
        options = _equiv(rl)
        hit = next((j for j in range(pos, len(skeleton)) if skeleton[j] in options), None)
        if hit is not None:
            found += 1
            pos = hit + 1
    return found


def root_is_weak(root: str) -> bool:
    letters = root.split(" ")
    if any(l in WEAK for l in letters):
        return True
    # Akar mudha'af: huruf kedua dan ketiga sama.
    return len(letters) >= 3 and letters[-1] == letters[-2]


def root_matches(root: str, word: str) -> bool:
    """Apakah huruf akar muncul berurutan pada kata.

    Untuk akar sehat (tanpa huruf lemah), SEMUA huruf akar harus muncur
    berurutan. Untuk akar lemah atau mudha'af, huruf yang luruh di permukaan
    adalah hal biasa (kata كَانَ dari ك و ن, مَاء dari م و ه), sehingga yang
    disyaratkan hanya mayoritas hurufnya; kekurangannya harus dijelaskan pada
    field root_note.
    """
    letters = root.split(" ")
    found = root_letters_found(root, word)
    if root_is_weak(root):
        return found >= len(letters) - 1
    return found == len(letters)
