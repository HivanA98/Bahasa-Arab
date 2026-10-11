#!/usr/bin/env python3
"""Buat ulang ekspor CSV dari data/*.json.

Hasilnya:
  data/csv/*.csv   tabel mentah untuk dibaca di penyunting lembar kerja
  anki/*.csv       berkas impor untuk Anki (tanpa baris judul)

Berkas JSON di data/ adalah satu-satunya sumber data. Jangan menyunting hasil
ekspor; sunting JSON-nya lalu jalankan ulang skrip ini.

    python tools/build_exports.py
"""

from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arabdrill import dataio  # noqa: E402
from arabdrill.arabic import strip_harakat  # noqa: E402
from arabdrill.questions import target_word  # noqa: E402
from arabdrill.translit import translit  # noqa: E402

ROOT = dataio.ROOT
CSV_DIR = os.path.join(ROOT, "data", "csv")
ANKI_DIR = os.path.join(ROOT, "anki")

#: Baris pengarah untuk Anki 2.1.55 ke atas. Versi Anki yang lebih tua tidak
#: mengenalinya; hapus baris-baris ini bila impor gagal (lihat anki/README.md).
ANKI_DIRECTIVES = ["#separator:Comma", "#html:false"]


def _write_csv(path: str, header: list[str], rows: list[list[str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        if header:
            w.writerow(header)
        w.writerows(rows)
    print(f"  {os.path.relpath(path, ROOT)}  ({len(rows)} baris)")


def _write_anki(path: str, rows: list[list[str]], tags_column: int) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        for line in ANKI_DIRECTIVES:
            f.write(line + "\n")
        f.write(f"#tags column:{tags_column}\n")
        w = csv.writer(f, lineterminator="\n", quoting=csv.QUOTE_ALL)
        w.writerows(rows)
    print(f"  {os.path.relpath(path, ROOT)}  ({len(rows)} kartu)")


def _s(value: object) -> str:
    """Ubah nilai menjadi teks; None dan daftar kosong menjadi string kosong."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value)


# ---------------------------------------------------------------- data/csv ---

def export_vocab_csv() -> None:
    entries = dataio.vocab_entries()
    header = [
        "id", "ar", "translit", "gloss", "alt", "pos", "gender", "fem", "plural",
        "mudhari", "root", "root_note", "example_ar", "example_gloss", "cat",
        "stage", "note",
    ]
    rows = [
        [
            e["id"], e["ar"], translit(e["ar"]), e["gloss"], _s(e.get("alt")), e["pos"],
            _s(e.get("gender")), _s(e.get("fem")), _s(e.get("plural")),
            _s(e.get("mudhari")), _s(e.get("root")), _s(e.get("root_note")),
            e["example"]["ar"], e["example"]["gloss"], e["cat"], str(e["stage"]),
            _s(e.get("note")),
        ]
        for e in entries
    ]
    _write_csv(os.path.join(CSV_DIR, "vocab.csv"), header, rows)


def export_grammar_csv() -> None:
    topics = dataio.grammar_topics()
    _write_csv(
        os.path.join(CSV_DIR, "grammar_topics.csv"),
        ["id", "stage", "title", "explanation", "caveats", "examples"],
        [
            [t["id"], str(t["stage"]), t["title"], t["explanation"],
             " | ".join(t.get("caveats") or []),
             " | ".join(f"{x['ar']} = {x['gloss']}" for x in t["examples"])]
            for t in topics
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "grammar_items.csv"),
        ["id", "topic_id", "stage", "type", "prompt", "prompt_ar", "options_lang",
         "options", "answer", "answer_text", "explain"],
        [
            [i["id"], i["topic_id"], str(i["stage"]), i["type"], i["prompt"],
             _s(i.get("prompt_ar")), i["options_lang"], " | ".join(i["options"]),
             str(i["answer"]), i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.grammar_items()
        ],
    )


def export_roots_csv() -> None:
    rows = []
    for fam in dataio.root_families():
        for m in fam["members"]:
            rows.append([
                fam["id"], fam["root"], fam["meaning"], str(fam["stage"]),
                m["ar"], translit(m["ar"]), m["gloss"], m["pattern"], _s(fam.get("note")),
            ])
    _write_csv(
        os.path.join(CSV_DIR, "roots_families.csv"),
        ["family_id", "root", "root_meaning", "stage", "ar", "translit", "gloss",
         "pattern", "family_note"],
        rows,
    )
    _write_csv(
        os.path.join(CSV_DIR, "roots_patterns.csv"),
        ["id", "pattern", "variants", "function", "stage", "examples", "note"],
        [
            [p["id"], p["pattern"], _s(p.get("variants")), p["function"], str(p["stage"]),
             " | ".join(f"{x['ar']} = {x['gloss']} ({x['root']})" for x in p["examples"]),
             _s(p.get("note"))]
            for p in dataio.root_patterns()
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "roots_items.csv"),
        ["id", "stage", "prompt", "prompt_ar", "options_lang", "options", "answer",
         "answer_text", "explain"],
        [
            [i["id"], str(i["stage"]), i["prompt"], _s(i.get("prompt_ar")),
             i["options_lang"], " | ".join(i["options"]), str(i["answer"]),
             i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.root_items()
        ],
    )


def export_reading_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "reading_passages.csv"),
        ["id", "stage", "level", "ar_level1", "ar_level3", "gloss", "keep"],
        [
            [p["id"], str(p["stage"]), str(p["level"]), p["ar"],
             strip_harakat(p["ar"]), p["gloss"], _s(p.get("keep"))]
            for p in dataio.reading_passages()
        ],
    )
    rows = []
    for i in dataio.reading_items():
        tw = target_word(i["full_ar"], i["target"]) if i["target"] is not None else ""
        rows.append([
            i["id"], i["type"], str(i["stage"]), str(i["level"]),
            strip_harakat(i["full_ar"]), i["full_ar"], i["gloss"],
            _s(i["target"]), strip_harakat(tw) if tw else "",
            " | ".join(i["options"]), str(i["answer"]), i["options"][i["answer"]],
            _s(i.get("option_glosses")), _s(i.get("explain")),
        ])
    _write_csv(
        os.path.join(CSV_DIR, "reading_items.csv"),
        ["id", "type", "stage", "level", "shown_no_harakat", "full_ar", "gloss",
         "target_index", "target_word_bare", "options", "answer", "answer_text",
         "option_glosses", "explain"],
        rows,
    )


def export_quran_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "quran_msa_entries.csv"),
        ["id", "ar", "translit", "root", "kind", "classical", "msa", "note",
         "quran_examples"],
        [
            [e["id"], e["ar"], translit(e["ar"]), _s(e.get("root")), e["kind"],
             e["classical"], e["msa"], _s(e.get("note")), _s(e.get("quran_examples"))]
            for e in dataio.quran_entries()
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "quran_msa_items.csv"),
        ["id", "stage", "prompt", "prompt_ar", "options_lang", "options", "answer",
         "answer_text", "explain"],
        [
            [i["id"], str(i["stage"]), i["prompt"], _s(i.get("prompt_ar")),
             i["options_lang"], " | ".join(i["options"]), str(i["answer"]),
             i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.quran_items()
        ],
    )


# -------------------------------------------------------------------- anki ---

def _detail(e: dict) -> str:
    bits = [e["pos"]]
    if e.get("gender"):
        bits.append({"m": "mudzakkar", "f": "mu'annats",
                     "m/f": "mudzakkar/mu'annats"}[e["gender"]])
    if e.get("plural"):
        bits.append("jamak: " + e["plural"])
    if e.get("fem"):
        bits.append("mu'annats: " + e["fem"])
    if e.get("mudhari"):
        bits.append("mudhari': " + e["mudhari"])
    if e.get("root"):
        bits.append("akar: " + e["root"])
    return " · ".join(bits)


def export_anki_vocab() -> None:
    rows = []
    for e in dataio.vocab_entries():
        rows.append([
            e["ar"],
            e["gloss"],
            _detail(e),
            e["example"]["ar"],
            e["example"]["gloss"],
            translit(e["ar"]),
            _s(e.get("note")),
            f"arab::kosakata arab::{e['cat']} arab::tahap{e['stage']}",
        ])
    _write_anki(os.path.join(ANKI_DIR, "kosakata.csv"), rows, tags_column=8)


def export_anki_grammar() -> None:
    rows = []
    for i in dataio.grammar_items():
        front = i["prompt"]
        if i.get("prompt_ar"):
            front += "<br>" + i["prompt_ar"]
        back = i["options"][i["answer"]]
        rows.append([
            front, back, _s(i.get("explain")), i["topic_title"],
            f"arab::tatabahasa arab::{i['topic_id']} arab::tahap{i['stage']}",
        ])
    _write_anki(os.path.join(ANKI_DIR, "tatabahasa.csv"), rows, tags_column=5)


def export_anki_roots() -> None:
    rows = []
    for fam in dataio.root_families():
        for m in fam["members"]:
            rows.append([
                m["ar"],
                f"{m['gloss']}",
                fam["root"],
                fam["meaning"],
                m["pattern"],
                translit(m["ar"]),
                f"arab::akar arab::{fam['id']} arab::tahap{fam['stage']}",
            ])
    _write_anki(os.path.join(ANKI_DIR, "akar.csv"), rows, tags_column=7)


def export_anki_reading() -> None:
    rows = []
    for p in dataio.reading_passages():
        rows.append([
            strip_harakat(p["ar"]), p["ar"], p["gloss"],
            f"Level {p['level']}",
            f"arab::baca arab::level{p['level']} arab::tahap{p['stage']}",
        ])
    for i in dataio.reading_items():
        rows.append([
            strip_harakat(i["full_ar"]), i["full_ar"], i["gloss"],
            _s(i.get("explain")),
            f"arab::baca arab::level{i['level']} arab::tahap{i['stage']}",
        ])
    _write_anki(os.path.join(ANKI_DIR, "baca.csv"), rows, tags_column=5)


def export_anki_quran() -> None:
    rows = [
        [
            e["ar"],
            f"MSA: {e['msa']}",
            f"Klasik: {e['classical']}",
            e["kind"],
            _s(e.get("note")),
            "arab::quran-msa",
        ]
        for e in dataio.quran_entries()
    ]
    _write_anki(os.path.join(ANKI_DIR, "quran-msa.csv"), rows, tags_column=6)


def main() -> int:
    print("Membuat ekspor CSV dari data/*.json")
    print("data/csv/:")
    export_vocab_csv()
    export_grammar_csv()
    export_roots_csv()
    export_reading_csv()
    export_quran_csv()
    print("anki/:")
    export_anki_vocab()
    export_anki_grammar()
    export_anki_roots()
    export_anki_reading()
    export_anki_quran()
    print("Selesai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
