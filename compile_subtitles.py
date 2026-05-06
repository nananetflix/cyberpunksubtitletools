#!/usr/bin/env python3
"""
Compile Cyberpunk 2077 / Phantom Liberty subtitle JSONs into:
  1. One big text dump (all lines, sorted by source file then stringId)
  2. Quest-grouped output: one folder per quest, with subtitles.txt and onscreens.txt inside

Usage:
    python compile_subtitles.py <input_dir> <output_dir>

<input_dir>  = folder containing the WolvenKit-converted .json files
               (recursively walked; mix of subtitle and onscreen files is fine)
<output_dir> = folder where the compiled output is written
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


# ---------- Quest key extraction ----------
# Filenames look like: q304_somename.json, mq055_intro.json, ep1_q301_blah.json,
# sq026_..., etc. We bucket by the quest prefix; everything else falls into "_misc".
QUEST_PATTERN = re.compile(r"(?:^|[/\\_])((?:ep1_)?(?:m?q|sq|gig)\d{2,4})", re.IGNORECASE)


def quest_key_from_path(path: Path) -> str:
    """Pull a quest identifier out of a filename, or return '_misc' if none."""
    name = path.stem.lower()
    m = QUEST_PATTERN.search(name)
    if m:
        return m.group(1).lower()
    # Common non-quest buckets worth keeping separate
    if "shard" in name:
        return "_shards"
    if "tutorial" in name:
        return "_tutorials"
    if "ui" in name or "menu" in name:
        return "_ui"
    return "_misc"


# ---------- Variant rendering ----------
def render_variants(female: str, male: str) -> str:
    """Render the two pronoun variants per the user's choice (side-by-side when they differ)."""
    f = (female or "").strip()
    m = (male or "").strip()
    if f == m:
        return f
    if not f:
        return f"[M] {m}"
    if not m:
        return f"[F] {f}"
    return f"[F] {f}  ||  [M] {m}"


# ---------- Entry extraction ----------
# Real WolvenKit-converted files have a deep wrapper. The two shapes that matter:
#   subtitles:  root["Data"]["RootChunk"]["root"]["Data"]["entries"]
#               each entry has: stringId, femaleVariant, maleVariant
#   onscreens:  root["Data"]["RootChunk"]["root"]["Data"]["entries"]
#               each entry has: secondaryKey, femaleVariant, maleVariant
# We walk defensively — if the schema shifts a level, we still find the entries list.

def find_entries(obj):
    """Recursively locate the 'entries' array of subtitle/onscreen records."""
    if isinstance(obj, dict):
        if "entries" in obj and isinstance(obj["entries"], list) and obj["entries"]:
            sample = obj["entries"][0]
            if isinstance(sample, dict) and (
                "femaleVariant" in sample or "maleVariant" in sample
            ):
                return obj["entries"]
        for v in obj.values():
            found = find_entries(v)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = find_entries(v)
            if found is not None:
                return found
    return None


def classify_file(entries) -> str:
    """Return 'onscreen' if entries use secondaryKey, else 'subtitle'."""
    if entries and isinstance(entries[0], dict) and "secondaryKey" in entries[0]:
        return "onscreen"
    return "subtitle"


def parse_file(path: Path):
    """Yield dicts: {kind, key, text, source} for each line in the file."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"  ! skipped {path.name}: {e}", file=sys.stderr)
        return

    entries = find_entries(data)
    if not entries:
        return

    kind = classify_file(entries)
    for e in entries:
        if not isinstance(e, dict):
            continue
        text = render_variants(e.get("femaleVariant", ""), e.get("maleVariant", ""))
        if not text:
            continue
        key = str(e.get("secondaryKey") or e.get("stringId") or "")
        yield {"kind": kind, "key": key, "text": text, "source": path.name}


# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir", type=Path)
    ap.add_argument("output_dir", type=Path)
    args = ap.parse_args()

    if not args.input_dir.is_dir():
        sys.exit(f"input dir does not exist: {args.input_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(args.input_dir.rglob("*.json"))
    print(f"Found {len(json_files)} JSON files in {args.input_dir}")

    # Bucket: quest_key -> kind -> list of (source, key, text)
    buckets = defaultdict(lambda: defaultdict(list))
    total_lines = 0

    for jf in json_files:
        qkey = quest_key_from_path(jf)
        for line in parse_file(jf):
            buckets[qkey][line["kind"]].append((line["source"], line["key"], line["text"]))
            total_lines += 1

    print(f"Parsed {total_lines} lines across {len(buckets)} quest buckets")

    # ---- Write quest-grouped output ----
    quest_root = args.output_dir / "by_quest"
    quest_root.mkdir(exist_ok=True)
    for qkey, by_kind in sorted(buckets.items()):
        qdir = quest_root / qkey
        qdir.mkdir(exist_ok=True)
        for kind, lines in by_kind.items():
            # Stable sort: source filename, then key
            lines.sort(key=lambda r: (r[0], r[1]))
            out = qdir / f"{kind}s.txt"
            with out.open("w", encoding="utf-8") as f:
                current_source = None
                for source, key, text in lines:
                    if source != current_source:
                        f.write(f"\n--- {source} ---\n")
                        current_source = source
                    f.write(f"[{key}] {text}\n")

    # ---- Write the big dump ----
    dump_path = args.output_dir / "all_lines.txt"
    with dump_path.open("w", encoding="utf-8") as f:
        for qkey in sorted(buckets):
            f.write(f"\n\n========== {qkey} ==========\n")
            for kind in ("subtitle", "onscreen"):
                lines = buckets[qkey].get(kind, [])
                if not lines:
                    continue
                f.write(f"\n----- {kind}s -----\n")
                lines.sort(key=lambda r: (r[0], r[1]))
                current_source = None
                for source, key, text in lines:
                    if source != current_source:
                        f.write(f"\n# {source}\n")
                        current_source = source
                    f.write(f"[{key}] {text}\n")

    print(f"\nWrote {dump_path}")
    print(f"Wrote per-quest folders in {quest_root}")


if __name__ == "__main__":
    main()
