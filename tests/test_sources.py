"""Pengujian aturan sumber: tidak ada ayat Al-Qur'an yang ditulis dari ingatan.

Aturannya: data/ TIDAK boleh memuat kutipan ayat kecuali pengguna menyediakan
berkas teks mushaf di sources/ dan mencantumkan rujukan surah:ayat. Selama
sources/ masih kosong, setiap field quran_examples harus kosong.
"""

from __future__ import annotations

import json
import os
import re

from conftest import ROOT

from arabdrill import dataio

DATA_DIR = os.path.join(ROOT, "data")
RUJUKAN_AYAT = re.compile(r"\b\d{1,3}\s*:\s*\d{1,3}\b")


def test_folder_sources_ada_dan_berpenjelasan():
    readme = os.path.join(ROOT, "sources", "README.md")
    assert os.path.exists(readme), "sources/README.md harus ada"
    isi = open(readme, encoding="utf-8").read()
    assert "surah" in isi.lower()


def test_pernyataan_tanpa_teks_quran_ada_di_data():
    doc = dataio.load("quran_msa")
    assert "no_quran_text" in doc
    assert doc["no_quran_text"]["pernyataan"]
    assert doc["no_quran_text"]["cara_menambah"]


def test_quran_examples_kosong_selama_sources_kosong():
    berkas = dataio.source_files()
    kosong = not berkas
    terisi = [
        e["id"] for e in dataio.quran_entries() if e.get("quran_examples")
    ]
    if kosong:
        assert not terisi, (
            "sources/ masih kosong tetapi ada entri dengan quran_examples: "
            f"{terisi}. Sediakan berkas sumbernya lebih dahulu."
        )


def test_setiap_quran_example_menyebut_rujukan_surah_ayat():
    """Bila suatu saat ayat ditambahkan, rujukannya wajib ada."""
    problems = []
    for e in dataio.quran_entries():
        for ex in e.get("quran_examples") or []:
            teks = json.dumps(ex, ensure_ascii=False)
            if not RUJUKAN_AYAT.search(teks):
                problems.append(f"{e['id']}: contoh tanpa rujukan surah:ayat")
    assert not problems, "\n".join(problems)


def test_tidak_ada_rujukan_ayat_tersembunyi_di_modul_lain():
    """Modul selain Modul 5 tidak boleh memuat rujukan surah:ayat sama sekali."""
    problems = []
    for name in ("vocab", "grammar", "roots", "reading"):
        raw = json.dumps(dataio.load(name), ensure_ascii=False)
        for m in RUJUKAN_AYAT.finditer(raw):
            problems.append(f"{name}: menyerupai rujukan ayat: {m.group(0)!r}")
    assert not problems, "\n".join(problems)


def test_needs_review_ada_dan_tidak_kosong():
    path = os.path.join(DATA_DIR, "NEEDS_REVIEW.md")
    assert os.path.exists(path), "data/NEEDS_REVIEW.md harus ada"
    isi = open(path, encoding="utf-8").read().strip()
    assert len(isi) > 200, "NEEDS_REVIEW.md terlalu pendek untuk bermakna"


def test_setiap_root_null_dijelaskan():
    """Akar yang dikosongkan harus punya alasan, bukan dibiarkan tanpa kabar."""
    problems = []
    for e in dataio.vocab_entries():
        if e.get("root") is None and e["pos"] in ("ism", "fi'l", "sifah", "adad"):
            if not e.get("root_note"):
                problems.append(
                    f"{e['id']} {e['ar']}: root null tanpa root_note"
                )
    assert not problems, "\n".join(problems)


def test_entri_yang_tercatat_di_needs_review_konsisten():
    """Setiap id kosakata yang disebut di NEEDS_REVIEW.md harus benar-benar ada."""
    isi = open(os.path.join(DATA_DIR, "NEEDS_REVIEW.md"), encoding="utf-8").read()
    ids_ada = {e["id"] for e in dataio.vocab_entries()}
    ids_ada |= {i["id"] for i in dataio.quran_items()}
    ids_ada |= {e["id"] for e in dataio.quran_entries()}
    ids_ada |= {f["id"] for f in dataio.root_families()}
    disebut = set(re.findall(r"\b(?:v\d{3}|q\d{2}|r\d{2})\b", isi))
    hilang = sorted(disebut - ids_ada)
    assert not hilang, f"NEEDS_REVIEW.md menyebut id yang tidak ada: {hilang}"
