#!/usr/bin/env python3
"""
Export a simplified chord bed from a finished MusicXML score as a type-1 MIDI file,
for drafting melody over in a DAW.

Produces four tracks:
  1  markers    - tempo, time signature and section names (A - FIELD, etc.)
  2  CHORDS     - one sustained block chord per harmonic change
  3  LEAD (ref) - the lead line that already exists, at CONCERT pitch
  4  BASS       - the written bass line, at concert pitch

Transposing parts are corrected via <transpose><chromatic>, so everything sounds
at the pitch it will actually sound. Also writes a plain-text chord sheet next to
the MIDI for anyone entering the changes by hand.

Run: python3 tools/export_chord_midi.py <file.musicxml> [...] --out midi/
"""
import argparse
import os
import re
import sys

import mido

PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Chord kind -> semitones above the root. Kept deliberately plain: this is a
# drafting bed, not a voicing exercise.
KINDS = {
    "major": (0, 4, 7),
    "minor": (0, 3, 7),
    "augmented": (0, 4, 8),
    "diminished": (0, 3, 6),
    "diminished-seventh": (0, 3, 6, 9),
    "half-diminished": (0, 3, 6, 10),
    "major-sixth": (0, 4, 7, 9),
    "minor-sixth": (0, 3, 7, 9),
    "major-seventh": (0, 4, 7, 11),
    "minor-seventh": (0, 3, 7, 10),
    "dominant": (0, 4, 7, 10),
    "major-ninth": (0, 4, 7, 11, 14),
    "minor-ninth": (0, 3, 7, 10, 14),
    "major-11th": (0, 4, 7, 11, 14, 18),
    "minor-11th": (0, 3, 7, 10, 14, 17),
    "major-13th": (0, 4, 7, 11, 14, 21),
    "minor-13th": (0, 3, 7, 10, 14, 21),
    "suspended-second": (0, 2, 7),
    "suspended-fourth": (0, 5, 7),
}
# Colour tokens in the <kind text="..."> label carry real pitch content.
# When a chord carries no text="" label, build the symbol from <kind>.
KIND_SYM = {
    "major": "", "minor": "m", "augmented": "aug", "diminished": "dim",
    "diminished-seventh": "dim7", "half-diminished": "m7b5",
    "major-sixth": "6", "minor-sixth": "m6", "major-seventh": "maj7",
    "minor-seventh": "m7", "dominant": "7", "major-ninth": "maj9",
    "minor-ninth": "m9", "major-11th": "maj11", "minor-11th": "m11",
    "major-13th": "maj13", "minor-13th": "m13",
    "suspended-second": "sus2", "suspended-fourth": "sus4",
}
ADD = {"add2": 2, "2": 2, "add9": 14, "9": 14, "add6": 9, "6": 9, "13": 21,
       "add4": 5, "11": 17, "#11": 18, "b9": 13, "#9": 15}
DROP = {"no3": (3, 4), "sus": (3, 4), "sus4": (3, 4)}
ALT = {"#5": (7, 8), "b5": (7, 6)}


def strip_ns(s):
    return re.sub(r'\sxmlns="[^"]+"', "", s)


def ascii_only(t):
    """MIDI meta text is latin-1; the scores use en/em dashes and curly quotes."""
    for a, b in (("\u2013", "-"), ("\u2014", "-"), ("\u2018", "'"), ("\u2019", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u2026", "...")):
        t = t.replace(a, b)
    return t.encode("ascii", "ignore").decode("ascii")


def part_names(s):
    out = {}
    for m in re.finditer(r'<score-part\b[^>]*id="([^"]+)"[^>]*>([\s\S]*?)</score-part>', s):
        n = re.search(r"<part-name[^>]*>([^<]*)", m.group(2))
        out[m.group(1)] = (n.group(1).strip() if n else m.group(1))
    return out


def chord_tones(root, kind, text):
    """Pitch classes as semitone offsets above the root, folded with the label."""
    iv = set(KINDS.get(kind, (0, 4, 7)))
    body = (text or "").split("/")[0]
    toks = [t.strip().lower() for t in re.split(r"[(),\s]+", body) if t.strip()]
    for t in toks:
        if t == "5":
            iv = {0, 7}
            continue
        if t.startswith("add") and t[3:] in ADD:
            t = t[3:]
        if t in DROP:
            iv -= set(DROP[t])
        if t in ALT:
            iv.discard(ALT[t][0])
            iv.add(ALT[t][1])
        if t in ADD:
            iv.add(ADD[t])
    return sorted(iv)


def harmonies(s):
    """[(bar, root_pc, bass_pc|None, label, [semitone offsets])] in bar order."""
    out = []
    for mm in re.finditer(r'<measure\b[^>]*number="(\d+)"[^>]*>([\s\S]*?)</measure>', s):
        bar = int(mm.group(1))
        for h in re.finditer(r"<harmony\b[\s\S]*?</harmony>", mm.group(2)):
            t = h.group(0)
            st = re.search(r"<root-step>([A-G])", t)
            if not st:
                continue
            al = re.search(r"<root-alter>(-?\d+)", t)
            root = (PC[st.group(1)] + (int(al.group(1)) if al else 0)) % 12
            bs = re.search(r"<bass-step>([A-G])", t)
            ba = re.search(r"<bass-alter>(-?\d+)", t)
            bass = (PC[bs.group(1)] + (int(ba.group(1)) if ba else 0)) % 12 if bs else None
            kd = re.search(r"<kind[^>]*>([^<]+)", t)
            tx = re.search(r'<kind[^>]*\btext="([^"]*)"', t)
            kind = kd.group(1).strip() if kd else "major"
            text = tx.group(1).strip() if tx else ""
            label = NAMES[root] + (text.split("/")[0] if text
                                   else KIND_SYM.get(kind, ""))
            if bass is not None and bass != root:
                label += "/" + NAMES[bass]
            out.append((bar, root, bass, label, chord_tones(root, kind, text)))
    # collapse consecutive repeats of the same sonority
    keep = []
    for e in out:
        if keep and (keep[-1][1], keep[-1][2], tuple(keep[-1][4])) == (e[1], e[2], tuple(e[4])):
            continue
        keep.append(e)
    return keep


def notes_of(s, pid):
    """[(bar, offset_in_divisions, midi, dur_divisions)] at CONCERT pitch."""
    pm = re.search(r'<part\b[^>]*id="%s"[^>]*>([\s\S]*?)</part>' % re.escape(pid), s)
    if not pm:
        return []
    body = pm.group(1)
    tr = re.search(r"<transpose>[\s\S]*?<chromatic>(-?\d+)", body)
    shift = int(tr.group(1)) if tr else 0
    out = []
    for mm in re.finditer(r'<measure\b[^>]*number="(\d+)"[^>]*>([\s\S]*?)</measure>', body):
        bar, pos = int(mm.group(1)), 0
        for n in re.finditer(r"<note\b[\s\S]*?</note>", mm.group(2)):
            t = n.group(0)
            du = re.search(r"<duration>(\d+)", t)
            dur = int(du.group(1)) if du else 0
            chord = "<chord" in t
            if "<rest" in t:
                pos += dur
                continue
            st = re.search(r"<step>([A-G])", t)
            oc = re.search(r"<octave>(\d+)", t)
            al = re.search(r"<alter>(-?\d+)", t)
            if st and oc:
                midi = (PC[st.group(1)] + (int(al.group(1)) if al else 0)
                        + 12 * (int(oc.group(1)) + 1) + shift)
                out.append((bar, pos if not chord else pos, midi, dur))
            if not chord:
                pos += dur
    return out


def voice(root, bass, iv):
    """Simple close voicing: bass note low, chord tones stacked from C3 up."""
    low = 36 + ((bass if bass is not None else root) - 0) % 12
    tones = sorted({(48 + (root + i) % 12) + (12 if i >= 12 else 0) for i in iv})
    return [low] + [t for t in tones if t != low]


def export(path, outdir):
    raw = open(path, encoding="utf-8").read()
    s = strip_ns(raw)
    stem = os.path.basename(path).replace(".musicxml", "")
    div = int(re.search(r"<divisions>(\d+)", s).group(1))
    beats = int(re.search(r"<beats>(\d+)", s).group(1))
    beat_type = int(re.search(r"<beat-type>(\d+)", s).group(1))
    tm = re.search(r'<sound[^>]*tempo="([\d.]+)"', s)
    if not tm:
        tm = re.search(r"<per-minute>([\d.]+)", s)
    tempo = float(tm.group(1)) if tm else 60.0
    total = max(int(x) for x in re.findall(r'<measure\b[^>]*number="(\d+)"', s))
    names = part_names(s)
    ids = re.findall(r'<part\b[^>]*id="([^"]+)"[^>]*>', s)

    TPB = 480
    scale = TPB / div                      # divisions -> ticks
    bar_ticks = beats * TPB

    def at(bar, off=0):
        return int((bar - 1) * bar_ticks + off * scale)

    mid = mido.MidiFile(type=1, ticks_per_beat=TPB)

    # --- track 1: tempo, metre, section markers
    t0 = mido.MidiTrack()
    t0.name = ascii_only(stem)
    t0.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo), time=0))
    t0.append(mido.MetaMessage("time_signature", numerator=beats,
                               denominator=beat_type, time=0))
    marks = []
    for mm in re.finditer(r'<measure\b[^>]*number="(\d+)"[^>]*>([\s\S]*?)</measure>', s):
        for w in re.finditer(r"<words[^>]*>([^<]*)</words>", mm.group(2)):
            txt = w.group(1).strip()
            if re.match(r"^(SECTION|[A-E]\s*[—–-])", txt, re.I) or re.match(r"^[A-E]\s", txt):
                marks.append((int(mm.group(1)), txt))
    seen = set()
    prev = 0
    for bar, txt in sorted(marks):
        if bar in seen:
            continue
        seen.add(bar)
        tick = at(bar)
        t0.append(mido.MetaMessage("marker", text=ascii_only(txt)[:60], time=tick - prev))
        prev = tick
    mid.tracks.append(t0)

    # --- track 2: chord bed
    ch = harmonies(s)
    tc = mido.MidiTrack()
    tc.name = "CHORDS"
    tc.append(mido.Message("program_change", program=4, channel=0, time=0))  # e.piano
    events = []
    for i, (bar, root, bass, label, iv) in enumerate(ch):
        start = at(bar)
        end = at(ch[i + 1][0]) if i + 1 < len(ch) else at(total + 1)
        for p in voice(root, bass, iv):
            if 0 <= p <= 127:
                events.append((start, "on", p))
                events.append((max(start + 1, end - 4), "off", p))
    prev = 0
    for tick, kind, p in sorted(events, key=lambda e: (e[0], e[1] == "on")):
        tc.append(mido.Message("note_on" if kind == "on" else "note_off",
                               note=p, velocity=64 if kind == "on" else 0,
                               channel=0, time=tick - prev))
        prev = tick
    mid.tracks.append(tc)

    # --- tracks 3 and 4: existing lead and bass, for reference
    def add_part(pid, title, prog, chan):
        ns = notes_of(s, pid)
        if not ns:
            return
        tr = mido.MidiTrack()
        tr.name = ascii_only(title)
        tr.append(mido.Message("program_change", program=prog, channel=chan, time=0))
        ev = []
        for bar, off, midi, dur in ns:
            st = at(bar, off)
            ev.append((st, "on", midi))
            ev.append((st + max(1, int(dur * scale) - 4), "off", midi))
        prev = 0
        for tick, kind, p in sorted(ev, key=lambda e: (e[0], e[1] == "on")):
            if not 0 <= p <= 127:
                continue
            tr.append(mido.Message("note_on" if kind == "on" else "note_off",
                                   note=p, velocity=88 if kind == "on" else 0,
                                   channel=chan, time=tick - prev))
            prev = tick
        mid.tracks.append(tr)

    lead = next((p for p in ids if re.search(r"flugel|trumpet", names.get(p, ""), re.I)), None)
    if lead is None:
        lead = next((p for p in ids if re.search(r"guitar", names.get(p, ""), re.I)), None)
    bassp = next((p for p in ids if re.search(r"bass", names.get(p, ""), re.I)), None)
    if lead:
        add_part(lead, f"LEAD ref - {names[lead]}", 56, 1)
    if bassp:
        add_part(bassp, f"BASS - {names[bassp]}", 32, 2)

    os.makedirs(outdir, exist_ok=True)
    mp = os.path.join(outdir, stem + "_ChordBed.mid")
    mid.save(mp)

    # --- plain-text chord sheet
    sec = {b: t for b, t in marks}
    lines = [f"{stem}   {beats}/{beat_type}   {int(tempo)} bpm   {total} bars", ""]
    for bar, root, bass, label, iv in ch:
        if bar in sec:
            lines.append("")
            lines.append(f"  [{sec[bar]}]")
        lines.append(f"  bar {bar:>3}   {label}")
    tp = os.path.join(outdir, stem + "_ChordSheet.txt")
    open(tp, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    print(f"{stem[:38]:38} {len(ch):>3} chords  {total:>3} bars  {int(tempo):>3}bpm  "
          f"{len(mid.tracks)} tracks -> {os.path.basename(mp)}")
    return mp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="midi")
    a = ap.parse_args()
    for f in a.files:
        export(f, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
