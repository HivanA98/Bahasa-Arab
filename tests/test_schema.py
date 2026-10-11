"""Pengujian skema data: id unik, tidak ada field kosong, nilai sah."""

from __future__ import annotations

import re

import pytest

from arabdrill import dataio

ID_PATTERNS = {
    "vocab": re.compile(r"^v\d{3}$"),
    "grammar_topic": re.compile(r"^g\d{2}$"),
    "grammar_item": re.compile(r"^g\d{2}-\d{2}$"),
    "root_family": re.compile(r"^r\d{2}$"),
    "root_pattern": re.compile(r"^w\d{2}$"),
    "root_item": re.compile(r"^r-q\d{2}$"),
    "reading_passage": re.compile(r"^rp\d{2}$"),
    "reading_item": re.compile(r"^rd-(q|m)\d{2}$"),
    "quran_entry": re.compile(r"^q\d{2}$"),
    "quran_item": re.compile(r"^q-q\d{2}$"),
}

#: Field yang boleh bernilai null. Field lain tidak boleh null MAUPUN kosong.
NULLABLE = {
    "gender", "fem", "plural", "mudhari", "root", "root_note", "note",
    "prompt_ar", "target", "option_glosses", "variants", "quran_examples",
    "explain", "caveats", "keep", "alt",
}


def _check_no_empty(obj, where: str, problems: list[str]) -> None:
    """Rekursif: tolak string kosong dan nilai null pada field wajib."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if v is None and k not in NULLABLE:
                problems.append(f"{where}.{k} bernilai null")
            elif isinstance(v, str) and not v.strip() and k not in NULLABLE:
                problems.append(f"{where}.{k} berupa teks kosong")
            else:
                _check_no_empty(v, f"{where}.{k}", problems)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and not v.strip():
                problems.append(f"{where}[{i}] berupa teks kosong")
            else:
                _check_no_empty(v, f"{where}[{i}]", problems)


def test_semua_id_unik_di_seluruh_modul():
    ids = dataio.all_card_ids()
    ids += [t["id"] for t in dataio.grammar_topics()]
    ids += [p["id"] for p in dataio.root_patterns()]
    ids += [e["id"] for e in dataio.quran_entries()]
    duplikat = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplikat, f"id ganda: {duplikat}"


@pytest.mark.parametrize(
    "kind,items",
    [
        ("vocab", dataio.vocab_entries()),
        ("grammar_topic", dataio.grammar_topics()),
        ("grammar_item", dataio.grammar_items()),
        ("root_family", dataio.root_families()),
        ("root_pattern", dataio.root_patterns()),
        ("root_item", dataio.root_items()),
        ("reading_passage", dataio.reading_passages()),
        ("reading_item", dataio.reading_items()),
        ("quran_entry", dataio.quran_entries()),
        ("quran_item", dataio.quran_items()),
    ],
)
def test_format_id(kind, items):
    pola = ID_PATTERNS[kind]
    salah = [i["id"] for i in items if not pola.match(i["id"])]
    assert not salah, f"{kind}: id tidak sesuai pola {pola.pattern}: {salah}"


def test_tidak_ada_field_kosong():
    problems: list[str] = []
    for name in dataio.MODULE_FILES:
        _check_no_empty(dataio.load(name), name, problems)
    assert not problems, "\n".join(problems)


def test_kosakata_nilai_sah():
    problems: list[str] = []
    for e in dataio.vocab_entries():
        if e["pos"] not in dataio.POS_VALUES:
            problems.append(f"{e['id']}: pos tidak dikenal: {e['pos']}")
        if e["gender"] not in dataio.GENDER_VALUES:
            problems.append(f"{e['id']}: gender tidak dikenal: {e['gender']}")
        if not 1 <= e["stage"] <= dataio.MAX_STAGE:
            problems.append(f"{e['id']}: stage di luar 1-{dataio.MAX_STAGE}")
        if not isinstance(e["alt"], list):
            problems.append(f"{e['id']}: alt bukan daftar")
        for field in ("ar", "gloss", "pos", "cat"):
            if not e.get(field):
                problems.append(f"{e['id']}: {field} wajib ada")
        if not e["example"].get("ar") or not e["example"].get("gloss"):
            problems.append(f"{e['id']}: contoh kalimat tidak lengkap")
    assert not problems, "\n".join(problems)


def test_kata_benda_wajib_bergender():
    kurang = [e["id"] for e in dataio.vocab_entries()
              if e["pos"] == "ism" and not e["gender"]]
    assert not kurang, f"pos=ism tanpa gender: {kurang}"


def test_kata_kerja_wajib_punya_mudhari():
    kurang = [e["id"] for e in dataio.vocab_entries()
              if e["pos"] == "fi'l" and not e["mudhari"]]
    assert not kurang, f"pos=fi'l tanpa mudhari': {kurang}"


def test_hanya_kata_kerja_punya_mudhari():
    salah = [e["id"] for e in dataio.vocab_entries()
             if e["pos"] != "fi'l" and e["mudhari"]]
    assert not salah, f"mudhari' pada kelas kata bukan fi'l: {salah}"


def test_tahap_terisi_merata():
    """Setiap tahap 1-6 harus punya materi kosakata, supaya jadwal tidak bolong."""
    per_stage = {s: 0 for s in range(1, dataio.MAX_STAGE + 1)}
    for e in dataio.vocab_entries():
        per_stage[e["stage"]] += 1
    kosong = [s for s, n in per_stage.items() if n == 0]
    assert not kosong, f"tahap tanpa kosakata: {kosong}"


def test_tahap_topik_tata_bahasa_sah():
    salah = [t["id"] for t in dataio.grammar_topics()
             if not 1 <= t["stage"] <= dataio.MAX_STAGE]
    assert not salah, f"stage topik di luar jangkauan: {salah}"


def test_level_baca_sah():
    salah = [p["id"] for p in dataio.reading_passages() if p["level"] not in (1, 2, 3)]
    salah += [i["id"] for i in dataio.reading_items() if i["level"] not in (1, 2, 3)]
    assert not salah, f"level di luar 1-3: {salah}"


def test_setiap_level_baca_ada_isinya():
    for level in (1, 2, 3):
        assert dataio.reading_passages(level=level), f"tidak ada teks untuk level {level}"


def test_indeks_keep_dalam_jangkauan():
    problems = []
    for p in dataio.reading_passages():
        n = len(p["ar"].split(" "))
        for i in p.get("keep") or []:
            if not 0 <= i < n:
                problems.append(f"{p['id']}: keep={i} di luar 0-{n - 1}")
    assert not problems, "\n".join(problems)
