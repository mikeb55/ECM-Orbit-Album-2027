#!/usr/bin/env python3
"""Modulation Menu CLI – simple_menu mode: fixed bridge formulas per style."""
import argparse
import json
import re

# Chroma: C=0, C#=1, D=2, Eb=3, E=4, F=5, F#=6, G=7, Ab=8, A=9, Bb=10, B=11
CHROMA_SHARP = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
CHROMA_FLAT = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")
ROOT_PATTERN = re.compile(r"^([A-G])([#b]?)(.*)$")


def parse_chord_root(symbol: str) -> int:
    """Extract root chroma (0–11) from chord symbol. Uses sharp names."""
    m = ROOT_PATTERN.match(symbol.strip())
    if not m:
        return 0
    step, acc, _ = m.groups()
    idx = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[step]
    if acc == "#":
        idx = (idx + 1) % 12
    elif acc == "b":
        idx = (idx - 1) % 12
    return idx


def chroma_to_name(i: int, prefer_flat: bool = False) -> str:
    return CHROMA_FLAT[i] if prefer_flat else CHROMA_SHARP[i]


def get_scale_degree(root: int, degree: str) -> int:
    """degree: 'I','ii','iii','IV','V','vi','vii' or 'bIII','bVI','bII' etc."""
    deg = degree.upper().replace("B", "b").replace("#", "#")
    base = {"I": 0, "II": 2, "III": 4, "IV": 5, "V": 7, "VI": 9, "VII": 11}
    flat_map = {"BIII": 3, "BVI": 8, "BII": 1, "BVII": 10}
    if degree in flat_map:
        return (root + flat_map[degree]) % 12
    letter = "".join(c for c in degree if c.isalpha())
    acc = -1 if "b" in degree or "B" in degree[1:] else 0
    acc += 1 if "#" in degree else 0
    b = base.get(letter.upper(), 0)
    return (root + b + acc) % 12


def simple_menu_classical(root: int) -> list[dict]:
    r = root
    opts = [
        {
            "label": "Pivot via relative minor",
            "target_key": chroma_to_name((r + 9) % 12) + "m",
            "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+9)%12)}m,{chroma_to_name((r+2)%12)},{chroma_to_name((r+7)%12)},{chroma_to_name((r+9)%12)}m",
        },
        {
            "label": "Secondary dominant",
            "target_key": chroma_to_name((r + 9) % 12) + "m",
            "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+6)%12)}7,{chroma_to_name((r+9)%12)}m",
        },
        {
            "label": "Circle of fifths step",
            "target_key": chroma_to_name((r + 7) % 12),
            "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+7)%12)},{chroma_to_name((r+2)%12)},{chroma_to_name((r+7)%12)}",
        },
    ]
    return opts


def simple_menu_jazz_modern(root: int) -> list[dict]:
    r = root
    opts = [
        {
            "label": "Tritone sub dominant",
            "target_key": chroma_to_name((r + 6) % 12),
            "bridge_chords": f"{chroma_to_name((r+2)%12)}m7,{chroma_to_name((r+6)%12)}7,{chroma_to_name((r+6)%12)}maj7",
        },
        {
            "label": "Modal interchange mediant",
            "target_key": chroma_to_name((r + 8) % 12),
            "bridge_chords": f"{chroma_to_name(r)}maj7,{chroma_to_name((r+8)%12)}maj7,{chroma_to_name((r+3)%12)}maj7",
        },
        {
            "label": "Side-slip return",
            "target_key": chroma_to_name(r),
            "bridge_chords": f"{chroma_to_name((r+2)%12)}m,{chroma_to_name((r+3)%12)}m,{chroma_to_name((r+2)%12)}m,{chroma_to_name(r)}",
        },
    ]
    return opts


def simple_menu_jazz_rock(root: int) -> list[dict]:
    r = root
    target_up4 = (r + 5) % 12
    opts = [
        {
            "label": "Dominant chain",
            "target_key": chroma_to_name(target_up4),
            "bridge_chords": f"{chroma_to_name((r+2)%12)}7,{chroma_to_name((r+7)%12)}7,{chroma_to_name(r)}7,{chroma_to_name(target_up4)}",
        },
        {
            "label": "Major third jump",
            "target_key": chroma_to_name((r + 4) % 12),
            "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+4)%12)}",
        },
        {
            "label": "Parallel dominant shift",
            "target_key": chroma_to_name((r + 4) % 12),
            "bridge_chords": f"{chroma_to_name(r)}7,{chroma_to_name((r+2)%12)}7,{chroma_to_name((r+4)%12)}7",
        },
    ]
    return opts


def simple_menu_pop_colour(root: int, prog: str) -> list[dict]:
    r = root
    chords = [c.strip() for c in prog.split(",") if c.strip()]
    transposed = []
    for c in chords:
        m = ROOT_PATTERN.match(c)
        if m:
            step, acc, rest = m.groups()
            idx = parse_chord_root(c)
            new_idx = (idx + 2) % 12
            new_root = chroma_to_name(new_idx)
            if "m" in rest.lower() or "min" in rest.lower():
                transposed.append(new_root + "m" + rest.split("m", 1)[-1].split("m", 1)[0] if "m" in rest else "m")
            else:
                transposed.append(new_root + rest)
        else:
            transposed.append(c)
    bridge_str = ",".join(transposed) if transposed else chroma_to_name((r + 2) % 12)
    opts = [
        {
            "label": "Whole step lift",
            "target_key": chroma_to_name((r + 2) % 12),
            "bridge_chords": bridge_str,
        },
        {
            "label": "Relative minor shift",
            "target_key": chroma_to_name((r + 9) % 12) + "m",
            "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+9)%12)}m",
        },
        {
            "label": "Direct mediant jump",
            "target_key": chroma_to_name((r + 4) % 12),
            "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+4)%12)}",
        },
    ]
    return opts


def simple_menu_pop_colour_fix(root: int, prog: str) -> list[dict]:
    """Whole step: transpose each chord +2 semitones."""
    r = root
    chords = [c.strip() for c in prog.split(",") if c.strip()]
    transposed = []
    for c in chords:
        idx = parse_chord_root(c)
        new_idx = (idx + 2) % 12
        new_root = chroma_to_name(new_idx)
        rest = c[1:] if c[0] in "ABCDEFG" else c
        if rest.startswith("#") or rest.startswith("b"):
            rest = rest[1:]
        if "m" in rest.lower():
            suffix = "m" + "".join(x for x in rest if x in "79addsus")
        else:
            suffix = "".join(x for x in rest if x in "79addsus")
        transposed.append(new_root + suffix if suffix else new_root)
    bridge_str = ",".join(transposed) if transposed else chroma_to_name((r + 2) % 12)
    opts = [
        {"label": "Whole step lift", "target_key": chroma_to_name((r + 2) % 12), "bridge_chords": bridge_str},
        {"label": "Relative minor shift", "target_key": chroma_to_name((r + 9) % 12) + "m", "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+9)%12)}m"},
        {"label": "Direct mediant jump", "target_key": chroma_to_name((r + 4) % 12), "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+4)%12)}"},
    ]
    return opts


def simple_menu_ecm_axis(root: int) -> list[dict]:
    r = root
    maj3 = (r + 4) % 12
    opts = [
        {
            "label": "Common tone drift",
            "target_key": chroma_to_name(maj3),
            "bridge_chords": f"{chroma_to_name(r)}maj7,{chroma_to_name(maj3)}maj7",
        },
        {
            "label": "Bass reorientation",
            "target_key": chroma_to_name((r + 4) % 12),
            "bridge_chords": f"{chroma_to_name(r)}maj7,{chroma_to_name(r)}maj7/{chroma_to_name((r+4)%12)},{chroma_to_name((r+4)%12)}maj7",
        },
        {
            "label": "Third-cycle drift",
            "target_key": chroma_to_name((r + 8) % 12),
            "bridge_chords": f"{chroma_to_name(r)},{chroma_to_name((r+3)%12)},{chroma_to_name((r+8)%12)},{chroma_to_name((r+8)%12)}",
        },
    ]
    return opts


def run_simple_menu(prog: str, style: str) -> dict:
    chords = [c.strip() for c in prog.split(",") if c.strip()]
    if not chords:
        root = 0
    else:
        root = parse_chord_root(chords[-1])
    handlers = {
        "classical_structural": lambda: simple_menu_classical(root),
        "jazz_modern": lambda: simple_menu_jazz_modern(root),
        "jazz_rock": lambda: simple_menu_jazz_rock(root),
        "pop_colour": lambda: simple_menu_pop_colour_fix(root, prog),
        "ecm_axis": lambda: simple_menu_ecm_axis(root),
    }
    if style not in handlers:
        return {"style": style, "options": [], "error": "unsupported style"}
    options = handlers[style]()
    return {"style": style, "options": options}


def main():
    ap = argparse.ArgumentParser(description="Modulation Menu CLI")
    ap.add_argument("--prog", required=True, help="Chord progression (e.g. C,G,Am,F)")
    ap.add_argument("--style", required=True, choices=["classical_structural", "jazz_modern", "jazz_rock", "pop_colour", "ecm_axis"])
    ap.add_argument("--mode", default="simple_menu", choices=["simple_menu"])
    args = ap.parse_args()
    if args.mode == "simple_menu":
        result = run_simple_menu(args.prog, args.style)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
