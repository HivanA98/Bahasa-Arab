"""Pengujian kunci jawaban: tepat satu jawaban benar, dan kunci sesuai data."""

from __future__ import annotations

import random

import pytest

from arabdrill import dataio
from arabdrill.arabic import strip_harakat
from arabdrill.questions import (
    MODES,
    accepted_set,
    build_pool,
    normalize,
    odd_one_out,
    root_of_word,
    target_word,
    vocab_id_to_ar,
)

SEEDS = (0, 1, 2, 7, 42)


def _all_mcq_items():
    for group, label in (
        (dataio.grammar_items(), "grammar"),
        (dataio.root_items(), "roots"),
        (dataio.reading_items(), "reading"),
        (dataio.quran_items(), "quran"),
    ):
        for item in group:
            yield label, item


def test_indeks_jawaban_dalam_jangkauan():
    problems = []
    for label, item in _all_mcq_items():
        if not 0 <= item["answer"] < len(item["options"]):
            problems.append(f"{label} {item['id']}: answer di luar jangkauan")
    assert not problems, "\n".join(problems)


def test_pilihan_jawaban_tidak_ganda():
    """Pilihan ganda identik akan membuat dua jawaban sama-sama benar."""
    problems = []
    for label, item in _all_mcq_items():
        opts = item["options"]
        ganda = sorted({o for o in opts if opts.count(o) > 1})
        if ganda:
            problems.append(f"{label} {item['id']}: pilihan ganda {ganda}")
    assert not problems, "\n".join(problems)


def test_jumlah_pilihan_memadai():
    problems = []
    for label, item in _all_mcq_items():
        if len(item["options"]) < 3:
            problems.append(f"{label} {item['id']}: hanya {len(item['options'])} pilihan")
    assert not problems, "\n".join(problems)


def test_options_lang_sah():
    problems = []
    for label, item in _all_mcq_items():
        if item["options_lang"] not in ("ar", "id"):
            problems.append(f"{label} {item['id']}: options_lang={item['options_lang']}")
    assert not problems, "\n".join(problems)


def test_jumlah_option_glosses_sesuai():
    problems = []
    for label, item in _all_mcq_items():
        g = item.get("option_glosses")
        if g and len(g) != len(item["options"]):
            problems.append(f"{label} {item['id']}: jumlah option_glosses tidak cocok")
    assert not problems, "\n".join(problems)


# ----------------------------------------------- modul baca tanpa harakat ---

def test_kunci_baca_sama_dengan_kata_pada_kalimat():
    """options[answer] WAJIB sama dengan kata ke-target pada full_ar."""
    problems = []
    for item in dataio.reading_items():
        if item["type"] != "harakat_choice":
            continue
        kata = target_word(item["full_ar"], item["target"])
        kunci = item["options"][item["answer"]]
        if kunci != kata:
            problems.append(
                f"{item['id']}: kunci {kunci!r} berbeda dari kata pada kalimat {kata!r}"
            )
    assert not problems, "\n".join(problems)


def test_target_baca_dalam_jangkauan():
    problems = []
    for item in dataio.reading_items():
        if item["target"] is None:
            continue
        n = len(item["full_ar"].split(" "))
        if not 0 <= item["target"] < n:
            problems.append(f"{item['id']}: target={item['target']}, kata hanya {n}")
    assert not problems, "\n".join(problems)


def test_semua_pilihan_baca_berangka_huruf_sama():
    """Soal 'pilih bacaan yang benar' tidak boleh bisa dijawab dari rangka huruf.

    Bila salah satu pilihan punya rangka huruf berbeda, soal menjadi sepele
    karena pengecohnya tidak mungkin dibaca dari tulisan yang sama.
    """
    problems = []
    for item in dataio.reading_items():
        if item["type"] != "harakat_choice":
            continue
        rangka = {strip_harakat(o) for o in item["options"]}
        if len(rangka) != 1:
            problems.append(f"{item['id']}: rangka huruf berbeda {sorted(rangka)}")
    assert not problems, "\n".join(problems)


def test_meaning_choice_tidak_punya_target():
    problems = [i["id"] for i in dataio.reading_items()
                if i["type"] == "meaning_choice" and i["target"] is not None]
    assert not problems, f"meaning_choice seharusnya target=null: {problems}"


# --------------------------------------------------- soal buatan otomatis ---

@pytest.mark.parametrize("seed", SEEDS)
def test_soal_kosakata_id_ke_ar_hanya_satu_jawaban_benar(seed):
    pool = dataio.vocab_entries()
    by_ar: dict[str, list[dict]] = {}
    for e in pool:
        by_ar.setdefault(e["ar"], []).append(e)
    problems = []
    for e in pool:
        q = vocab_id_to_ar(e, pool, random.Random(seed))
        if q.options[q.answer] != e["ar"]:
            problems.append(f"{e['id']}: kunci tidak menunjuk kata yang benar")
        if len(set(q.options)) != len(q.options):
            problems.append(f"{e['id']}: pilihan ganda")
        prompt_key = normalize(e["gloss"])
        for i, opt in enumerate(q.options):
            if i == q.answer:
                continue
            for cand in by_ar.get(opt, []):
                if prompt_key in accepted_set(cand):
                    problems.append(
                        f"{e['id']} '{e['gloss']}': pengecoh {opt} juga jawaban benar"
                    )
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("seed", SEEDS)
def test_soal_akar_buatan_hanya_satu_jawaban_benar(seed):
    fams = dataio.root_families()
    problems = []
    for fam in fams:
        q = root_of_word(fam, fams, random.Random(seed))
        if q.options[q.answer] != fam["root"]:
            problems.append(f"{fam['id']}: kunci root_of_word salah")
        if len(set(q.options)) != len(q.options):
            problems.append(f"{fam['id']}: pilihan root_of_word ganda")

        q2 = odd_one_out(fam, fams, random.Random(seed))
        keluar = q2.options[q2.answer]
        anggota = {m["ar"] for m in fam["members"]}
        if keluar in anggota:
            problems.append(f"{fam['id']}: odd_one_out menunjuk anggota keluarganya")
        lain = [o for i, o in enumerate(q2.options) if i != q2.answer]
        for o in lain:
            if o not in anggota:
                problems.append(f"{fam['id']}: {o} bukan anggota tetapi dijadikan pengecoh")
        if len(set(q2.options)) != len(q2.options):
            problems.append(f"{fam['id']}: pilihan odd_one_out ganda")
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("mode", MODES)
def test_setiap_soal_punya_kunci_yang_sah(mode, seed):
    problems = []
    for q in build_pool(mode, None, random.Random(seed)):
        if q.kind == "mcq":
            if q.options is None or q.answer is None:
                problems.append(f"{q.card_id}: soal mcq tanpa pilihan atau kunci")
                continue
            if not 0 <= q.answer < len(q.options):
                problems.append(f"{q.card_id}: kunci di luar jangkauan")
            if len(set(q.options)) != len(q.options):
                problems.append(f"{q.card_id}: pilihan ganda")
        elif q.kind == "typed":
            if not q.accepted:
                problems.append(f"{q.card_id}: soal bertaip tanpa jawaban yang diterima")
        elif q.kind == "selfcheck":
            if not q.reveal:
                problems.append(f"{q.card_id}: selfcheck tanpa jawaban untuk dibandingkan")
        else:
            problems.append(f"{q.card_id}: kind tidak dikenal: {q.kind}")
        if not q.question.strip():
            problems.append(f"{q.card_id}: pertanyaan kosong")
    assert not problems, "\n".join(problems)


def test_jawaban_bertaip_menerima_arti_utama():
    """Mengetik arti utama harus dinilai benar."""
    problems = []
    for q in build_pool("kosakata-ar", None, random.Random(0)):
        entry = next(e for e in dataio.vocab_entries() if e["id"] == q.card_id)
        if not q.is_correct_text(entry["gloss"]):
            problems.append(f"{q.card_id}: arti utama tidak diterima")
        for a in entry.get("alt") or []:
            if not q.is_correct_text(a):
                problems.append(f"{q.card_id}: arti alternatif {a!r} tidak diterima")
    assert not problems, "\n".join(problems)


def test_jawaban_bertaip_menolak_arti_yang_salah():
    kitab = next(e for e in dataio.vocab_entries() if e["gloss"] == "buku")
    q = next(q for q in build_pool("kosakata-ar", None, random.Random(0))
             if q.card_id == kitab["id"])
    assert q.is_correct_text("buku")
    assert q.is_correct_text("  BUKU  ")
    assert not q.is_correct_text("pulpen")
    assert not q.is_correct_text("")
