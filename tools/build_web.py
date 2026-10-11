#!/usr/bin/env python3
"""Buat webdata.js untuk aplikasi kartu di browser.

    python tools/build_web.py

Data tetap bersumber dari data/*.json. Berkas hasilnya dimuat lewat tag
<script>, bukan fetch(), supaya aplikasi jalan baik di GitHub Pages maupun
saat index.html dibuka langsung dari berkas (file://) tanpa masalah CORS.

Teks Arab ditulis sebagai escape \\uXXXX (ASCII murni) supaya tidak bergantung
pada charset yang dikirim peladen.

Semua bentuk tanpa harakat dan bentuk per level dihitung di sini memakai
arabdrill/arabic.py, sehingga logika harakat tidak perlu ditulis ulang dalam
JavaScript dan tetap satu sumber dengan yang dipakai quiz.py.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arabdrill import dataio  # noqa: E402
from arabdrill.arabic import strip_harakat  # noqa: E402
from arabdrill.questions import render_level, target_word  # noqa: E402
from arabdrill.translit import translit  # noqa: E402

ROOT = dataio.ROOT
OUT = os.path.join(ROOT, "webdata.js")

GENDER_LABEL = {"m": "mudzakkar", "f": "mu'annats", "m/f": "mudzakkar/mu'annats"}

CAT_LABEL = {
    "dhamir": "Kata ganti",
    "isyarah": "Kata tunjuk",
    "istifham": "Kata tanya",
    "adad": "Angka",
    "usrah": "Keluarga",
    "nas": "Orang",
    "asyya": "Benda",
    "makan": "Tempat",
    "zaman": "Waktu",
    "fi'l": "Kata kerja",
    "sifah": "Kata sifat",
    "huruf": "Huruf jar & zharf",
}


def _detail(e: dict) -> str:
    bits = [e["pos"]]
    if e.get("gender"):
        bits.append(GENDER_LABEL[e["gender"]])
    if e.get("plural"):
        bits.append("jamak: " + e["plural"])
    if e.get("fem"):
        bits.append("mu'annats: " + e["fem"])
    if e.get("mudhari"):
        bits.append("mudhari': " + e["mudhari"])
    return " · ".join(bits)


def build_kosakata() -> list[dict]:
    out = []
    for e in dataio.vocab_entries():
        out.append({
            "id": e["id"],
            "ar": e["ar"],
            "bare": strip_harakat(e["ar"]),
            "tr": translit(e["ar"]),
            "gloss": e["gloss"],
            "alt": e.get("alt") or [],
            "detail": _detail(e),
            "pos": e["pos"],
            "root": e.get("root") or "",
            "rootNote": e.get("root_note") or "",
            "exAr": e["example"]["ar"],
            "exBare": strip_harakat(e["example"]["ar"]),
            "exTr": translit(e["example"]["ar"]),
            "exGloss": e["example"]["gloss"],
            "cat": e["cat"],
            "catLabel": CAT_LABEL.get(e["cat"], e["cat"]),
            "stage": e["stage"],
            "note": e.get("note") or "",
        })
    return out


def build_tatabahasa() -> list[dict]:
    out = []
    for t in dataio.grammar_topics():
        for item in t["items"]:
            out.append({
                "id": item["id"],
                "cat": t["id"],
                "catLabel": t["title"],
                "stage": t["stage"],
                "prompt": item["prompt"],
                "promptAr": item.get("prompt_ar") or "",
                "optionsLang": item["options_lang"],
                "options": item["options"],
                "answer": item["answer"],
                "explain": item.get("explain") or "",
            })
    return out


def build_topik() -> list[dict]:
    return [
        {
            "id": t["id"],
            "title": t["title"],
            "stage": t["stage"],
            "explanation": t["explanation"],
            "caveats": t["caveats"],
            "examples": [
                {"ar": x["ar"], "tr": translit(x["ar"]), "gloss": x["gloss"]}
                for x in t["examples"]
            ],
        }
        for t in dataio.grammar_topics()
    ]


def build_akar() -> list[dict]:
    out = []
    for fam in dataio.root_families():
        anggota = [m["ar"] for m in fam["members"]]
        for m in fam["members"]:
            out.append({
                "id": f"{fam['id']}-{m['ar']}",
                "ar": m["ar"],
                "bare": strip_harakat(m["ar"]),
                "tr": translit(m["ar"]),
                "gloss": m["gloss"],
                "pattern": m["pattern"],
                "root": fam["root"],
                "rootMeaning": fam["meaning"],
                "cat": fam["id"],
                "catLabel": fam["root"],
                "stage": fam["stage"],
                "siblings": [a for a in anggota if a != m["ar"]],
                "note": fam.get("note") or "",
            })
    return out


def build_pola() -> list[dict]:
    return [
        {
            "id": p["id"],
            "pattern": p["pattern"],
            "variants": p.get("variants") or [],
            "function": p["function"],
            "stage": p["stage"],
            "examples": [
                {"ar": x["ar"], "tr": translit(x["ar"]), "gloss": x["gloss"], "root": x["root"]}
                for x in p["examples"]
            ],
            "note": p.get("note") or "",
        }
        for p in dataio.root_patterns()
    ]


def build_baca() -> list[dict]:
    out = []
    for p in dataio.reading_passages():
        keep = set(p.get("keep") or [])
        out.append({
            "id": p["id"],
            "kind": "teks",
            "stage": p["stage"],
            "level": p["level"],
            "cat": f"level{p['level']}",
            "catLabel": f"Level {p['level']}",
            "l1": p["ar"],
            "l2": render_level(p["ar"], 2, keep=keep),
            "l3": render_level(p["ar"], 3),
            "tr": translit(p["ar"]),
            "gloss": p["gloss"],
        })
    for i in dataio.reading_items():
        target = i["target"]
        soal = {
            "id": i["id"],
            "kind": "soal",
            "type": i["type"],
            "stage": i["stage"],
            "level": i["level"],
            "cat": f"level{i['level']}",
            "catLabel": f"Level {i['level']}",
            "l1": i["full_ar"],
            "l3": render_level(i["full_ar"], 3),
            "tr": translit(i["full_ar"]),
            "gloss": i["gloss"],
            "options": i["options"],
            "optionsLang": i["options_lang"],
            "answer": i["answer"],
            "optionGlosses": i.get("option_glosses") or [],
            "explain": i.get("explain") or "",
        }
        if target is not None:
            soal["shown"] = render_level(i["full_ar"], i["level"], blank=target)
            soal["targetBare"] = strip_harakat(target_word(i["full_ar"], target))
        else:
            soal["shown"] = render_level(i["full_ar"], i["level"])
            soal["targetBare"] = ""
        out.append(soal)
    return out


def build_quran() -> list[dict]:
    return [
        {
            "id": e["id"],
            "ar": e["ar"],
            "bare": strip_harakat(e["ar"]),
            "tr": translit(e["ar"]),
            "root": e.get("root") or "",
            "kind": e["kind"],
            "cat": e["kind"],
            "catLabel": e["kind"].capitalize(),
            "classical": e["classical"],
            "msa": e["msa"],
            "note": e.get("note") or "",
            "stage": 5,
        }
        for e in dataio.quran_entries()
    ]


def build_catatan() -> dict:
    d = dataio.load("quran_msa")
    return {
        "penting": d["catatan_penting"],
        "pemakaian": d["usage_notes"],
    }


def main() -> int:
    data = {
        "kosakata": build_kosakata(),
        "tatabahasa": build_tatabahasa(),
        "topik": build_topik(),
        "akar": build_akar(),
        "pola": build_pola(),
        "baca": build_baca(),
        "quran": build_quran(),
        "catatan": build_catatan(),
    }
    data["meta"] = {k: len(v) for k, v in data.items() if isinstance(v, list)}

    body = json.dumps(data, ensure_ascii=True, separators=(",", ":"), sort_keys=False)
    teks = (
        "/* Dibuat otomatis oleh tools/build_web.py dari data/*.json.\n"
        "   JANGAN disunting langsung; sunting datanya lalu jalankan ulang skripnya. */\n"
        '"use strict";\n'
        "const ARAB_DATA = " + body + ";\n"
    )
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(teks)
    kb = len(teks.encode("utf-8")) / 1024
    print(f"  webdata.js  ({kb:.0f} KB)")
    for k, n in data["meta"].items():
        print(f"    {k:12s} {n:4d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
