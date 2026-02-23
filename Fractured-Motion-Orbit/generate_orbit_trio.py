#!/usr/bin/env python3
"""Generate Fractured Motion Orbit Trio (Flugelhorn, Guitar, Upright Bass)."""
import xml.etree.ElementTree as ET
from pathlib import Path

# Import from melody generator
from generate_orbit_melody import CHORDS, MELODY, note_elem, rest_elem

NS = "http://www.musicxml.org/ns/3.1"

# Guitar open voicings: list of (step, alter, octave) per chord - 3-4 notes, no doubled thirds
# Bm(add9): B D F# A C# -> B3 F#4 A4 or D4 F#4 A4
# D(add4): D F# A G
# Fmaj7(add4): F A C E G
# Cmaj7(#11): C E G B F#
# Eb(add9): Eb G Bb F
GUITAR_VOICINGS = {
    "Bm(add9)": [("B", 0, 3), ("F", 1, 4), ("A", 0, 4)],
    "Bm(add9)/C": [("C", 0, 3), ("F", 1, 4), ("A", 0, 4)],
    "Bm(add9)/A": [("A", 0, 3), ("B", 0, 4), ("F", 1, 4)],
    "Bm(add9)/F#": [("F", 1, 3), ("A", 0, 4), ("B", 0, 4)],
    "D(add4)": [("D", 0, 3), ("F", 1, 4), ("A", 0, 4), ("G", 0, 4)],
    "D6": [("D", 0, 3), ("F", 1, 4), ("B", 0, 4)],
    "Bbmaj(#11)": [("B", -1, 3), ("F", 0, 4), ("A", -1, 4)],
    "D(add4)/C": [("C", 0, 3), ("D", 0, 4), ("F", 1, 4)],
    "Fmaj7(add4)": [("F", 0, 3), ("A", 0, 4), ("C", 0, 5), ("G", 0, 4)],
    "F(add4)": [("F", 0, 3), ("A", 0, 4), ("C", 0, 5)],
    "F(add4)/A": [("A", 0, 3), ("C", 0, 4), ("F", 0, 4)],
    "Fmaj7(add4)/C": [("C", 0, 3), ("F", 0, 4), ("A", 0, 4)],
    "Cmaj7(#11)": [("C", 0, 3), ("E", 0, 4), ("G", 0, 4), ("F", 1, 4)],
    "C(add4)": [("C", 0, 3), ("E", 0, 4), ("G", 0, 4)],
    "C(add4)/G": [("G", 0, 3), ("C", 0, 4), ("E", 0, 4)],
    "C(add4)/E": [("E", 0, 3), ("G", 0, 4), ("C", 0, 5)],
    "Eb(add9)": [("E", -1, 3), ("G", 0, 4), ("B", -1, 4)],
    "Eb(add4)": [("E", -1, 3), ("G", 0, 4), ("A", -1, 4)],
}

# Bass: root or slash root. Pedal in A (B or F#), sparse in B, chromatic E->Eb into plateau
BASS = [
    "B", "C", "B", "A", "B", "C", "B", "F#", "B", "C", "B", "A", "B", "C", "B", "F#",
    "D", "D", "D", "Bb", "D", "C", "D", "F", "F", "F", "A", "F", "F", "C", "F", "F",
    "C", "C", "C", "G", "C", "C", "C", "E", "C", "C", "C", "C", "E", "Eb",  # bar 44 E, 45 Eb chromatic
    "B", "C", "B", "A", "B", "F#", "B", "C", "B", "A", "B", "C", "B", "F#", "B", "C", "B", "A",
]


def bass_note(root: str, octave: int = 2, alter: int = 0) -> tuple:
    m = {"B": ("B", 0), "C": ("C", 0), "D": ("D", 0), "E": ("E", 0), "Eb": ("E", -1), "F": ("F", 0), "F#": ("F", 1), "G": ("G", 0), "A": ("A", 0), "Bb": ("B", -1)}
    s, a = m.get(root, ("B", 0))
    return (s, a if alter == 0 else alter, octave)


def chord_to_bass(chord: str) -> str:
    if "/" in chord:
        return chord.split("/")[-1].replace("#", "").replace("b", "")
    base = chord.split("(")[0]
    return base[0] if base else "B"


def main(version: int = 1):
    root = ET.Element("score-partwise", version="3.1", xmlns=NS)
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = "Fractured Motion – Orbit Version (Trio)"
    ET.SubElement(work, "creator", type="composer").text = "Mike Bryant"
    ident = ET.SubElement(root, "identification")
    enc = ET.SubElement(ident, "encoding")
    ET.SubElement(enc, "encoding-date").text = "2026-02-23"
    ET.SubElement(enc, "software").text = f"Fractured Motion Orbit Trio V{version} / GCE-Jazz V1.0"
    defaults = ET.SubElement(root, "defaults")
    scaling = ET.SubElement(defaults, "scaling")
    ET.SubElement(scaling, "millimeters").text = "7.0"
    ET.SubElement(scaling, "tenths").text = "40"
    plist = ET.SubElement(root, "part-list")
    for pid, pname in [("P1", "Flugelhorn in Bb"), ("P2", "Guitar"), ("P3", "Upright Bass")]:
        sp = ET.SubElement(plist, "score-part", id=pid)
        ET.SubElement(sp, "part-name").text = pname

    def add_measure(part, m, attrs_first=False, chord=None):
        measure = ET.SubElement(part, "measure", number=str(m + 1))
        if attrs_first:
            a = ET.SubElement(measure, "attributes")
            ET.SubElement(a, "divisions").text = "4"
            k = ET.SubElement(a, "key")
            ET.SubElement(k, "fifths").text = "-3"
            ET.SubElement(k, "mode").text = "minor"
            t = ET.SubElement(a, "time")
            ET.SubElement(t, "beats").text = "4"
            ET.SubElement(t, "beat-type").text = "4"
            if part == parts["P1"]:
                c = ET.SubElement(a, "clef")
                ET.SubElement(c, "sign").text = "G"
                ET.SubElement(c, "line").text = "2"
                tr = ET.SubElement(a, "transpose")
                ET.SubElement(tr, "diatonic").text = "-2"
                ET.SubElement(tr, "chromatic").text = "-2"
                d = ET.SubElement(measure, "direction", placement="above")
                dt = ET.SubElement(d, "direction-type")
                metro = ET.SubElement(dt, "metronome")
                ET.SubElement(metro, "beat-unit").text = "quarter"
                ET.SubElement(metro, "per-minute").text = "72"
                ET.SubElement(measure, "sound", tempo="72")
            elif part == parts["P2"]:
                c = ET.SubElement(a, "clef")
                ET.SubElement(c, "sign").text = "G"
                ET.SubElement(c, "line").text = "2"
            else:
                c = ET.SubElement(a, "clef")
                ET.SubElement(c, "sign").text = "F"
                ET.SubElement(c, "line").text = "4"
        if chord:
            d = ET.SubElement(measure, "direction", placement="above")
            dt = ET.SubElement(d, "direction-type")
            ET.SubElement(dt, "words").text = chord
        return measure

    parts = {pid: ET.SubElement(root, "part", id=pid) for pid in ["P1", "P2", "P3"]}

    for m in range(64):
        chord = CHORDS[m]
        # Flugelhorn
        meas = add_measure(parts["P1"], m, attrs_first=(m == 0), chord=chord)
        for note_tup in (MELODY[m] if isinstance(MELODY[m][0], (list, tuple)) else (MELODY[m],)):
            if note_tup[0] == "R":
                _, _, _, dur, ntype = note_tup
                meas.append(rest_elem(dur, ntype))
            else:
                step, alter, octave, dur, ntype = note_tup[:5]
                dot = note_tup[5] if len(note_tup) > 5 else False
                n = note_elem(step, alter, octave, dur, ntype, dot)
                dyn = ET.SubElement(n, "dynamics")
                ET.SubElement(dyn, "pp")
                meas.append(n)

        # Guitar
        meas = add_measure(parts["P2"], m, attrs_first=(m == 0), chord=None)
        base = chord.split("/")[0]
        voicing = GUITAR_VOICINGS.get(base, GUITAR_VOICINGS["Bm(add9)"])
        for i, (s, a, o) in enumerate(voicing[:4]):
            n = note_elem(s, a, o, 16, "whole")
            if i > 0:
                n.insert(0, ET.Element("chord"))
            dyn = ET.SubElement(n, "dynamics")
            ET.SubElement(dyn, "pp")
            meas.append(n)

        # Bass
        meas = add_measure(parts["P3"], m, attrs_first=(m == 0), chord=None)
        bass_root = BASS[m] if m < len(BASS) else chord_to_bass(chord)
        s, a = {"B": ("B", 0), "C": ("C", 0), "D": ("D", 0), "E": ("E", 0), "Eb": ("E", -1),
                "F": ("F", 0), "F#": ("F", 1), "G": ("G", 0), "A": ("A", 0), "Bb": ("B", -1)}.get(bass_root, ("B", 0))
        bn = note_elem(s, a, 2, 16, "whole")
        dyn = ET.SubElement(bn, "dynamics")
        ET.SubElement(dyn, "pp")
        meas.append(bn)

    tree = ET.ElementTree(root)
    out = Path(__file__).parent / "MusicXML" / f"fractured_motion_orbit_trio_v{version}.musicxml"
    tree.write(str(out), encoding="unicode", method="xml", xml_declaration=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    import sys
    v = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    main(v)
