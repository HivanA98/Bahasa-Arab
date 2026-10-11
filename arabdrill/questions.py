"""Pembuat soal untuk setiap mode latihan.

Soal yang dibuat otomatis (akar kata dan kartu kosakata dua arah) selalu
mengambil kunci jawaban LANGSUNG dari data, bukan dari daftar terpisah,
sehingga kunci tidak bisa menyimpang dari sumbernya. Pengecoh dipilih dengan
generator acak ber-seed agar hasilnya bisa diulang dan diuji.
"""

from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass, field

from . import dataio
from .arabic import PUNCT, strip_harakat, strip_harakat_keep_shadda

MODES = ("kosakata-ar", "kosakata-id", "tatabahasa", "akar", "baca")

_ACCEPTED_CACHE: dict[tuple, frozenset[str]] = {}

MODE_LABELS = {
    "kosakata-ar": "Kosakata: Arab ke Indonesia",
    "kosakata-id": "Kosakata: Indonesia ke Arab",
    "tatabahasa": "Tata bahasa",
    "akar": "Akar kata dan pola",
    "baca": "Membaca tanpa harakat",
}


@dataclass
class Question:
    card_id: str
    mode: str
    kind: str  # "mcq" | "typed" | "selfcheck"
    question: str
    stimulus_ar: str | None = None
    stimulus_label: str | None = None
    options: list[str] | None = None
    options_lang: str | None = None
    answer: int | None = None
    accepted: list[str] = field(default_factory=list)
    reveal: str = ""
    reveal_ar: str | None = None
    explain: str | None = None
    #: True bila soal ini adalah pengulangan materi baru di lintasan kedua
    #: sesi yang sama. quiz.py tidak menaikkan kotak Leitner dua kali.
    repeat: bool = False
    #: Tahap materi (1-6). Dipakai session.py untuk memperkenalkan kartu baru
    #: menurut urutan tahap, bukan secara acak dari seluruh materi.
    stage: int | None = None

    def is_correct_text(self, text: str) -> bool:
        return normalize(text) in {normalize(a) for a in self.accepted}


# ------------------------------------------------------- jawaban bertaip ---

_PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Bakukan jawaban bertaip: huruf kecil, tanpa tanda baca, spasi tunggal."""
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = _PUNCT_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


def expand_accepted(gloss: str, alt: list[str] | None = None) -> list[str]:
    """Kembangkan arti menjadi daftar jawaban yang diterima.

    "besar, tua (usia)" menghasilkan: kalimat utuhnya, "besar", "tua (usia)",
    dan "tua". Tujuannya supaya pengguna tidak dihukum karena menulis salah
    satu arti saja.
    """
    out: list[str] = []

    def add(s: str) -> None:
        s = s.strip()
        if s and s not in out:
            out.append(s)

    add(gloss)
    for piece in re.split(r"[,;/]", gloss):
        add(piece)
        add(re.sub(r"\([^)]*\)", "", piece))
    for a in alt or []:
        add(a)
        add(re.sub(r"\([^)]*\)", "", a))
    return [o for o in out if o]


# ------------------------------------------------------------- pengecoh ---

def _pick_distractors(
    rng: random.Random, pool: list[dict], target: dict, key: str, n: int = 3
) -> list[str]:
    """Pilih n pengecoh, mengutamakan kata dengan kelas kata yang sama."""
    want = target[key]
    same_pos = [e for e in pool if e[key] != want and e.get("pos") == target.get("pos")]
    same_cat = [e for e in pool if e[key] != want and e.get("cat") == target.get("cat")]
    others = [e for e in pool if e[key] != want]
    chosen: list[str] = []
    for bucket in (same_pos, same_cat, others):
        rng.shuffle(bucket)
        for e in bucket:
            if e[key] not in chosen and len(chosen) < n:
                chosen.append(e[key])
        if len(chosen) >= n:
            break
    return chosen[:n]


def _shuffle_options(rng: random.Random, correct: str, distractors: list[str]) -> tuple[list[str], int]:
    opts = [correct] + [d for d in distractors if d != correct]
    rng.shuffle(opts)
    return opts, opts.index(correct)


# ------------------------------------------------------------- kosakata ---

def _vocab_detail(e: dict) -> str:
    bits = [e["pos"]]
    if e.get("gender"):
        bits.append({"m": "mudzakkar", "f": "mu'annats", "m/f": "mudzakkar/mu'annats"}[e["gender"]])
    if e.get("plural"):
        bits.append(f"jamak: {e['plural']}")
    if e.get("fem"):
        bits.append(f"mu'annats: {e['fem']}")
    if e.get("mudhari"):
        bits.append(f"mudhari': {e['mudhari']}")
    if e.get("root"):
        bits.append(f"akar: {e['root']}")
    return " · ".join(bits)


def vocab_ar_to_id(e: dict) -> Question:
    return Question(
        card_id=e["id"],
        mode="kosakata-ar",
        kind="typed",
        stage=e["stage"],
        question="Apa arti kata ini?",
        stimulus_ar=e["ar"],
        options=None,
        accepted=expand_accepted(e["gloss"], e.get("alt")),
        reveal=f"{e['gloss']}  ({_vocab_detail(e)})",
        reveal_ar=e["example"]["ar"],
        explain=f"{e['example']['ar']} = {e['example']['gloss']}",
    )


def accepted_set(entry: dict) -> frozenset[str]:
    """Himpunan jawaban yang diterima untuk satu entri, sudah dibakukan."""
    key = (entry["gloss"], tuple(entry.get("alt") or ()))
    cached = _ACCEPTED_CACHE.get(key)
    if cached is None:
        cached = frozenset(
            normalize(a) for a in expand_accepted(entry["gloss"], entry.get("alt"))
        )
        _ACCEPTED_CACHE[key] = cached
    return cached


def vocab_id_to_ar(e: dict, pool: list[dict], rng: random.Random) -> Question:
    # Pengecoh tidak boleh menerima teks pertanyaan sebagai jawabannya sendiri.
    # Tanpa saringan ini, pertanyaan "kata Arab untuk 'tahun'" bisa memuat
    # سَنَة dan عَام sekaligus, sehingga ada dua jawaban benar.
    prompt_key = normalize(e["gloss"])
    safe = [
        o for o in pool
        if o["id"] != e["id"] and prompt_key not in accepted_set(o)
    ]
    distractors = _pick_distractors(rng, safe, e, "ar", 3)
    options, answer = _shuffle_options(rng, e["ar"], distractors)
    return Question(
        card_id=e["id"],
        mode="kosakata-id",
        kind="mcq",
        stage=e["stage"],
        question=f"Mana kata Arab untuk ‘{e['gloss']}’?",
        stimulus_ar=None,
        options=options,
        options_lang="ar",
        answer=answer,
        reveal=f"{e['ar']} = {e['gloss']}  ({_vocab_detail(e)})",
        reveal_ar=e["example"]["ar"],
        explain=f"{e['example']['ar']} = {e['example']['gloss']}",
    )


# ------------------------------------------------------------ tata bahasa ---

def grammar_question(item: dict) -> Question:
    return Question(
        card_id=item["id"],
        mode="tatabahasa",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_ar=item.get("prompt_ar"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


# ------------------------------------------------------------------ akar ---

def root_question(item: dict) -> Question:
    return Question(
        card_id=item["id"],
        mode="akar",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_ar=item.get("prompt_ar"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


def root_of_word(family: dict, families: list[dict], rng: random.Random) -> Question:
    """Soal buatan: 'Apa akar kata ini?' Kunci diambil dari data keluarga akar."""
    member = rng.choice(family["members"])
    other_roots = [f["root"] for f in families if f["root"] != family["root"]]
    rng.shuffle(other_roots)
    options, answer = _shuffle_options(rng, family["root"], other_roots[:3])
    return Question(
        card_id=family["id"],
        mode="akar",
        kind="mcq",
        stage=family["stage"],
        question=f"Apa akar kata dari ‘{member['gloss']}’ berikut?",
        stimulus_ar=member["ar"],
        options=options,
        options_lang="ar",
        answer=answer,
        reveal=f"{family['root']} ({family['meaning']})",
        explain=(
            f"{member['ar']} berpola {member['pattern']} dari akar {family['root']} "
            f"yang bermakna ‘{family['meaning']}’."
        ),
    )


def odd_one_out(family: dict, families: list[dict], rng: random.Random) -> Question:
    """Soal buatan: 'Mana yang BUKAN dari akar ini?'."""
    members = [m["ar"] for m in family["members"]]
    rng.shuffle(members)
    keep = members[:3]
    outsiders = [
        m["ar"] for f in families if f["root"] != family["root"] for m in f["members"]
    ]
    outsider = rng.choice(outsiders)
    options = keep + [outsider]
    rng.shuffle(options)
    return Question(
        card_id=family["id"],
        mode="akar",
        kind="mcq",
        stage=family["stage"],
        question=f"Mana kata yang BUKAN dari akar {family['root']} ?",
        stimulus_ar=None,
        options=options,
        options_lang="ar",
        answer=options.index(outsider),
        reveal=outsider,
        explain=(
            f"Tiga kata lainnya berakar {family['root']} ({family['meaning']}). "
            f"{outsider} berakar lain."
        ),
    )


# ------------------------------------------------------------------ baca ---

def render_level(text: str, level: int, *, keep: set[int] | None = None,
                 blank: int | None = None) -> str:
    """Tampilkan teks pada level harakat tertentu.

    level 1: harakat penuh.
    level 2: harakat hanya pada kata yang indeksnya ada di `keep`; kata lain
        kehilangan harakat tetapi syaddahnya dipertahankan.
    level 3: tanpa harakat.
    `blank` adalah indeks kata yang SELALU dilepas harakatnya (kata yang
    ditanyakan), supaya jawabannya tidak terlihat.
    """
    words = text.split(" ")
    keep = keep if keep is not None else set()
    out: list[str] = []
    for i, w in enumerate(words):
        if blank is not None and i == blank:
            out.append(strip_harakat(w))
        elif level == 1:
            out.append(w)
        elif level == 2:
            out.append(w if i in keep else strip_harakat_keep_shadda(w))
        else:
            out.append(strip_harakat(w))
    return " ".join(out)


def target_word(full_ar: str, index: int) -> str:
    """Kata ke-`index` pada sebuah kalimat, tanpa tanda baca yang menempel."""
    word = full_ar.split(" ")[index]
    return "".join(ch for ch in word if ch not in PUNCT)


def reading_question(item: dict) -> Question:
    level = item["level"]
    if item["type"] == "harakat_choice":
        target = item["target"]
        shown = render_level(item["full_ar"], level, blank=target)
        bare = strip_harakat(target_word(item["full_ar"], target))
        glosses = item.get("option_glosses") or []
        explain = item.get("explain") or ""
        if glosses:
            detail = "; ".join(
                f"{o} = {g}" for o, g in zip(item["options"], glosses)
            )
            explain = f"{explain}\n   Semua pilihan: {detail}"
        return Question(
            card_id=item["id"],
            mode="baca",
            kind="mcq",
            stage=item["stage"],
            question="Bagaimana bacaan yang tepat untuk kata yang ditanyakan?",
            stimulus_ar=shown,
            stimulus_label=f"kata yang ditanyakan: {bare}",
            options=list(item["options"]),
            options_lang="ar",
            answer=item["answer"],
            reveal=f"{item['full_ar']} = {item['gloss']}",
            explain=explain,
        )
    if item["type"] == "meaning_choice":
        shown = render_level(item["full_ar"], level)
        return Question(
            card_id=item["id"],
            mode="baca",
            kind="mcq",
            stage=item["stage"],
            question="Apa arti kalimat tanpa harakat berikut?",
            stimulus_ar=shown,
            options=list(item["options"]),
            options_lang="id",
            answer=item["answer"],
            reveal=f"{item['full_ar']} = {item['gloss']}",
            explain=item.get("explain"),
        )
    raise ValueError(f"jenis soal baca tidak dikenal: {item['type']}")


def passage_question(p: dict) -> Question:
    shown = render_level(p["ar"], p["level"], keep=set(p.get("keep") or []))
    return Question(
        card_id=p["id"],
        mode="baca",
        kind="selfcheck",
        stage=p["stage"],
        question=(
            f"Bacalah dengan suara (Level {p['level']}), tentukan harakatnya, "
            "lalu bandingkan dengan jawabannya."
        ),
        stimulus_ar=shown,
        reveal=f"{p['ar']} = {p['gloss']}",
        reveal_ar=p["ar"],
        explain=None,
    )


def quran_question(item: dict) -> Question:
    return Question(
        card_id=item["id"],
        mode="tatabahasa",
        kind="mcq",
        stage=item["stage"],
        question=item["prompt"],
        stimulus_ar=item.get("prompt_ar"),
        options=list(item["options"]),
        options_lang=item["options_lang"],
        answer=item["answer"],
        reveal=item["options"][item["answer"]],
        explain=item.get("explain"),
    )


# -------------------------------------------------------------- kumpulan ---

def build_pool(mode: str, stage: int | None, rng: random.Random) -> list[Question]:
    """Bangun seluruh soal yang tersedia untuk satu mode."""
    if mode == "kosakata-ar":
        return [vocab_ar_to_id(e) for e in dataio.vocab_entries(stage)]
    if mode == "kosakata-id":
        pool = dataio.vocab_entries(stage)
        return [vocab_id_to_ar(e, pool, rng) for e in pool]
    if mode == "tatabahasa":
        qs = [grammar_question(i) for i in dataio.grammar_items(stage)]
        qs += [quran_question(i) for i in dataio.quran_items(stage)
               if stage is None or i["stage"] <= stage]
        return qs
    if mode == "akar":
        fams = dataio.root_families(stage)
        qs = [root_question(i) for i in dataio.root_items(stage)]
        if len(fams) >= 4:
            qs += [root_of_word(f, fams, rng) for f in fams]
            qs += [odd_one_out(f, fams, rng) for f in fams]
        return qs
    if mode == "baca":
        qs = [reading_question(i) for i in dataio.reading_items(stage)]
        qs += [passage_question(p) for p in dataio.reading_passages(stage)]
        return qs
    raise ValueError(f"mode tidak dikenal: {mode}")


__all__ = [
    "MODES",
    "MODE_LABELS",
    "Question",
    "accepted_set",
    "build_pool",
    "expand_accepted",
    "grammar_question",
    "normalize",
    "odd_one_out",
    "passage_question",
    "quran_question",
    "reading_question",
    "render_level",
    "root_of_word",
    "root_question",
    "target_word",
    "vocab_ar_to_id",
    "vocab_id_to_ar",
]
