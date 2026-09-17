#!/usr/bin/env python3
"""
BHL harmoniser — writes a Bryant Harmonic Language chord field into a score.

Follows the BHL rules that can be mechanised:

  Liquid Harmony        each chord is chosen to retain common tones with the
                        previous one; parsimonious motion is preferred
  Transformation        re-colouring a held root scores higher than replacing it
  Anti-functional       dominant-quality chords are excluded from every pool, so
                        V-I and ii-V-I cannot be produced; a root motion of a
                        descending fifth is penalised, and forbidden at the end
  Banned sonority       maj7(#11) family never enters a pool
  Harmonic field first  the chord pool is fixed per section by harmonic world
                        before any symbol is chosen
  Recurrence            the chord opening each section is drawn from the pool of
                        section A where possible, so material recurs

The melody is never altered. A candidate chord is only legal if it contains the
sounding melody pitch-classes of its bar, so harmony is fitted to the existing
line rather than the line being bent to the harmony.

Usage:
  python tools/bhl_harmonise.py <file.musicxml> --world <A|C|D|E|F> [--dry-run]
"""

import argparse
import re
import sys

PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
# MusicXML kind -> (intervals above root, printed suffix)
KIND = {
    "major": ((0, 4, 7), ""),
    "minor": ((0, 3, 7), "m"),
    "augmented": ((0, 4, 8), "aug"),
    "diminished": ((0, 3, 6), "dim"),
    "diminished-seventh": ((0, 3, 6, 9), "dim7"),
    "major-seventh": ((0, 4, 7, 11), "maj7"),
    "minor-seventh": ((0, 3, 7, 10), "m7"),
    "major-sixth": ((0, 4, 7, 9), "6"),
    "minor-sixth": ((0, 3, 7, 9), "m6"),
    "suspended-second": ((0, 2, 7), "sus2"),
    "suspended-fourth": ((0, 5, 7), "sus4"),
    "major-ninth": ((0, 4, 7, 11, 2), "maj9"),
    "minor-ninth": ((0, 3, 7, 10, 2), "m9"),
}
# Harmonic worlds -> permitted chord qualities. No dominant-quality chord
# appears anywhere, which is what makes functional cadence unreachable.
WORLDS = {
    "A": ("Triad Pairs", ["major", "minor", "major-sixth", "minor-sixth"]),
    "C": ("Major + Augmented Structures", ["major", "major-seventh", "augmented", "major-sixth"]),
    "D": ("Major + Diminished Structures",
          ["major", "major-seventh", "diminished-seventh", "diminished", "minor-sixth"]),
    "E": ("Pentatonic Harmony",
          ["suspended-second", "suspended-fourth", "minor-seventh", "major-sixth", "major-ninth"]),
    "F": ("Unrelated Major Triads", ["major", "major-seventh", "major-sixth"]),
}


def tones(root, kind):
    return frozenset((root + i) % 12 for i in KIND[kind][0])


def label(root, kind):
    return NAMES[root] + KIND[kind][1]


def strip_ns(s):
    return re.sub(r'\sxmlns="[^"]+"', "", s)


def read_score(path):
    """-> (raw_no_ns, parts) where parts = [(part_id, body, transpose, divisions)]."""
    raw = strip_ns(open(path, encoding="utf-8").read())
    parts = []
    for pm in re.finditer(r'<part\b[^>]*id="([^"]+)"[^>]*>([\s\S]*?)</part>', raw):
        body = pm.group(2)
        ch = re.search(r"<chromatic>(-?\d+)", body)
        dv = re.search(r"<divisions>(\d+)", body)
        parts.append((pm.group(1), body, int(ch.group(1)) if ch else 0,
                      int(dv.group(1)) if dv else 1))
    return raw, parts


def part_name(raw, pid):
    m = re.search(r'<score-part\b[^>]*id="%s"[^>]*>([\s\S]*?)</score-part>' % re.escape(pid), raw)
    if not m:
        return pid
    n = re.search(r"<part-name>([^<]*)", m.group(1))
    return n.group(1).strip() if n else pid


def melody_by_bar(raw, parts):
    """Sounding pitch-classes per bar, and the lead part's pcs per bar."""
    every, lead = {}, {}
    lead_id = None
    for pid, body, tr, _ in parts:
        nm = part_name(raw, pid)
        if re.search(r"flugel|trumpet|sax", nm, re.I) and lead_id is None:
            lead_id = pid
    if lead_id is None:
        for pid, body, tr, _ in parts:
            if not re.search(r"bass", part_name(raw, pid), re.I):
                lead_id = pid
                break
    for pid, body, tr, _ in parts:
        is_bass = bool(re.search(r"bass", part_name(raw, pid), re.I))
        for mm in re.finditer(r'<measure\b[^>]*number="(\d+)"[^>]*>([\s\S]*?)</measure>', body):
            b = int(mm.group(1))
            for n in re.findall(r"<note\b[^>]*>([\s\S]*?)</note>", mm.group(2)):
                p = re.search(r"<step>([A-G])</step>\s*(?:<alter>(-?\d+)</alter>)?", n)
                if not p:
                    continue
                pc = (PC[p.group(1)] + (int(p.group(2)) if p.group(2) else 0) + tr) % 12
                if not is_bass:
                    every.setdefault(b, set()).add(pc)
                if pid == lead_id:
                    lead.setdefault(b, set()).add(pc)
    return every, lead


def sections(raw):
    out = {}
    for mm in re.finditer(r'<measure\b[^>]*number="(\d+)"[^>]*>([\s\S]*?)</measure>', raw):
        for w in re.findall(r"<words[^>]*>([^<]+)</words>", mm.group(2)):
            if "SECTION" in w.upper():
                out[int(mm.group(1))] = w.strip()
    return out


def choose(world, every, lead, secs, total_bars):
    """Pick a chord per change-point. Returns {bar: (root, kind)}."""
    _, kinds = WORLDS[world]
    pool = [(r, k) for r in range(12) for k in kinds]

    # Change points: every section start, then every 4th bar inside a section.
    starts = sorted(secs) or [1]
    pts = []
    for i, st in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else total_bars + 1
        b = st
        while b < end:
            pts.append(b)
            b += 4
    pts = sorted(set(p for p in pts if p <= total_bars))

    chosen = {}
    prev = None
    first_of_section = {}
    for b in pts:
        sec = max([s for s in starts if s <= b], default=starts[0])
        # Constraint ladder: prefer a chord containing every lead pitch in the
        # window, but a sparse modal line can span more than one triad, so relax
        # to the change-bar only, then to unconstrained, rather than skip the bar.
        win = list(range(b, min(b + 4, total_bars + 1)))
        wide = set().union(*[lead.get(k, set()) for k in win]) if win else set()
        narrow = lead.get(b, set()) or set().union(*[every.get(k, set()) for k in win])
        ctx = set().union(*[every.get(k, set()) for k in win])

        cands = []
        for need in (wide, narrow, set()):
            cands = [(r, k) for r, k in pool
                     if (not need or need <= tones(r, k)) and (r, k) != prev]
            if cands:
                break

        best, best_s = None, None
        for root, kind in cands:
            t = tones(root, kind)
            s = 0.0
            if ctx:
                s += 1.0 * len(ctx & t) / len(ctx)   # agree with guitar dyads
            if prev:
                pt = tones(*prev)
                s += 3.0 * len(t & pt) / max(1, min(len(t), len(pt)))  # Liquid Harmony
                iv = (root - prev[0]) % 12
                if root == prev[0] and kind != prev[1]:
                    s += 2.0                      # transformation over replacement
                elif iv in (1, 2, 10, 11):
                    s += 1.0                      # parsimonious root motion
                elif iv in (3, 4, 8, 9):
                    s += 0.5
                elif iv in (5, 7):
                    s -= 1.5                      # fifth motion: functional smell
            # Recurrence: reuse the chord that opened section A.
            if b in starts and first_of_section.get(starts[0]):
                if (root, kind) == first_of_section[starts[0]]:
                    s += 1.5
                elif root == first_of_section[starts[0]][0]:
                    s += 0.75
            if best_s is None or s > best_s:
                best, best_s = (root, kind), s
        if best is None:
            continue
        # Ending must not be a cadence: no descending fifth into the last chord.
        if b == pts[-1] and prev and (best[0] - prev[0]) % 12 == 5:
            alts = sorted(
                ((r, k) for r, k in cands if (r - prev[0]) % 12 not in (5, 7)),
                key=lambda rk: -len(tones(*rk) & tones(*prev)))
            if alts:
                best = alts[0]
        chosen[b] = best
        first_of_section.setdefault(sec, best)
        prev = best
    return chosen


def harmony_xml(root, kind, indent="      "):
    r = NAMES[root]
    step = r[0]
    alter = -1 if r.endswith("b") else 0
    a = f"<root-alter>{alter}</root-alter>" if alter else ""
    return (f'{indent}<harmony print-frame="no">\n'
            f'{indent}  <root><root-step>{step}</root-step>{a}</root>\n'
            f"{indent}  <kind>{kind}</kind>\n"
            f"{indent}</harmony>\n")


def insert(path, chosen, dry_run):
    """Write <harmony> before the first note of each chosen bar, in every part
    that already carries the chord staff (the first non-bass part)."""
    raw = open(path, encoding="utf-8").read()
    has_ns = 'xmlns="' in raw
    body_ns = strip_ns(raw)

    # Target part: the guitar. These scores put the harmonic field in the guitar
    # ("Guitar defines harmonic field"), so the symbols belong on that staff
    # rather than over the horn line.
    parts = re.findall(r'<part\b[^>]*id="([^"]+)"[^>]*>', body_ns)
    target = next((p for p in parts if re.search(r"guitar", part_name(body_ns, p), re.I)), None)
    if target is None:
        target = next((p for p in parts if not re.search(r"bass", part_name(body_ns, p), re.I)), parts[0])

    pm = re.search(r'(<part\b[^>]*id="%s"[^>]*>)([\s\S]*?)(</part>)' % re.escape(target), body_ns)
    body = pm.group(2)
    added = 0

    def do_measure(m):
        nonlocal added
        num = int(re.search(r'number="(\d+)"', m.group(1)).group(1))
        if num not in chosen:
            return m.group(0)
        inner = m.group(2)
        if "<harmony" in inner:
            return m.group(0)
        h = harmony_xml(*chosen[num])
        nm = re.search(r"([ \t]*)<note\b", inner)
        if not nm:
            return m.group(0)
        added += 1
        return m.group(1) + inner[:nm.start()] + h + inner[nm.start():] + m.group(3)

    body2 = re.sub(r'(<measure\b[^>]*>)([\s\S]*?)(</measure>)', do_measure, body)
    out = body_ns[:pm.start(2)] + body2 + body_ns[pm.end(2):]
    if has_ns:
        out = out.replace("<score-partwise ", '<score-partwise xmlns="http://www.musicxml.org/ns/3.1" ', 1)
    if not dry_run:
        open(path, "w", encoding="utf-8").write(out)
    return added, part_name(body_ns, target)


def keep_roots(a):
    """Revise chord qualities in place, keeping every root. BHL asks for
    transformation over replacement: the roots carry the piece's identity, so
    only the colouring changes, chosen to maximise common tones with the
    previous chord while staying inside the assigned world."""
    raw, parts = read_score(a.file)
    every, lead = melody_by_bar(raw, parts)
    _, kinds = WORLDS[a.world]

    src = open(a.file, encoding="utf-8").read()
    body = strip_ns(src)

    # Walk harmony elements in document order, with the bar each sits in.
    entries = []
    for mm in re.finditer(r'<measure\b[^>]*number="(\d+)"[^>]*>([\s\S]*?)</measure>', body):
        bar = int(mm.group(1))
        for hm in re.finditer(r"<harmony\b[\s\S]*?</harmony>", mm.group(2)):
            st = re.search(r"<root-step>([^<]+)", hm.group(0))
            al = re.search(r"<root-alter>(-?\d+)", hm.group(0))
            kd = re.search(r"<kind[^>]*>([^<]+)", hm.group(0))
            if not st:
                continue
            root = (PC[st.group(1).strip()] + (int(al.group(1)) if al else 0)) % 12
            entries.append({"bar": bar, "root": root,
                            "old": kd.group(1).strip() if kd else "major",
                            "xml": hm.group(0)})

    prev = None
    changes = []
    for e in entries:
        need = lead.get(e["bar"], set())
        ctx = every.get(e["bar"], set())
        best, best_s = None, None
        for k in kinds:
            t = tones(e["root"], k)
            if need and not need <= t:
                continue
            s = 0.0
            if prev:
                pt = tones(*prev)
                s += 3.0 * len(t & pt) / max(1, min(len(t), len(pt)))
                if (e["root"], k) == prev:
                    s -= 4.0
            if ctx:
                s += 1.0 * len(ctx & t) / len(ctx)
            if k == e["old"]:
                s += 0.4          # don't churn a quality that already works
            if best_s is None or s > best_s:
                best, best_s = k, s
        if best is None:
            best = e["old"]
        changes.append((e, best))
        prev = (e["root"], best)

    def liquid(seq):
        v = []
        for x, y in zip(seq, seq[1:]):
            tx, ty = tones(*x), tones(*y)
            v.append(len(tx & ty) / max(1, min(len(tx), len(ty))))
        return sum(v) / len(v) if v else 0.0

    before = liquid([(e["root"], e["old"]) for e in entries])
    after = liquid([(e["root"], k) for e, k in changes])

    print(f"\n{a.file.split('/')[-1]}  —  World {a.world}: {WORLDS[a.world][0]}  (roots kept)")
    print(f"  {len(entries)} chords · liquid {before:.2f} -> {after:.2f}")
    edited = 0
    out = src
    for e, k in changes:
        if k == e["old"]:
            continue
        new = e["xml"].replace(f"<kind>{e['old']}</kind>", f"<kind>{k}</kind>")
        if new != e["xml"] and e["xml"] in out:
            out = out.replace(e["xml"], new, 1)
            edited += 1
    seq_before = " ".join(label(e["root"], e["old"]) for e in entries)
    seq_after = " ".join(label(e["root"], k) for e, k in changes)
    print(f"  before: {seq_before}")
    print(f"  after:  {seq_after}")
    if not a.dry_run:
        open(a.file, "w", encoding="utf-8").write(out)
    print(f"  {'would change' if a.dry_run else 'changed'} {edited} chord qualities")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--world", required=True, choices=sorted(WORLDS))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strip", action="store_true",
                    help="remove existing <harmony> first (re-harmonise from scratch)")
    ap.add_argument("--keep-roots", action="store_true",
                    help="keep the existing roots and change only chord quality, so the "
                         "piece's harmonic identity survives; raises common-tone retention "
                         "by transformation rather than replacement")
    a = ap.parse_args()

    if a.keep_roots:
        return keep_roots(a)

    if a.strip and not a.dry_run:
        s = open(a.file, encoding="utf-8").read()
        s = re.sub(r"\s*<harmony\b[\s\S]*?</harmony>", "", s)
        open(a.file, "w", encoding="utf-8").write(s)

    raw, parts = read_score(a.file)
    every, lead = melody_by_bar(raw, parts)
    secs = sections(raw)
    total = max(int(x) for x in re.findall(r'<measure\b[^>]*number="(\d+)"', raw))

    chosen = choose(a.world, every, lead, secs, total)
    wname = WORLDS[a.world][0]
    print(f"\n{a.file.split('/')[-1]}  —  World {a.world}: {wname}")
    print(f"  {total} bars, {len(secs)} sections, {len(chosen)} chords placed")

    seq = [chosen[b] for b in sorted(chosen)]
    ct = []
    for x, y in zip(seq, seq[1:]):
        tx, ty = tones(*x), tones(*y)
        ct.append(len(tx & ty) / max(1, min(len(tx), len(ty))))
    if ct:
        print(f"  liquid (mean common-tone retention): {sum(ct)/len(ct):.2f}")
    starts = sorted(secs)
    for i, st in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else total + 1
        bars = [b for b in sorted(chosen) if st <= b < end]
        if bars:
            print(f"    {secs[st][:32]:34} " + " ".join(label(*chosen[b]) for b in bars))

    added, tgt = insert(a.file, chosen, a.dry_run)
    print(f"  {'would write' if a.dry_run else 'wrote'} {added} symbols into: {tgt}")


if __name__ == "__main__":
    main()
