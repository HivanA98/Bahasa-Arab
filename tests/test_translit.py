"""Pengujian transliterasi opsional.

Transliterasi mengikuti TULISAN, bukan lafal: هَذَا menjadi "hadha" dengan alif
panjang hanya pada suku yang alifnya ditulis. Pengujian ini mematok perilaku
itu supaya tidak berubah tanpa sengaja.
"""

from __future__ import annotations

import pytest

from arabdrill import dataio
from arabdrill.translit import translit

KASUS = [
    ("كِتَاب", "kitāb"),                    # كِتَاب
    ("الْكِتَابُ", "al-kitābu"),  # الْكِتَابُ
    ("الرَّجُلُ", "ar-rajulu"),   # الرَّجُلُ
    ("مُدَرِّس", "mudarris"),          # مُدَرِّس
    ("بَيْت", "bayt"),                                # بَيْت
    ("يَوْم", "yawm"),                                # يَوْم
    ("سُوق", "sūq"),                                  # سُوق
    ("فِي", "fī"),                                         # فِي
    ("مَدْرَسَة", "madrasah"),    # مَدْرَسَة
    ("مَدْرَسَةٌ", "madrasatun"),  # مَدْرَسَةٌ
    ("كِتَابًا", "kitāban"),      # كِتَابًا
    ("غَدًا", "ghadan"),                              # غَدًا
    ("كَتَبُوا", "katabū"),       # كَتَبُوا
    ("اِسْم", "ism"),                                 # اِسْم
    ("مَاء", "māʾ"),                             # مَاء
    ("حَارّ", "ḥārr"),                      # حَارّ
]


@pytest.mark.parametrize("arab,latin", KASUS)
def test_kasus_yang_dipatok(arab, latin):
    assert translit(arab) == latin


def test_lam_syamsiyah_dileburkan():
    # الطَّالِبُ -> at-talibu dengan ta' tebal
    hasil = translit("الطَّالِبُ")
    assert hasil == "aṭ-ṭālibu"


def test_lam_qamariyah_tetap_dibaca():
    assert translit("الْكِتَابُ").startswith("al-")


def test_spasi_dan_tanda_baca_diteruskan():
    hasil = translit("الْبَيْتُ "
                     "كَبِيرٌ.")
    assert hasil == "al-baytu kabīrun."


def test_tidak_meninggalkan_huruf_arab():
    """Setiap teks Arab pada data harus habis dialihhurufkan."""
    from arabdrill.arabic import LETTERS, MARKS

    sisa = []
    for e in dataio.vocab_entries():
        for teks in (e["ar"], e["example"]["ar"]):
            hasil = translit(teks)
            tertinggal = {c for c in hasil if c in LETTERS or c in MARKS}
            if tertinggal:
                sisa.append(f"{e['id']}: {sorted(tertinggal)}")
    assert not sisa, "\n".join(sisa)


def test_bersifat_deterministik():
    for e in dataio.vocab_entries()[:30]:
        assert translit(e["ar"]) == translit(e["ar"])


def test_tidak_pernah_mengembalikan_teks_kosong():
    kosong = [e["id"] for e in dataio.vocab_entries() if not translit(e["ar"]).strip()]
    assert not kosong, f"transliterasi kosong: {kosong}"
