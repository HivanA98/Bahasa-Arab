"""Pengujian lembar kerja: kunci terpisah, lengkap, dan sesuai data."""

from __future__ import annotations

import os
import re

from conftest import ROOT

from arabdrill import dataio
from arabdrill.arabic import MARKS, strip_harakat

WS_DIR = os.path.join(ROOT, "worksheets")
KEY_DIR = os.path.join(WS_DIR, "answers")
BAGIAN = ("## A.", "## B.", "## C.", "## D.", "## E.")


def _ws_files() -> list[str]:
    return sorted(f for f in os.listdir(WS_DIR) if re.match(r"^ws-\d{2}\.md$", f))


def _read(path: str) -> str:
    return open(path, encoding="utf-8").read()


def test_ada_dua_belas_lembar_kerja():
    assert len(_ws_files()) == 12


def test_setiap_lembar_punya_kunci():
    for nama in _ws_files():
        tag = nama[:-3]
        kunci = os.path.join(KEY_DIR, f"{tag}-kunci.md")
        assert os.path.exists(kunci), f"kunci untuk {nama} tidak ada"


def test_kunci_berada_di_berkas_terpisah():
    """Lembar kerja tidak boleh memuat kuncinya sendiri."""
    for nama in _ws_files():
        isi = _read(os.path.join(WS_DIR, nama))
        assert "Kunci jawaban ·" not in isi
        assert "## A. Arti kata" not in isi, f"{nama} memuat tabel kunci"


def test_setiap_lembar_punya_semua_bagian():
    for nama in _ws_files():
        isi = _read(os.path.join(WS_DIR, nama))
        for b in BAGIAN:
            assert b in isi, f"{nama} tidak punya bagian {b}"


def test_setiap_kunci_punya_semua_bagian():
    for nama in _ws_files():
        tag = nama[:-3]
        isi = _read(os.path.join(KEY_DIR, f"{tag}-kunci.md"))
        for b in BAGIAN:
            assert b in isi, f"{tag}-kunci.md tidak punya bagian {b}"


def test_bagian_e_lembar_kerja_tanpa_harakat():
    """Soal membaca harus disajikan tanpa harakat; kalau tidak, bukan latihan."""
    for nama in _ws_files():
        isi = _read(os.path.join(WS_DIR, nama))
        bagian_e = isi.split("## E.")[1].split("---")[0]
        baris_soal = [
            b for b in bagian_e.splitlines()
            if re.match(r"^\d+\. ", b.strip())
        ]
        assert baris_soal, f"{nama}: bagian E tidak punya soal"
        for b in baris_soal:
            tersisa = set(b) & MARKS
            assert not tersisa, f"{nama}: soal bagian E masih berharakat: {b!r}"


def test_bagian_e_kunci_berharakat_penuh():
    for nama in _ws_files():
        tag = nama[:-3]
        isi = _read(os.path.join(KEY_DIR, f"{tag}-kunci.md"))
        bagian_e = isi.split("## E.")[1]
        baris = [b for b in bagian_e.splitlines() if re.match(r"^\d+\. ", b.strip())]
        assert baris, f"{tag}: kunci bagian E kosong"
        for b in baris:
            assert set(b) & MARKS, f"{tag}: kunci bagian E tidak berharakat: {b!r}"


def test_kalimat_bagian_e_berasal_dari_data():
    """Setiap kalimat pada kunci bagian E harus ada di data/reading.json."""
    sah = {i["full_ar"] for i in dataio.reading_items()}
    for nama in _ws_files():
        tag = nama[:-3]
        isi = _read(os.path.join(KEY_DIR, f"{tag}-kunci.md"))
        bagian_e = isi.split("## E.")[1]
        for b in bagian_e.splitlines():
            m = re.match(r"^\d+\. (.+)$", b.strip())
            if m:
                assert m.group(1) in sah, f"{tag}: kalimat tidak ada di data: {m.group(1)}"


def test_soal_dan_kunci_bagian_e_sejalan():
    """Kalimat tanpa harakat pada soal harus merupakan rangka dari kunci."""
    for nama in _ws_files():
        tag = nama[:-3]
        soal = _read(os.path.join(WS_DIR, nama)).split("## E.")[1].split("---")[0]
        kunci = _read(os.path.join(KEY_DIR, f"{tag}-kunci.md")).split("## E.")[1]
        s = [re.match(r"^\d+\. (.+?)\s{2,}\(", b.strip()).group(1)
             for b in soal.splitlines() if re.match(r"^\d+\. ", b.strip())]
        k = [re.match(r"^\d+\. (.+)$", b.strip()).group(1)
             for b in kunci.splitlines() if re.match(r"^\d+\. ", b.strip())]
        assert len(s) == len(k), f"{tag}: jumlah soal dan kunci bagian E berbeda"
        for a, b in zip(s, k):
            assert a == strip_harakat(b), f"{tag}: soal {a!r} bukan rangka dari {b!r}"


def test_kunci_bagian_c_menyebut_huruf_pilihan():
    for nama in _ws_files():
        tag = nama[:-3]
        isi = _read(os.path.join(KEY_DIR, f"{tag}-kunci.md"))
        bagian_c = isi.split("## C.")[1].split("## D.")[0]
        huruf = re.findall(r"^\d+\. \*\*([a-d])\*\*", bagian_c, flags=re.M)
        assert len(huruf) == 5, f"{tag}: kunci bagian C ada {len(huruf)}, seharusnya 5"


def test_kata_pada_bagian_a_berasal_dari_data():
    sah = {e["ar"] for e in dataio.vocab_entries()}
    for nama in _ws_files():
        isi = _read(os.path.join(WS_DIR, nama))
        bagian_a = isi.split("## A.")[1].split("## B.")[0]
        for b in bagian_a.splitlines():
            m = re.match(r"^\| \d+ \| (.+?) \|", b)
            if m:
                assert m.group(1) in sah, f"{nama}: kata tidak ada di data: {m.group(1)}"


def test_kunci_bagian_a_sesuai_arti_di_data():
    arti = {e["ar"]: e["gloss"] for e in dataio.vocab_entries()}
    for nama in _ws_files():
        tag = nama[:-3]
        isi = _read(os.path.join(KEY_DIR, f"{tag}-kunci.md"))
        bagian_a = isi.split("## A.")[1].split("## B.")[0]
        for b in bagian_a.splitlines():
            m = re.match(r"^\| \d+ \| (.+?) \| (.+?) \|", b)
            if m:
                kata, jawab = m.group(1), m.group(2)
                assert arti.get(kata) == jawab, (
                    f"{tag}: arti {kata} tertulis {jawab!r}, "
                    f"di data {arti.get(kata)!r}"
                )


def test_kunci_bagian_d_sesuai_akar_di_data():
    akar = {
        m["ar"]: fam["root"]
        for fam in dataio.root_families()
        for m in fam["members"]
    }
    for nama in _ws_files():
        tag = nama[:-3]
        isi = _read(os.path.join(KEY_DIR, f"{tag}-kunci.md"))
        bagian_d = isi.split("## D.")[1].split("## E.")[0]
        baris = 0
        for b in bagian_d.splitlines():
            m = re.match(r"^\| \d+ \| (.+?) \| (.+?) \|", b)
            if m:
                baris += 1
                assert akar.get(m.group(1)) == m.group(2), (
                    f"{tag}: akar {m.group(1)} tertulis {m.group(2)!r}"
                )
        assert baris > 0, f"{tag}: kunci bagian D kosong"


def test_ada_daftar_isi_lembar_kerja():
    isi = _read(os.path.join(WS_DIR, "README.md"))
    for nama in _ws_files():
        assert nama in isi, f"{nama} tidak tercantum di worksheets/README.md"
