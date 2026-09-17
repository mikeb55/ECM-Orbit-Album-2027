#!/usr/bin/env python3
"""
Write a simplified chord bed in Hookpad's own MIDI shape, reverse-engineered from
Hookpad exports (C-major-Chord.mid / C-major-Chord-v2.mid), plus a text entry sheet
giving each chord as Hookpad's chord search will accept it.

Format matched from the reference files:
  type 1, ticks_per_beat = 1024, everything on channel 0
  track 0  no name: time_signature (clocks_per_click 24, notated_32nd 8), set_tempo,
           key_signature, end_of_track
  track 1  "H: Piano", program 0 - close triads re-articulated on every beat,
           velocities 102 / 51 / 70 / 51, note_off velocity 90, all notes inside A3-A4
  track 2  "B: Piano", program 0 - single root, onsets on beats 1, 2.5, 3, 4.5,
           velocities 102 / 51 / 102 / 51, all notes inside F2-E3
  (the reference third track is a "D: Basic Pop 1" drum pattern; deliberately omitted)

Chords are reduced to triads: one chord per bar, held colours forward-filled.

Run: python3 tools/export_hookpad.py <file.musicxml> [...] --out midi-hookpad/
"""
import argparse
import os
import re
import sys

import mido

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export_chord_midi import (NAMES, harmonies, strip_ns)  # noqa: E402

MAJOR = (0, 2, 4, 5, 7, 9, 11)
MINOR = (0, 2, 3, 5, 7, 8, 10)


def best_key(ch):
    """Pick the key whose scale covers the most chord tones. This harmony often has
    no key centre at all, so this is the least-bad frame for Hookpad's note grid,
    not a claim about the music."""
    best = None
    for tonic in range(12):
        for name, scale in (("", MAJOR), ("m", MINOR)):
            sc = {(tonic + d) % 12 for d in scale}
            hits = total = 0
            for _, root, bass, _, iv in ch:
                for i in iv:
                    total += 1
                    if (root + i) % 12 in sc:
                        hits += 1
            key = NAMES[tonic] + name
            if best is None or hits > best[0]:
                best = (hits, total, key)
    return best[2], (100.0 * best[0] / best[1] if best[1] else 0)

TPB = 1024
HARM_LO, HARM_HI = 57, 69          # A3 - A4, the band Hookpad voices chords into
BASS_LO = 41                       # F2; root placed into F2 - E3
FIFTHS = {-7: "Cb", -6: "Gb", -5: "Db", -4: "Ab", -3: "Eb", -2: "Bb", -1: "F",
          0: "C", 1: "G", 2: "D", 3: "A", 4: "E", 5: "B", 6: "F#", 7: "C#"}

# What Hookpad's chord search will actually accept, and what each of our colours
# has to become to get in. Values: (typed symbol, what is lost).
SUBS = [
    (r"maj9\(#11\)$", "maj7", "#11 and 9th - Hookpad has no #11"),
    (r"maj7\(#11\)$", "maj7", "#11 - Hookpad has no #11"),
    (r"maj7\(#5\)$", "aug", "the maj7 - kept the #5 as an augmented triad"),
    (r"maj7\(add2,\s*add#11\)$", "maj7", "add2 and #11"),
    (r"maj7\(add2\)$", "maj7", "add2"),
    (r"maj9\(add6\)$", "6", "the maj7 and 9th - kept the 6th"),
    (r"add2\(no3\)$", "sus2", "nothing - sus2 is the same sonority"),
    (r"maj9$", "maj7", "the 9th"),
    (r"m9$", "m7", "the 9th"),
    (r"7sus$", "sus4", "the b7"),
    (r"6\(add9\)$", "6", "the 9th"),
    (r"^([A-G][b#]?)5$", r"\1", "nothing - no power chords, use the plain triad"),
]


def hookpad_symbol(label):
    """Rewrite one of our chord labels into something Hookpad will take."""
    body, _, bass = label.partition("/")
    out, lost = body, ""
    for pat, rep, note in SUBS:
        if re.search(pat, body):
            out = re.sub(pat, rep, body) if "\\1" not in rep else re.sub(pat, rep, body)
            lost = note
            break
    return (out + ("/" + bass if bass else "")), lost


def triad(root, bass, iv):
    """Reduce to a triad and voice it closed inside A3-A4, as Hookpad does."""
    have = {i % 12 for i in iv}
    third = 4 if 4 in have else (3 if 3 in have else (2 if 2 in have else
                                (5 if 5 in have else 4)))
    fifth = 7 if 7 in have else (8 if 8 in have else (6 if 6 in have else 7))
    pcs = [(root + 0) % 12, (root + third) % 12, (root + fifth) % 12]
    best = None
    for rot in range(3):
        order = pcs[rot:] + pcs[:rot]
        low = HARM_LO + (order[0] - HARM_LO) % 12
        v, prev = [low], low
        for pc in order[1:]:
            n = prev + (pc - prev) % 12
            if n == prev:
                n += 12
            v.append(n)
            prev = n
        if max(v) <= HARM_HI:
            return v
        span = max(v) - min(v)
        if best is None or span < best[0]:
            best = (span, v)
    return best[1]


def export(path, outdir):
    s = strip_ns(open(path, encoding="utf-8").read())
    stem = os.path.basename(path).replace(".musicxml", "")
    beats = int(re.search(r"<beats>(\d+)", s).group(1))
    beat_type = int(re.search(r"<beat-type>(\d+)", s).group(1))
    tm = re.search(r'<sound[^>]*tempo="([\d.]+)"', s) or re.search(r"<per-minute>([\d.]+)", s)
    tempo = float(tm.group(1)) if tm else 60.0
    total = max(int(x) for x in re.findall(r'<measure\b[^>]*number="(\d+)"', s))

    # one chord per bar, forward-filled
    ch = harmonies(s)
    keyname, fit = best_key(ch)
    per_bar, cur = {}, None
    for bar in range(1, total + 1):
        for e in ch:
            if e[0] == bar:
                cur = e
        if cur:
            per_bar[bar] = cur

    mid = mido.MidiFile(type=1, ticks_per_beat=TPB)
    bar_ticks = beats * TPB

    t0 = mido.MidiTrack()
    t0.append(mido.MetaMessage("time_signature", numerator=beats, denominator=beat_type,
                               clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    t0.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo), time=0))
    t0.append(mido.MetaMessage("key_signature", key=keyname, time=0))
    mid.tracks.append(t0)

    HV = [102, 51, 70, 51, 70, 51, 70]                  # per beat, as measured
    BEATS_BASS = [(0.0, 102), (1.5, 51), (2.0, 102), (3.5, 51)]

    th, tb = mido.MidiTrack(), mido.MidiTrack()
    th.name, tb.name = "H: Piano", "B: Piano"
    th.append(mido.Message("program_change", program=0, channel=0, time=0))
    tb.append(mido.Message("program_change", program=0, channel=0, time=0))
    eh, eb = [], []
    for bar, (b0, root, bass, label, iv) in sorted(per_bar.items()):
        base = (bar - 1) * bar_ticks
        v = triad(root, bass, iv)
        for k in range(beats):
            on = base + k * TPB
            off = on + int(0.8 * TPB)
            for p in v:
                eh.append((on, 1, p, HV[k % len(HV)]))
                eh.append((off, 0, p, 90))
        bnote = BASS_LO + (((bass if bass is not None else root) - BASS_LO) % 12)
        for off_beats, vel in BEATS_BASS:
            if off_beats >= beats:
                continue
            on = base + int(off_beats * TPB)
            eb.append((on, 1, bnote, vel))
            eb.append((on + int(0.8 * TPB), 0, bnote, 90))

    for tr, ev in ((th, eh), (tb, eb)):
        prev = 0
        for tick, on, p, vel in sorted(ev, key=lambda e: (e[0], -e[1])):
            tr.append(mido.Message("note_on" if on else "note_off", note=p,
                                   velocity=vel, channel=0, time=tick - prev))
            prev = tick
        mid.tracks.append(tr)

    os.makedirs(outdir, exist_ok=True)
    mp = os.path.join(outdir, stem + "_Hookpad.mid")
    mid.save(mp)

    # ---- text entry sheet: what to type into Hookpad's chord staff
    lines = [f"{stem}",
             f"set Hookpad to:   key {keyname or 'C'}   {beats}/{beat_type}   "
             f"{int(tempo)} bpm   {total} bars",
             f"({fit:.0f}% of the chord tones fall inside that scale - "
             f"enter chords by letter name in the chord search, not by typing 1-7)", "",
             f"{'bar':>5}  {'written':22} {'type into Hookpad':18} what Hookpad drops", "-" * 86]
    for bar, root, bass, label, iv in ch:
        sym, lost = hookpad_symbol(label)
        lines.append(f"{bar:>5}  {label:22} {sym:18} {lost}")
    tp = os.path.join(outdir, stem + "_Hookpad_EntrySheet.txt")
    open(tp, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    losses = sum(1 for e in ch if hookpad_symbol(e[3])[1] and "nothing" not in
                 hookpad_symbol(e[3])[1])
    print(f"{stem[:38]:38} {len(ch):>3} chords, {total:>3} bars, "
          f"key {keyname:>3} ({fit:.0f}% fit), {losses:>2} altered -> {os.path.basename(mp)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="midi-hookpad")
    a = ap.parse_args()
    for f in a.files:
        export(f, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
