"""Pemuat data dan pemeriksa skema.

Satu-satunya sumber data adalah berkas JSON di folder data/. Berkas CSV di
data/csv/ dan anki/ adalah hasil ekspor yang dibuat ulang oleh tools/, bukan
sumber yang diedit langsung.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")
SOURCES_DIR = os.path.join(ROOT, "sources")

MODULE_FILES = {
    "vocab": "vocab.json",
    "grammar": "grammar.json",
    "roots": "roots.json",
    "reading": "reading.json",
    "quran_msa": "quran_msa.json",
}

POS_VALUES = {
    "dhamir", "isyarah", "istifham", "adad", "ism", "fi'l", "sifah",
    "harf jar", "zarf", "harf athf", "harf nafi", "harf jawab",
}
GENDER_VALUES = {"m", "f", "m/f", None}
MAX_STAGE = 6


def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    """Muat satu modul data berdasarkan nama ('vocab', 'grammar', ...)."""
    if name not in MODULE_FILES:
        raise KeyError(f"modul tidak dikenal: {name}")
    return _read_json(os.path.join(DATA_DIR, MODULE_FILES[name]))


def load_all() -> dict[str, dict]:
    return {name: load(name) for name in MODULE_FILES}


def vocab_entries(stage: int | None = None) -> list[dict]:
    entries = load("vocab")["entries"]
    if stage is None:
        return list(entries)
    return [e for e in entries if e["stage"] <= stage]


def grammar_items(stage: int | None = None) -> list[dict]:
    out: list[dict] = []
    for topic in load("grammar")["topics"]:
        if stage is not None and topic["stage"] > stage:
            continue
        for item in topic["items"]:
            out.append({**item, "topic_id": topic["id"], "topic_title": topic["title"],
                        "stage": topic["stage"]})
    return out


def grammar_topics(stage: int | None = None) -> list[dict]:
    topics = load("grammar")["topics"]
    if stage is None:
        return list(topics)
    return [t for t in topics if t["stage"] <= stage]


def root_families(stage: int | None = None) -> list[dict]:
    fams = load("roots")["families"]
    if stage is None:
        return list(fams)
    return [f for f in fams if f["stage"] <= stage]


def root_patterns(stage: int | None = None) -> list[dict]:
    pats = load("roots")["patterns"]
    if stage is None:
        return list(pats)
    return [p for p in pats if p["stage"] <= stage]


def root_items(stage: int | None = None) -> list[dict]:
    items = load("roots")["items"]
    if stage is None:
        return list(items)
    return [i for i in items if i["stage"] <= stage]


def reading_items(stage: int | None = None, level: int | None = None) -> list[dict]:
    items = load("reading")["items"]
    out = [i for i in items if stage is None or i["stage"] <= stage]
    if level is not None:
        out = [i for i in out if i["level"] == level]
    return out


def reading_passages(stage: int | None = None, level: int | None = None) -> list[dict]:
    ps = load("reading")["passages"]
    out = [p for p in ps if stage is None or p["stage"] <= stage]
    if level is not None:
        out = [p for p in out if p["level"] == level]
    return out


def quran_items(stage: int | None = None) -> list[dict]:
    return list(load("quran_msa")["items"])


def quran_entries() -> list[dict]:
    return list(load("quran_msa")["entries"])


def source_files() -> list[str]:
    """Daftar berkas sumber yang disediakan pengguna di folder sources/."""
    if not os.path.isdir(SOURCES_DIR):
        return []
    return sorted(
        f for f in os.listdir(SOURCES_DIR)
        if not f.startswith(".") and f.lower() != "readme.md"
    )


def all_card_ids() -> list[str]:
    """Semua id yang dipakai sebagai kartu Leitner, dari seluruh modul."""
    ids: list[str] = []
    for e in load("vocab")["entries"]:
        ids.append(e["id"])
    for item in grammar_items():
        ids.append(item["id"])
    for item in root_items():
        ids.append(item["id"])
    for f in root_families():
        ids.append(f["id"])
    for item in reading_items():
        ids.append(item["id"])
    for p in reading_passages():
        ids.append(p["id"])
    for item in quran_items():
        ids.append(item["id"])
    return ids


__all__ = [
    "DATA_DIR",
    "GENDER_VALUES",
    "MAX_STAGE",
    "MODULE_FILES",
    "POS_VALUES",
    "ROOT",
    "SOURCES_DIR",
    "all_card_ids",
    "grammar_items",
    "grammar_topics",
    "load",
    "load_all",
    "quran_entries",
    "quran_items",
    "reading_items",
    "reading_passages",
    "root_families",
    "root_items",
    "root_patterns",
    "source_files",
    "vocab_entries",
]
