#!/usr/bin/env python3
"""
BHL (Bryant Harmonic Language) conformance audit for MusicXML scores.

BHL, codified 2026-08-06, drives harmony by colour, transformation and
voice-leading rather than functional progression. This script measures the
rules that are objectively testable from a chord timeline:

  Liquid Harmony      common tones retained between successive chords;
                      parsimonious root motion (step / third, not fifth)
  Anti-functional     no routine II-V-I, V-I, or circle-of-fifths chains
  Banned sonority     maj7(#11) temporarily banned
  Transformation      same root re-coloured rather than replaced
  Ending              inevitable by long-range relationship, not cadence

Rules BHL states that a script cannot judge - "melody grows from harmony",
"orchestration reveals existing ideas", emotional coherence - are out of scope
and left to the composer.

Usage: python tools/bhl_audit.py <file.musicxml> [...]
"""

import re
import sys

PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# MusicXML kind -> (chord-tone semitones above root, display suffix)
KINDS = {
    "major": ((0, 4, 7), ""),
    "minor": ((0, 3, 7), "m"),
    "augmented": ((0, 4, 8), "aug"),
    "diminished": ((0, 3, 6), "dim"),
    "major-sixth": ((0, 4, 7, 9), "6"),
    "minor-sixth": ((0, 3, 7, 9), "m6"),
    "major-seventh": ((0, 4, 7, 11), "maj7"),
    "minor-seventh": ((0, 3, 7, 10), "m7"),
    "dominant": ((0, 4, 7, 10), "7"),
    "half-diminished": ((0, 3, 6, 10), "m7b5"),
    "diminished-seventh": ((0, 3, 6, 9), "dim7"),
    "major-ninth": ((0, 4, 7, 11, 2), "maj9"),
    "minor-ninth": ((0, 3, 7, 10, 2), "m9"),
    "dominant-ninth": ((0, 4, 7, 10, 2), "9"),
    "suspended-fourth": ((0, 5, 7), "sus4"),
    "suspended-second": ((0, 2, 7), "sus2"),
    "major-11th": ((0, 4, 7, 11, 2, 5), "maj11"),
    "minor-11th": ((0, 3, 7, 10, 2, 5), "m11"),
    "dominant-11th": ((0, 4, 7, 10, 2, 5), "11"),
    "major-13th": ((0, 4, 7, 11, 2, 9), "maj13"),
    "dominant-13th": ((0, 4, 7, 10, 2, 9), "13"),
    "minor-13th": ((0, 3, 7, 10, 2, 9), "m13"),
}


def chords_of(path):
    """Return [(root_pc, kind, label)] in order, repeats collapsed."""
    s = re.sub(r'\sxmlns="[^"]+"', "", open(path, encoding="utf-8").read())
    out = []
    for h in re.findall(r"<harmony\b[^>]*>([\s\S]*?)</harmony>", s):
        st = re.search(r"<root-step>([^<]+)", h)
        if not st:
            continue
        al = re.search(r"<root-alter>(-?\d+)", h)
        kd = re.search(r"<kind[^>]*>([^<]+)", h)
        root = (PC[st.group(1).strip()] + (int(al.group(1)) if al else 0)) % 12
        kind = (kd.group(1).strip() if kd else "major")
        label = NAMES[root] + KINDS.get(kind, ((0, 4, 7), kind))[1]
        if not out or (out[-1][0], out[-1][1]) != (root, kind):
            out.append((root, kind, label))
    return out


def tones(root, kind):
    return {(root + i) % 12 for i in KINDS.get(kind, ((0, 4, 7), ""))[0]}


def audit(path):
    ch = chords_of(path)
    name = path.split("/")[-1].replace(".musicxml", "")
    if len(ch) < 2:
        return {"name": name, "n": len(ch), "empty": True}

    common, roots, transforms = [], [], 0
    for a, b in zip(ch, ch[1:]):
        ta, tb = tones(a[0], a[1]), tones(b[0], b[1])
        common.append(len(ta & tb) / max(1, min(len(ta), len(tb))))
        iv = (b[0] - a[0]) % 12
        roots.append(iv)
        if iv == 0:
            transforms += 1

    # Functional motion: descending fifth (root up a 4th = +5) into a chord.
    desc5 = sum(1 for i in roots if i == 5)
    # V-I: dominant-quality chord resolving down a fifth.
    v_i = sum(1 for a, b in zip(ch, ch[1:])
              if a[1] in ("dominant", "dominant-ninth", "dominant-11th", "dominant-13th")
              and (b[0] - a[0]) % 12 == 5)
    # ii-V-I chain.
    ii_v_i = 0
    for a, b, c in zip(ch, ch[1:], ch[2:]):
        if (a[1].startswith("minor") and (b[0] - a[0]) % 12 == 5
                and b[1].startswith("dominant") and (c[0] - b[0]) % 12 == 5):
            ii_v_i += 1
    # Circle-of-fifths chains: 3+ consecutive descending fifths.
    cof = 0
    run = 0
    for i in roots:
        run = run + 1 if i == 5 else 0
        if run >= 2:
            cof += 1
    banned = sum(1 for _, k, _ in ch if k in ("major-11th", "major-13th"))

    # Ending: last root motion. Plagal (+7 = up a fifth/down a fourth) or
    # authentic (+5) reads as a conventional cadence.
    last = roots[-1]
    ending = ("authentic V-I" if last == 5 and ch[-2][1].startswith("dominant")
              else "authentic-type (down a 5th)" if last == 5
              else "plagal (down a 4th)" if last == 7
              else "non-cadential")

    stepwise = sum(1 for i in roots if i in (1, 2, 10, 11))
    thirds = sum(1 for i in roots if i in (3, 4, 8, 9))

    return {
        "name": name, "n": len(ch), "empty": False,
        "liquid": sum(common) / len(common),
        "transforms": transforms,
        "stepwise_pct": 100 * stepwise / len(roots),
        "third_pct": 100 * thirds / len(roots),
        "fifth_pct": 100 * desc5 / len(roots),
        "v_i": v_i, "ii_v_i": ii_v_i, "cof": cof, "banned": banned,
        "ending": ending,
        "seq": " ".join(c[2] for c in ch),
    }


def verdict(r):
    """BHL conformance band from the testable rules."""
    if r["empty"]:
        return "NO CHART", "no chord timeline - nothing to audit"
    bad = r["v_i"] + r["ii_v_i"] * 2 + r["cof"]
    # Root motion by a fourth/fifth is only functional when a dominant-quality
    # chord resolves, or when it chains. A repeated two-chord oscillation (e.g.
    # B-E-B-E) is an unrelated-pair device, not a cadence, so fifth_pct alone
    # must not condemn a piece.
    if bad >= 4:
        return "CONFLICTS", "functional progression is the organising principle"
    if bad >= 1 or r["banned"] or r["ending"] != "non-cadential":
        return "PARTIAL", "largely non-functional with conventional residue"
    if r["liquid"] >= 0.3:
        return "ALIGNED", "non-functional, common-tone connected"
    return "PARTIAL", "non-functional but harmonically disjunct"


def main():
    rows = [audit(p) for p in sys.argv[1:]]
    order = {"ALIGNED": 0, "PARTIAL": 1, "CONFLICTS": 2, "NO CHART": 3}
    rows.sort(key=lambda r: (order[verdict(r)[0]], -(r.get("liquid") or 0)))

    print("\nBHL conformance audit — testable rules only\n")
    print(f"{'piece':34} {'chords':>6} {'liquid':>7} {'step%':>6} {'5th%':>6} "
          f"{'V-I':>4} {'iiVI':>5} {'CoF':>4} {'ban':>4}  {'verdict':10} ending")
    print("-" * 118)
    for r in rows:
        v, _ = verdict(r)
        if r["empty"]:
            print(f"{r['name'][:34]:34} {r['n']:>6} {'-':>7} {'-':>6} {'-':>6} "
                  f"{'-':>4} {'-':>5} {'-':>4} {'-':>4}  {v:10} -")
            continue
        print(f"{r['name'][:34]:34} {r['n']:>6} {r['liquid']:>7.2f} "
              f"{r['stepwise_pct']:>6.0f} {r['fifth_pct']:>6.0f} {r['v_i']:>4} "
              f"{r['ii_v_i']:>5} {r['cof']:>4} {r['banned']:>4}  {v:10} {r['ending']}")

    print("\n  liquid = mean common-tone retention between successive chords (Liquid Harmony)")
    print("  step%  = root motion by step; 5th% = root motion by descending fifth")
    print("  V-I / iiVI / CoF = functional cadences and circle-of-fifths chains (BHL avoids)")
    print("  ban    = maj7(#11)-family chords (temporarily banned under BHL)")

    print("\n--- detail ---")
    for r in rows:
        v, why = verdict(r)
        print(f"\n{r['name']}  [{v}] {why}")
        if not r["empty"]:
            print(f"  transformations on a held root: {r['transforms']}")
            print(f"  {r['seq']}")


if __name__ == "__main__":
    main()
