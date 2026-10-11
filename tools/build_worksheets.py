#!/usr/bin/env python3
"""Buat lembar kerja Markdown beserta kunci jawaban terpisah.

    python tools/build_worksheets.py

Hasilnya:
  worksheets/ws-NN.md            lembar kerja (tanpa jawaban)
  worksheets/answers/ws-NN-kunci.md   kunci jawaban

Isi lembar kerja diambil langsung dari data/*.json dengan generator acak
ber-seed tetap, sehingga menjalankan ulang skrip ini menghasilkan lembar yang
sama persis. Kunci jawaban dibuat pada proses yang sama dengan soalnya,
sehingga tidak mungkin tidak sinkron.
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arabdrill import dataio  # noqa: E402
from arabdrill.arabic import strip_harakat  # noqa: E402
from arabdrill.questions import target_word  # noqa: E402

ROOT = dataio.ROOT
WS_DIR = os.path.join(ROOT, "worksheets")
KEY_DIR = os.path.join(WS_DIR, "answers")

#: (nomor lembar, tahap). Dua lembar per tahap, enam tahap.
PLAN = [(n, (n + 1) // 2) for n in range(1, 13)]

N_VOCAB_AR = 8
N_VOCAB_ID = 6
N_GRAMMAR = 5
N_ROOTS = 4
N_READING = 4
BLANK = " " * 20


class Picker:
    """Pengambil butir yang menghindari pengulangan antar lembar kerja."""

    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)
        self.used: set[str] = set()

    def take(self, pool: list[dict], n: int, key: str = "id") -> list[dict]:
        fresh = [x for x in pool if x[key] not in self.used]
        self.rng.shuffle(fresh)
        chosen = fresh[:n]
        if len(chosen) < n:
            # Kolam sudah habis; ulangi butir lama agar lembar tetap penuh.
            rest = [x for x in pool if x[key] not in {c[key] for c in chosen}]
            self.rng.shuffle(rest)
            chosen += rest[: n - len(chosen)]
        for c in chosen:
            self.used.add(c[key])
        return chosen


def _mcq_block(lines: list[str], n: int, item: dict) -> None:
    lines.append(f"{n}. {item['prompt']}")
    if item.get("prompt_ar"):
        lines.append("")
        lines.append(f"   > {item['prompt_ar']}")
    lines.append("")
    for i, opt in enumerate(item["options"]):
        lines.append(f"   {chr(ord('a') + i)}. {opt}")
    lines.append("")
    lines.append("   Jawaban: ____")
    lines.append("")


def build_worksheet(number: int, stage: int, pickers: dict[str, Picker]) -> tuple[str, str]:
    vocab_pool = [e for e in dataio.vocab_entries() if e["stage"] <= stage]
    grammar_pool = [i for i in dataio.grammar_items() if i["stage"] <= stage]
    root_pool = [f for f in dataio.root_families() if f["stage"] <= stage]
    reading_pool = [
        i for i in dataio.reading_items()
        if i["stage"] <= stage and i["type"] == "harakat_choice"
    ]

    v_ar = pickers["vocab_ar"].take(vocab_pool, N_VOCAB_AR)
    v_id = pickers["vocab_id"].take(vocab_pool, N_VOCAB_ID)
    gram = pickers["grammar"].take(grammar_pool, N_GRAMMAR)
    roots = pickers["roots"].take(root_pool, min(N_ROOTS, len(root_pool)))
    read = pickers["reading"].take(reading_pool, min(N_READING, len(reading_pool)))

    rng = random.Random(1000 + number)

    ws: list[str] = []
    key: list[str] = []
    tag = f"ws-{number:02d}"

    ws.append(f"# Lembar kerja {number:02d} · tahap {stage}")
    ws.append("")
    ws.append(
        "Kerjakan dengan tulisan tangan tanpa membuka data. Menuliskan harakat "
        "sendiri adalah bagian dari latihannya. Perkiraan waktu 20-30 menit."
    )
    ws.append("")
    ws.append(f"Kunci jawaban: `worksheets/answers/{tag}-kunci.md`")
    ws.append("")

    key.append(f"# Kunci jawaban · lembar kerja {number:02d} · tahap {stage}")
    key.append("")
    key.append(f"Soal: `worksheets/{tag}.md`")
    key.append("")

    # --- A. Kosakata Arab ke Indonesia ------------------------------------
    ws.append("## A. Tulis arti kata berikut dalam Bahasa Indonesia")
    ws.append("")
    ws.append("| No | Kata | Arti |")
    ws.append("|---:|:-----|:-----|")
    key.append("## A. Arti kata")
    key.append("")
    key.append("| No | Kata | Arti | Keterangan |")
    key.append("|---:|:-----|:-----|:-----------|")
    for i, e in enumerate(v_ar, 1):
        ws.append(f"| {i} | {e['ar']} | {BLANK} |")
        extra = [e["pos"]]
        if e.get("gender"):
            extra.append({"m": "mudzakkar", "f": "mu'annats",
                          "m/f": "mudzakkar/mu'annats"}[e["gender"]])
        if e.get("plural"):
            extra.append("jamak: " + e["plural"])
        if e.get("root"):
            extra.append("akar: " + e["root"])
        key.append(f"| {i} | {e['ar']} | {e['gloss']} | {' · '.join(extra)} |")
    ws.append("")
    key.append("")

    # --- B. Kosakata Indonesia ke Arab ------------------------------------
    ws.append("## B. Tulis kata Arab berharakat untuk arti berikut")
    ws.append("")
    ws.append("| No | Arti | Kata Arab |")
    ws.append("|---:|:-----|:----------|")
    key.append("## B. Kata Arab")
    key.append("")
    key.append("| No | Arti | Kata Arab | Contoh pemakaian |")
    key.append("|---:|:-----|:----------|:-----------------|")
    for i, e in enumerate(v_id, 1):
        ws.append(f"| {i} | {e['gloss']} | {BLANK} |")
        key.append(
            f"| {i} | {e['gloss']} | {e['ar']} | "
            f"{e['example']['ar']} = {e['example']['gloss']} |"
        )
    ws.append("")
    key.append("")

    # --- C. Tata bahasa ----------------------------------------------------
    ws.append("## C. Tata bahasa: pilih satu jawaban")
    ws.append("")
    key.append("## C. Tata bahasa")
    key.append("")
    for i, item in enumerate(gram, 1):
        _mcq_block(ws, i, item)
        letter = chr(ord("a") + item["answer"])
        key.append(f"{i}. **{letter}** — {item['options'][item['answer']]}")
        if item.get("explain"):
            key.append(f"   {item['explain']}")
        key.append(f"   (topik {item['topic_id']}: {item['topic_title']})")
        key.append("")

    # --- D. Akar kata ------------------------------------------------------
    ws.append("## D. Akar kata")
    ws.append("")
    ws.append("Tulis akar tiga huruf dari setiap kata berikut.")
    ws.append("")
    ws.append("| No | Kata | Akar |")
    ws.append("|---:|:-----|:-----|")
    key.append("## D. Akar kata")
    key.append("")
    key.append("| No | Kata | Akar | Pola | Arti |")
    key.append("|---:|:-----|:-----|:-----|:-----|")
    d_items = []
    for fam in roots:
        member = rng.choice(fam["members"])
        d_items.append((fam, member))
    for i, (fam, member) in enumerate(d_items, 1):
        ws.append(f"| {i} | {member['ar']} | {BLANK} |")
        key.append(
            f"| {i} | {member['ar']} | {fam['root']} | {member['pattern']} | "
            f"{member['gloss']} |"
        )
    ws.append("")
    key.append("")

    # --- E. Baca tanpa harakat --------------------------------------------
    ws.append("## E. Membaca tanpa harakat")
    ws.append("")
    ws.append(
        "Tulis ulang setiap kalimat dengan harakat penuh, lalu tulis artinya. "
        "Kata di dalam tanda kurung adalah kata yang paling menentukan bacaannya."
    )
    ws.append("")
    key.append("## E. Membaca tanpa harakat")
    key.append("")
    for i, item in enumerate(read, 1):
        bare_sentence = strip_harakat(item["full_ar"])
        bare_word = strip_harakat(target_word(item["full_ar"], item["target"]))
        ws.append(f"{i}. {bare_sentence}   (kata kunci: {bare_word})")
        ws.append("")
        ws.append("   Berharakat: ______________________________________")
        ws.append("")
        ws.append("   Arti: ___________________________________________")
        ws.append("")
        key.append(f"{i}. {item['full_ar']}")
        key.append(f"   Arti: {item['gloss']}")
        key.append(
            f"   Kata kunci {bare_word} dibaca "
            f"{item['options'][item['answer']]}."
        )
        if item.get("explain"):
            key.append(f"   {item['explain']}")
        if item.get("option_glosses"):
            other = "; ".join(
                f"{o} = {g}"
                for j, (o, g) in enumerate(zip(item["options"], item["option_glosses"]))
                if j != item["answer"]
            )
            if other:
                key.append(f"   Bacaan lain yang mungkin tetapi tidak cocok: {other}")
        key.append("")

    ws.append("---")
    ws.append("")
    ws.append(
        "Setelah selesai, cocokkan dengan kunci jawaban. Butir yang salah "
        "sebaiknya dilatih lagi lewat `python quiz.py`, bukan hanya dibaca ulang."
    )
    ws.append("")

    return "\n".join(ws), "\n".join(key)


def main() -> int:
    os.makedirs(WS_DIR, exist_ok=True)
    os.makedirs(KEY_DIR, exist_ok=True)
    pickers = {
        name: Picker(seed)
        for name, seed in (
            ("vocab_ar", 11), ("vocab_id", 22), ("grammar", 33),
            ("roots", 44), ("reading", 55),
        )
    }
    index: list[str] = [
        "# Lembar kerja",
        "",
        "Latihan tertulis yang dibuat dari `data/*.json` oleh "
        "`tools/build_worksheets.py`. Jangan menyunting berkas di folder ini; "
        "sunting datanya lalu jalankan ulang skripnya.",
        "",
        "| Lembar | Tahap | Kunci |",
        "|:-------|------:|:------|",
    ]
    for number, stage in PLAN:
        ws, key = build_worksheet(number, stage, pickers)
        tag = f"ws-{number:02d}"
        with open(os.path.join(WS_DIR, f"{tag}.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(ws)
        with open(os.path.join(KEY_DIR, f"{tag}-kunci.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(key)
        index.append(f"| [{tag}.md]({tag}.md) | {stage} | [answers/{tag}-kunci.md](answers/{tag}-kunci.md) |")
        print(f"  worksheets/{tag}.md  +  worksheets/answers/{tag}-kunci.md")
    index.append("")
    with open(os.path.join(WS_DIR, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(index))
    print("  worksheets/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
