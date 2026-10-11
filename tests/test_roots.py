"""Pengujian kesesuaian akar kata dengan kata turunannya.

Aturannya (lihat arabdrill/arabic.py):

* Akar sehat (tanpa huruf lemah dan bukan mudha'af): SEMUA huruf akar harus
  muncul berurutan pada rangka huruf kata.
* Akar lemah atau mudha'af: huruf yang luruh di permukaan adalah hal biasa
  (كَانَ dari ك و ن), sehingga cukup sebagian besar hurufnya.
* Kata yang tetap tidak lolos WAJIB punya penjelasan di field root_note.
  Dengan begitu pengecualian tercatat, bukan dibiarkan lewat diam-diam.
"""

from __future__ import annotations

from arabdrill import dataio
from arabdrill.arabic import (
    root_is_weak,
    root_letters_found,
    root_matches,
)


def test_akar_kosakata_cocok_dengan_kata():
    problems = []
    for e in dataio.vocab_entries():
        root = e.get("root")
        if not root:
            continue
        if not root_matches(root, e["ar"]):
            if not e.get("root_note"):
                problems.append(
                    f"{e['id']} {e['ar']}: akar {root} tidak cocok "
                    f"(ditemukan {root_letters_found(root, e['ar'])} huruf) "
                    "dan tidak ada root_note"
                )
    assert not problems, "\n".join(problems)


def test_pengecualian_akar_tercatat():
    """Setiap ketidakcocokan akar harus punya catatan, dan jumlahnya sedikit."""
    pengecualian = [
        e["id"] for e in dataio.vocab_entries()
        if e.get("root") and not root_matches(e["root"], e["ar"])
    ]
    for cid in pengecualian:
        e = next(x for x in dataio.vocab_entries() if x["id"] == cid)
        assert e.get("root_note"), f"{cid} tanpa root_note"
    assert len(pengecualian) <= 5, (
        f"terlalu banyak pengecualian akar ({len(pengecualian)}): {pengecualian}"
    )


def test_anggota_keluarga_akar_cocok():
    problems = []
    for fam in dataio.root_families():
        for m in fam["members"]:
            if not root_matches(fam["root"], m["ar"]):
                problems.append(
                    f"{fam['id']} {m['ar']}: tidak cocok dengan akar {fam['root']}"
                )
    assert not problems, "\n".join(problems)


def test_contoh_pola_cocok_dengan_akarnya():
    problems = []
    for p in dataio.root_patterns():
        for x in p["examples"]:
            if not root_matches(x["root"], x["ar"]):
                problems.append(
                    f"{p['id']} {x['ar']}: tidak cocok dengan akar {x['root']}"
                )
    assert not problems, "\n".join(problems)


def test_akar_quran_msa_cocok():
    problems = []
    for e in dataio.quran_entries():
        if e.get("root") and not root_matches(e["root"], e["ar"]):
            problems.append(f"{e['id']} {e['ar']}: tidak cocok dengan akar {e['root']}")
    assert not problems, "\n".join(problems)


def test_kata_dalam_keluarga_akar_tidak_ganda():
    problems = []
    for fam in dataio.root_families():
        kata = [m["ar"] for m in fam["members"]]
        ganda = sorted({k for k in kata if kata.count(k) > 1})
        if ganda:
            problems.append(f"{fam['id']}: kata ganda {ganda}")
    assert not problems, "\n".join(problems)


def test_satu_kata_tidak_diklaim_dua_akar_berbeda():
    """Kata yang sama tidak boleh terdaftar pada dua keluarga akar berbeda."""
    pemilik: dict[str, str] = {}
    problems = []
    for fam in dataio.root_families():
        for m in fam["members"]:
            lain = pemilik.get(m["ar"])
            if lain and lain != fam["root"]:
                problems.append(f"{m['ar']} diklaim akar {lain} dan {fam['root']}")
            pemilik[m["ar"]] = fam["root"]
    assert not problems, "\n".join(problems)


def test_akar_kosakata_sejalan_dengan_keluarga_akar():
    """Bila sebuah kata ada di kedua modul, akarnya harus sama."""
    dari_keluarga = {
        m["ar"]: fam["root"]
        for fam in dataio.root_families()
        for m in fam["members"]
    }
    problems = []
    for e in dataio.vocab_entries():
        if e.get("root") and e["ar"] in dari_keluarga:
            if dari_keluarga[e["ar"]] != e["root"]:
                problems.append(
                    f"{e['id']} {e['ar']}: vocab.json menyebut {e['root']}, "
                    f"roots.json menyebut {dari_keluarga[e['ar']]}"
                )
    assert not problems, "\n".join(problems)


# -------------------------------------------- pengujian fungsi pencocok ---

def test_root_is_weak():
    assert root_is_weak("ك و ن")       # ك و ن, ada waw
    assert root_is_weak("ح ر ر")       # ح ر ر, mudha'af
    assert root_is_weak("ق ر أ")       # ق ر أ, ada hamzah
    assert not root_is_weak("ك ت ب")   # ك ت ب, sehat


def test_root_matches_akar_sehat():
    assert root_matches("ك ت ب", "مَكْتَب")  # مَكْتَب
    assert not root_matches("ك ت ب", "كَبِير")  # كَبِير


def test_root_matches_akar_lemah():
    # كَانَ dari ك و ن: waw tidak muncul di permukaan, tetap dianggap cocok.
    assert root_matches("ك و ن", "كَانَ")


def test_pencarian_huruf_akar_tidak_memakan_sisa_kata():
    # خَال dari خ و ل: waw tidak ada, tetapi lam harus tetap ditemukan.
    assert root_letters_found("خ و ل", "خَال") == 2
