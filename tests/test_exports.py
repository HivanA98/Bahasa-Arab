"""Pengujian ekspor: hasil di repositori harus sama dengan yang dihasilkan ulang.

Berkas di data/csv/, anki/, dan worksheets/ adalah TURUNAN dari data/*.json.
Pengujian ini membuat ulang semuanya ke folder sementara lalu membandingkannya
dengan yang tersimpan. Bila berbeda, berarti data sudah berubah tetapi
ekspornya belum dibuat ulang.
"""

from __future__ import annotations

import csv
import os

import pytest

from conftest import ROOT, load_tool

CSV_DIR = os.path.join(ROOT, "data", "csv")
ANKI_DIR = os.path.join(ROOT, "anki")
WS_DIR = os.path.join(ROOT, "worksheets")
KEY_DIR = os.path.join(WS_DIR, "answers")


def _regenerate_exports(tmp_path):
    mod = load_tool("build_exports")
    mod.CSV_DIR = str(tmp_path / "csv")
    mod.ANKI_DIR = str(tmp_path / "anki")
    mod.main()
    return str(tmp_path / "csv"), str(tmp_path / "anki")


def _regenerate_worksheets(tmp_path):
    mod = load_tool("build_worksheets")
    mod.WS_DIR = str(tmp_path / "ws")
    mod.KEY_DIR = str(tmp_path / "ws" / "answers")
    mod.main()
    return str(tmp_path / "ws"), str(tmp_path / "ws" / "answers")


def _compare_dirs(baru: str, lama: str, label: str) -> None:
    nama_baru = sorted(f for f in os.listdir(baru) if os.path.isfile(os.path.join(baru, f)))
    nama_lama = sorted(f for f in os.listdir(lama) if os.path.isfile(os.path.join(lama, f)))
    assert nama_baru == nama_lama, (
        f"{label}: daftar berkas berbeda.\nbaru: {nama_baru}\ntersimpan: {nama_lama}"
    )
    beda = []
    for nama in nama_baru:
        a = open(os.path.join(baru, nama), encoding="utf-8").read()
        b = open(os.path.join(lama, nama), encoding="utf-8").read()
        if a != b:
            beda.append(nama)
    assert not beda, (
        f"{label}: berkas berikut tidak mutakhir, jalankan ulang skripnya: {beda}"
    )


def test_ekspor_csv_mutakhir(tmp_path):
    csv_baru, anki_baru = _regenerate_exports(tmp_path)
    _compare_dirs(csv_baru, CSV_DIR, "data/csv")


def test_ekspor_anki_mutakhir(tmp_path):
    csv_baru, anki_baru = _regenerate_exports(tmp_path)
    nama = [f for f in os.listdir(ANKI_DIR) if f.endswith(".csv")]
    nama_baru = sorted(os.listdir(anki_baru))
    assert sorted(nama) == nama_baru
    beda = [
        n for n in nama_baru
        if open(os.path.join(anki_baru, n), encoding="utf-8").read()
        != open(os.path.join(ANKI_DIR, n), encoding="utf-8").read()
    ]
    assert not beda, f"anki/: tidak mutakhir, jalankan tools/build_exports.py: {beda}"


def test_lembar_kerja_mutakhir(tmp_path):
    ws_baru, key_baru = _regenerate_worksheets(tmp_path)
    nama_ws_baru = sorted(f for f in os.listdir(ws_baru) if f.endswith(".md"))
    nama_ws_lama = sorted(f for f in os.listdir(WS_DIR) if f.endswith(".md"))
    assert nama_ws_baru == nama_ws_lama
    beda = [
        n for n in nama_ws_baru
        if open(os.path.join(ws_baru, n), encoding="utf-8").read()
        != open(os.path.join(WS_DIR, n), encoding="utf-8").read()
    ]
    assert not beda, f"worksheets/: tidak mutakhir: {beda}"
    _compare_dirs(key_baru, KEY_DIR, "worksheets/answers")


# ----------------------------------------------- isi berkas hasil ekspor ---

def _read_csv(path: str) -> tuple[list[str], list[list[str]]]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


@pytest.mark.parametrize(
    "nama,modul",
    [
        ("vocab.csv", "vocab"),
        ("grammar_items.csv", "grammar"),
        ("reading_items.csv", "reading"),
    ],
)
def test_csv_punya_baris_judul_dan_isi(nama, modul):
    header, rows = _read_csv(os.path.join(CSV_DIR, nama))
    assert header and header[0] == "id"
    assert rows, f"{nama} kosong"
    assert all(len(r) == len(header) for r in rows), f"{nama}: jumlah kolom tidak rata"


def test_kolom_answer_text_sesuai_kunci():
    """Kolom answer_text pada CSV harus sama dengan options[answer]."""
    for nama in ("grammar_items.csv", "roots_items.csv", "reading_items.csv",
                 "quran_msa_items.csv"):
        header, rows = _read_csv(os.path.join(CSV_DIR, nama))
        i_opts = header.index("options")
        i_ans = header.index("answer")
        i_text = header.index("answer_text")
        for r in rows:
            opts = r[i_opts].split(" | ")
            assert r[i_text] == opts[int(r[i_ans])], f"{nama}: {r[0]} answer_text salah"


def test_csv_vocab_memuat_semua_entri():
    from arabdrill import dataio

    _header, rows = _read_csv(os.path.join(CSV_DIR, "vocab.csv"))
    assert len(rows) == len(dataio.vocab_entries())
    assert [r[0] for r in rows] == [e["id"] for e in dataio.vocab_entries()]


def test_anki_memakai_baris_pengarah_dan_tanpa_baris_judul():
    for nama in os.listdir(ANKI_DIR):
        if not nama.endswith(".csv"):
            continue
        baris = open(os.path.join(ANKI_DIR, nama), encoding="utf-8").read().splitlines()
        assert baris[0] == "#separator:Comma", f"{nama}: baris pengarah hilang"
        assert any(b.startswith("#tags column:") for b in baris[:4]), nama
        isi = [b for b in baris if not b.startswith("#")]
        assert isi, f"{nama} tidak punya kartu"
        assert not isi[0].startswith('"id"'), f"{nama}: Anki tidak memakai baris judul"


def test_anki_setiap_kartu_punya_sisi_depan_dan_belakang():
    for nama in os.listdir(ANKI_DIR):
        if not nama.endswith(".csv"):
            continue
        with open(os.path.join(ANKI_DIR, nama), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        for r in rows:
            assert r[0].strip(), f"{nama}: ada kartu tanpa sisi depan"
            assert r[1].strip(), f"{nama}: ada kartu tanpa sisi belakang"


def test_anki_jumlah_kolom_seragam_per_berkas():
    for nama in os.listdir(ANKI_DIR):
        if not nama.endswith(".csv"):
            continue
        with open(os.path.join(ANKI_DIR, nama), encoding="utf-8", newline="") as f:
            rows = [r for r in csv.reader(f) if r and not r[0].startswith("#")]
        lebar = {len(r) for r in rows}
        assert len(lebar) == 1, f"{nama}: jumlah kolom tidak seragam {lebar}"
