#!/usr/bin/env python3
"""Generate Fractured Motion Orbit Version MusicXML with GCE-compliant melody."""
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "http://www.musicxml.org/ns/3.1"

CHORDS = [
    "Bm(add9)", "Bm(add9)/C", "Bm(add9)", "Bm(add9)/A", "Bm(add9)", "Bm(add9)/C",
    "Bm(add9)", "Bm(add9)/F#", "Bm(add9)", "Bm(add9)/C", "Bm(add9)", "Bm(add9)/A",
    "Bm(add9)", "Bm(add9)/C", "Bm(add9)", "Bm(add9)/F#",
    "D(add4)", "D6", "D(add4)", "Bbmaj(#11)", "D(add4)", "D(add4)/C",
    "D(add4)", "Fmaj7(add4)", "F(add4)", "Fmaj7(add4)", "F(add4)/A", "Fmaj7(add4)",
    "F(add4)", "Fmaj7(add4)/C", "F(add4)", "Fmaj7(add4)",
    "Cmaj7(#11)", "C(add4)", "Cmaj7(#11)", "C(add4)/G", "Cmaj7(#11)", "C(add4)",
    "Cmaj7(#11)", "C(add4)/E", "Cmaj7(#11)", "C(add4)", "Cmaj7(#11)", "C(add4)",
    "Eb(add9)", "Eb(add4)",
    "Bm(add9)", "Bm(add9)/C", "Bm(add9)", "Bm(add9)/A", "Bm(add9)", "Bm(add9)/F#",
    "Bm(add9)", "Bm(add9)/C", "Bm(add9)", "Bm(add9)/A", "Bm(add9)", "Bm(add9)/C",
    "Bm(add9)", "Bm(add9)/F#", "Bm(add9)", "Bm(add9)/C", "Bm(add9)", "Bm(add9)",
]

# Melody: (step, alter, octave, duration, type)
# duration: 4=quarter, 8=half, 16=whole; 2=eighth
# Motivic cell A-B-C-B-A-F# = A4 B4 C#5 B4 A4 F#4
MELODY = [
    # A 1-16: B minor, motivic statement, long tones
    (("B", 0, 4, 8, "half"), ("A", 0, 4, 4, "quarter"), ("C", 1, 5, 4, "quarter")),  # 1
    (("B", 0, 4, 8, "half"), ("A", 0, 4, 8, "half")),  # 2
    (("F", 1, 4, 16, "whole")),  # 3
    (("A", 0, 4, 8, "half"), ("B", 0, 4, 4, "quarter"), ("C", 1, 5, 4, "quarter")),  # 4
    (("B", 0, 4, 16, "whole")),  # 5
    (("A", 0, 4, 8, "half"), ("G", 0, 4, 8, "half")),  # 6
    (("F", 1, 4, 4, "quarter"), ("E", 0, 4, 4, "quarter"), ("D", 0, 4, 8, "half")),  # 7
    (("E", 0, 4, 8, "half"), ("F", 1, 4, 8, "half")),  # 8
    (("A", 0, 4, 16, "whole")),  # 9
    (("B", 0, 4, 8, "half"), ("C", 1, 5, 8, "half")),  # 10
    (("B", 0, 4, 16, "whole")),  # 11
    (("A", 0, 4, 8, "half"), ("F", 1, 4, 8, "half")),  # 12
    (("E", 0, 4, 16, "whole")),  # 13
    (("F", 1, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("A", 0, 4, 8, "half")),  # 14
    (("B", 0, 4, 16, "whole")),  # 15
    (("A", 0, 4, 8, "half"), ("B", 0, 4, 4, "quarter"), ("F", 1, 4, 4, "quarter")),  # 16
    # B 17-32: D/F Lydian pivot
    (("D", 0, 5, 8, "half"), ("F", 1, 5, 8, "half")),  # 17
    (("A", 0, 5, 16, "whole")),  # 18 - pivot tone
    (("G", 0, 5, 8, "half"), ("A", 0, 5, 8, "half")),  # 19
    (("F", 1, 5, 16, "whole")),  # 20
    (("A", 0, 5, 8, "half"), ("B", 0, 5, 4, "quarter"), ("C", 0, 5, 4, "quarter")),  # 21 - F Lydian hint
    (("C", 0, 5, 16, "whole")),  # 22
    (("A", 0, 4, 8, "half"), ("F", 0, 4, 8, "half")),  # 23 - into F
    (("F", 0, 4, 16, "whole")),  # 24 - F Lydian
    (("A", 0, 4, 8, "half"), ("B", 0, 4, 8, "half")),  # 25
    (("C", 0, 5, 16, "whole")),  # 26
    (("B", 0, 4, 8, "half"), ("A", 0, 4, 8, "half")),  # 27
    (("G", 0, 4, 16, "whole")),  # 28
    (("A", 0, 4, 8, "half"), ("C", 0, 5, 8, "half")),  # 29
    (("B", 0, 4, 16, "whole")),  # 30
    (("C", 0, 5, 8, "half"), ("D", 0, 5, 8, "half")),  # 31
    (("E", 0, 5, 16, "whole")),  # 32
    # B' 33-44: C suspended - REGISTRAL LIFT
    (("G", 0, 5, 8, "half"), ("E", 0, 5, 8, "half")),  # 33
    (("E", 0, 5, 8, "half"), ("E", 0, 6, 8, "half")),  # 34 - intervallic expansion (octave)
    (("G", 0, 5, 4, "quarter"), ("A", 0, 5, 4, "quarter"), ("B", 0, 5, 8, "half")),  # 35 - lift
    (("R", 0, 0, 4, "quarter"), ("B", 0, 5, 12, "half", True)),  # 36 - rhythmic displacement
    (("A", 0, 5, 8, "half"), ("G", 0, 5, 8, "half")),  # 37
    (("E", 0, 5, 16, "whole")),  # 38
    (("F", 1, 5, 8, "half"), ("G", 0, 5, 8, "half")),  # 39 - #11 colour
    (("G", 0, 5, 16, "whole")),  # 40
    (("E", 0, 5, 8, "half"), ("D", 0, 5, 8, "half")),  # 41
    (("C", 0, 5, 16, "whole")),  # 42
    (("D", 0, 5, 8, "half"), ("E", 0, 5, 4, "quarter"), ("C", 0, 5, 4, "quarter")),  # 43
    (("B", 0, 4, 16, "whole")),  # 44 - descent begins
    # Plateau 45-46: Eb - destabilising
    (("G", 0, 5, 4, "quarter"), ("G", 1, 5, 4, "quarter"), ("B", -1, 4, 8, "half")),  # 45 - G# destabilising
    (("F", 0, 4, 8, "half"), ("E", -1, 4, 8, "half")),  # 46 Eb
    # A' 47-64: fracture-return
    (("B", 0, 4, 16, "whole")),  # 47 - direct return
    (("A", 0, 4, 8, "half"), ("F", 1, 4, 8, "half")),  # 48
    (("E", 0, 4, 16, "whole")),  # 49
    (("A", 0, 4, 8, "half"), ("B", 0, 4, 8, "half")),  # 50
    (("C", 1, 5, 16, "whole")),  # 51 - motivic recall C#
    (("B", 0, 4, 8, "half"), ("A", 0, 4, 8, "half")),  # 52
    (("F", 1, 4, 16, "whole")),  # 53
    (("A", 0, 4, 8, "half"), ("G", 0, 4, 8, "half")),  # 54
    (("E", 0, 4, 16, "whole")),  # 55
    (("F", 1, 4, 4, "quarter"), ("A", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 56
    (("B", 0, 4, 16, "whole")),  # 57
    (("A", 0, 4, 8, "half"), ("F", 1, 4, 4, "quarter"), ("E", 0, 4, 4, "quarter")),  # 58
    (("D", 0, 4, 16, "whole")),  # 59
    (("E", 0, 4, 8, "half"), ("F", 1, 4, 8, "half")),  # 60
    (("A", 0, 4, 8, "half"), ("F", 1, 4, 4, "quarter"), ("E", 0, 4, 4, "quarter")),  # 61 - motif alteration
    (("B", 0, 4, 4, "quarter"), ("A", 0, 4, 4, "quarter"), ("C", 1, 5, 4, "quarter"), ("B", 0, 4, 4, "quarter")),  # 62
    (("B", 0, 4, 8, "half"), ("F", 1, 4, 8, "half")),  # 63
    (("A", 0, 4, 16, "whole")),  # 64 - afterglow
]


def rest_elem(duration: int, ntype: str) -> ET.Element:
    n = ET.Element("note")
    ET.SubElement(n, "rest")
    ET.SubElement(n, "duration").text = str(duration)
    ET.SubElement(n, "voice").text = "1"
    ET.SubElement(n, "type").text = ntype
    return n


def note_elem(step: str, alter: int, octave: int, duration: int, ntype: str, dot: bool = False) -> ET.Element:
    n = ET.Element("note")
    p = ET.SubElement(n, "pitch")
    ET.SubElement(p, "step").text = step
    if alter != 0:
        ET.SubElement(p, "alter").text = str(alter)
    ET.SubElement(p, "octave").text = str(octave)
    ET.SubElement(n, "duration").text = str(duration)
    ET.SubElement(n, "voice").text = "1"
    ET.SubElement(n, "type").text = ntype
    ET.SubElement(n, "stem").text = "up"
    if alter == 1:
        ET.SubElement(n, "accidental").text = "sharp"
    elif alter == -1:
        ET.SubElement(n, "accidental").text = "flat"
    if dot:
        ET.SubElement(n, "dot")
    return n


def chord_elem(root: str, kind: str) -> ET.Element:
    h = ET.Element("harmony")
    ET.SubElement(h, "root").append(ET.fromstring(f'<root-step>{root}</root-step>'))
    k = ET.SubElement(h, "kind")
    k.text = kind
    k.set("text", kind)
    return h


def main(version: int = 2):
    root = ET.Element("score-partwise", version="3.1", xmlns=NS)
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = "Fractured Motion – Orbit Version"
    ET.SubElement(work, "creator", type="composer").text = "Mike Bryant"
    ident = ET.SubElement(root, "identification")
    enc = ET.SubElement(ident, "encoding")
    ET.SubElement(enc, "encoding-date").text = "2026-02-23"
    ET.SubElement(enc, "software").text = f"Fractured Motion Orbit V{version} / GCE-Jazz V1.0"
    defaults = ET.SubElement(root, "defaults")
    scaling = ET.SubElement(defaults, "scaling")
    ET.SubElement(scaling, "millimeters").text = "7.0"
    ET.SubElement(scaling, "tenths").text = "40"
    plist = ET.SubElement(root, "part-list")
    sp = ET.SubElement(plist, "score-part", id="P1")
    ET.SubElement(sp, "part-name").text = "Melody (Concert)"
    part = ET.SubElement(root, "part", id="P1")

    for m in range(64):
        measure = ET.SubElement(part, "measure", number=str(m + 1))
        if m == 0:
            attrs = ET.SubElement(measure, "attributes")
            ET.SubElement(attrs, "divisions").text = "4"
            key = ET.SubElement(attrs, "key")
            ET.SubElement(key, "fifths").text = "-3"
            ET.SubElement(key, "mode").text = "minor"
            time = ET.SubElement(attrs, "time")
            ET.SubElement(time, "beats").text = "4"
            ET.SubElement(time, "beat-type").text = "4"
            clef = ET.SubElement(attrs, "clef")
            ET.SubElement(clef, "sign").text = "G"
            ET.SubElement(clef, "line").text = "2"
            direction = ET.SubElement(measure, "direction", placement="above")
            dt = ET.SubElement(direction, "direction-type")
            metro = ET.SubElement(dt, "metronome")
            ET.SubElement(metro, "beat-unit").text = "quarter"
            ET.SubElement(metro, "per-minute").text = "72"
            ET.SubElement(measure, "sound", tempo="72")
        direction = ET.SubElement(measure, "direction", placement="above")
        dt = ET.SubElement(direction, "direction-type")
        ET.SubElement(dt, "words").text = CHORDS[m]
        for note_tup in (MELODY[m] if isinstance(MELODY[m][0], (list, tuple)) else (MELODY[m],)):
            if note_tup[0] == "R":
                _, _, _, dur, ntype = note_tup
                measure.append(rest_elem(dur, ntype))
            else:
                step, alter, octave, dur, ntype = note_tup[:5]
                dot = note_tup[5] if len(note_tup) > 5 else False
                measure.append(note_elem(step, alter, octave, dur, ntype, dot))

    tree = ET.ElementTree(root)
    out = Path(__file__).parent / "MusicXML" / f"fractured_motion_orbit_v{version}.musicxml"
    tree.write(str(out), encoding="unicode", method="xml", xml_declaration=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    import sys
    v = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    main(v)
