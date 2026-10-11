"""Pengujian Unicode Arab dan kelengkapan harakat pada seluruh data.

Yang diuji di sini bersifat ORTOGRAFIS: karakter yang dipakai, bentuk NFC,
dan apakah setiap huruf memikul tanda yang semestinya. Kebenaran ISI (arti,
gender, jamak, kesesuaian akar dengan makna) tidak bisa diuji mesin.
"""

from __future__ import annotations

from arabdrill import dataio
from arabdrill.arabic import (
    LETTERS,
    MARKS,
    TATWEEL,
    is_nfc,
    letter_units,
    nfc,
    partial_harakat,
    strip_harakat,
    strip_harakat_keep_shadda,
    validate_root,
    validate_vocalization,
)


def _lemma_fields():
    """(label, teks) untuk setiap field yang ditulis dalam bentuk waqf."""
    for e in dataio.vocab_entries():
        for field in ("ar", "plural", "fem", "mudhari"):
            if e.get(field):
                yield f"vocab {e['id']}.{field}", e[field]
    for fam in dataio.root_families():
        for m in fam["members"]:
            yield f"roots {fam['id']} {m['ar']}", m["ar"]
    for p in dataio.root_patterns():
        yield f"pattern {p['id']}", p["pattern"]
        for v in p.get("variants") or []:
            yield f"pattern {p['id']} varian", v
        for x in p["examples"]:
            yield f"pattern {p['id']} contoh", x["ar"]
    for e in dataio.quran_entries():
        yield f"quran {e['id']}.ar", e["ar"]


def _sentence_fields():
    """(label, teks) untuk setiap field yang ditulis berharakat penuh."""
    for e in dataio.vocab_entries():
        yield f"vocab {e['id']}.example", e["example"]["ar"]
    for t in dataio.grammar_topics():
        for x in t["examples"]:
            yield f"grammar {t['id']}.example", x["ar"]
    for p in dataio.reading_passages():
        yield f"reading {p['id']}.ar", p["ar"]
    for i in dataio.reading_items():
        yield f"reading {i['id']}.full_ar", i["full_ar"]


def _option_fields():
    """Pilihan jawaban berbahasa Arab: aturan lema, tetapi boleh berupa frasa."""
    sources = (
        dataio.grammar_items(), dataio.root_items(),
        dataio.reading_items(), dataio.quran_items(),
    )
    for group in sources:
        for item in group:
            if item.get("prompt_ar"):
                # prompt_ar satu kata adalah kutipan lema (bentuk waqf);
                # yang lebih dari satu kata adalah kalimat berharakat penuh.
                mode = "lemma" if " " not in item["prompt_ar"].strip() else "sentence"
                yield f"{item['id']}.prompt_ar", item["prompt_ar"], mode
            if item["options_lang"] == "ar":
                for o in item["options"]:
                    yield f"{item['id']} pilihan", o, "lemma"


def _all_arabic_strings():
    for label, text in _lemma_fields():
        yield label, text
    for label, text in _sentence_fields():
        yield label, text
    for label, text, _mode in _option_fields():
        yield label, text


def test_semua_teks_arab_berbentuk_nfc():
    salah = [label for label, text in _all_arabic_strings() if not is_nfc(text)]
    assert not salah, f"teks belum NFC: {salah}"


def test_tidak_ada_tatwil():
    salah = [label for label, text in _all_arabic_strings() if TATWEEL in text]
    assert not salah, f"memakai tatwil U+0640: {salah}"


def test_tidak_ada_huruf_latin_di_field_arab():
    problems = []
    for label, text in _all_arabic_strings():
        asing = {ch for ch in text if ch.isalpha() and ch not in LETTERS}
        if asing:
            problems.append(f"{label}: huruf non-Arab {sorted(asing)}")
    assert not problems, "\n".join(problems)


def test_harakat_lengkap_pada_lema():
    problems = []
    for label, text in _lemma_fields():
        for p in validate_vocalization(text, mode="lemma"):
            problems.append(f"{label}: {p}")
    assert not problems, "\n".join(problems)


def test_harakat_lengkap_pada_kalimat():
    problems = []
    for label, text in _sentence_fields():
        for p in validate_vocalization(text, mode="sentence"):
            problems.append(f"{label}: {p}")
    assert not problems, "\n".join(problems)


def test_harakat_lengkap_pada_pilihan_jawaban():
    problems = []
    for label, text, mode in _option_fields():
        for p in validate_vocalization(text, mode=mode, allow_punct=True):
            problems.append(f"{label}: {p}")
    assert not problems, "\n".join(problems)


def test_format_akar_kata():
    problems = []
    for e in dataio.vocab_entries():
        if e.get("root"):
            for p in validate_root(e["root"]):
                problems.append(f"vocab {e['id']}: {p}")
    for fam in dataio.root_families():
        for p in validate_root(fam["root"]):
            problems.append(f"roots {fam['id']}: {p}")
    for pat in dataio.root_patterns():
        for x in pat["examples"]:
            for p in validate_root(x["root"]):
                problems.append(f"pattern {pat['id']}: {p}")
    for e in dataio.quran_entries():
        if e.get("root"):
            for p in validate_root(e["root"]):
                problems.append(f"quran {e['id']}: {p}")
    assert not problems, "\n".join(problems)


# ----------------------------------------------- pengujian fungsi bantu ---

def test_strip_harakat_membuang_semua_tanda():
    for _label, text in _all_arabic_strings():
        bare = strip_harakat(text)
        assert not (set(bare) & MARKS), f"masih ada tanda pada {bare!r}"


def test_strip_harakat_mempertahankan_huruf():
    for _label, text in _all_arabic_strings():
        huruf_asli = [ch for ch in nfc(text) if ch in LETTERS]
        huruf_hasil = [ch for ch in strip_harakat(text) if ch in LETTERS]
        assert huruf_asli == huruf_hasil


def test_strip_harakat_keep_shadda():
    teks = "الطَّالِبُ"  # الطَّالِبُ
    hasil = strip_harakat_keep_shadda(teks)
    assert "ّ" in hasil
    assert "َ" not in hasil and "ُ" not in hasil


def test_partial_harakat_hanya_mempertahankan_kata_terpilih():
    for p in dataio.reading_passages():
        keep = set(p.get("keep") or [])
        hasil = partial_harakat(p["ar"], keep).split(" ")
        asli = p["ar"].split(" ")
        for i, (a, h) in enumerate(zip(asli, hasil)):
            if i in keep:
                assert h == a, f"{p['id']} kata {i} seharusnya utuh"
            else:
                assert h == strip_harakat_keep_shadda(a), f"{p['id']} kata {i}"


def test_letter_units_memetakan_tanda_ke_huruf_sebelumnya():
    # كَتَبَ: tiga huruf, masing-masing satu fathah.
    units = letter_units("كَتَبَ")
    assert [u[0] for u in units] == ["ك", "ت", "ب"]
    assert all(u[1] == ["َ"] for u in units)


def test_validator_menolak_huruf_tanpa_harakat_di_tengah():
    # كتَبَ: kaf tanpa harakat, seharusnya ditolak.
    problems = validate_vocalization("كتَبَ", mode="sentence")
    assert problems


def test_validator_menolak_tatwil():
    assert validate_vocalization("كَـتَبَ")


def test_validator_menerima_alif_tanpa_harakat():
    # كِتَاب dalam bentuk waqf: alif memang tidak memikul harakat.
    assert not validate_vocalization(
        "كِتَاب", mode="lemma"
    )


def test_validator_menerima_lam_syamsiyah_tanpa_tanda():
    # الطَّالِبُ: lam pada ال tidak diberi tanda karena ط bersyaddah.
    teks = "الطَّالِبُ"
    assert not validate_vocalization(teks, mode="sentence")


def test_validator_menolak_syaddah_tanpa_vokal_di_tengah_kalimat():
    # الطَّالِبُ tanpa fathah pada ط.
    teks = "الطّالِبُ"
    assert validate_vocalization(teks, mode="sentence")
