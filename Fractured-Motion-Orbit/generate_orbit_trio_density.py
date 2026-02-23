#!/usr/bin/env python3
"""Generate Fractured Motion Orbit Trio with density waves (Flugelhorn, Guitar, Upright Bass)."""
import xml.etree.ElementTree as ET
from pathlib import Path

from generate_orbit_melody import CHORDS, MELODY, note_elem, rest_elem

NS = "http://www.musicxml.org/ns/3.1"

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

BASS_ROOTS = [
    "B", "C", "B", "A", "B", "C", "B", "F#", "B", "C", "B", "A", "B", "C", "B", "F#",
    "D", "D", "D", "Bb", "D", "C", "D", "F", "F", "F", "A", "F", "F", "C", "F", "F",
    "C", "C", "C", "G", "C", "C", "C", "E", "C", "C", "C", "C", "E", "Eb",
    "B", "C", "B", "A", "B", "F#", "B", "C", "B", "A", "B", "C", "B", "F#", "B", "C", "B", "A",
]

# Density: guitar 0=rest, 1=dyad, 2=3-note, 3=4-note, 4=counter-line
# bass 0=rest, 1=pedal whole
# No section constant - vary within
GUITAR_DENSITY = [
    0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 2, 0, 1, 0, 2, 0,
    2, 1, 2, 2, 1, 2, 2, 2,
    3, 3, 3, 2, 3, 3, 3, 3,
    3, 4, 3, 3, 4, 3, 3, 3,
    0, 0,
    2, 1, 2, 2, 1, 2, 2, 2, 2, 2,
    2, 1, 1, 0, 1, 0, 1, 0,
]
BASS_DENSITY = [
    1, 1, 1, 0, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 0, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 0, 1, 0, 1,
]

# Counter-line for guitar bars 33-40: (step, alter, octave, duration)
GTR_COUNTER_33 = [("E", 0, 4, 4), ("G", 0, 4, 4), ("B", 0, 4, 8)]
GTR_COUNTER_36 = [("G", 0, 4, 8), ("F", 1, 4, 8)]


def bass_pitch(root: str):
    m = {"B": ("B", 0), "C": ("C", 0), "D": ("D", 0), "E": ("E", 0), "Eb": ("E", -1),
         "F": ("F", 0), "F#": ("F", 1), "G": ("G", 0), "A": ("A", 0), "Bb": ("B", -1)}
    return m.get(root, ("B", 0))


def main(version: int = 1):
    root = ET.Element("score-partwise", version="3.1", xmlns=NS)
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = "Fractured Motion – Orbit Version (Trio, Density)"
    ET.SubElement(work, "creator", type="composer").text = "Mike Bryant"
    ident = ET.SubElement(root, "identification")
    enc = ET.SubElement(ident, "encoding")
    ET.SubElement(enc, "encoding-date").text = "2026-02-23"
    ET.SubElement(enc, "software").text = f"Fractured Motion Orbit Trio Density V{version} / GCE-Jazz V1.0"
    defaults = ET.SubElement(root, "defaults")
    scaling = ET.SubElement(defaults, "scaling")
    ET.SubElement(scaling, "millimeters").text = "7.0"
    ET.SubElement(scaling, "tenths").text = "40"
    plist = ET.SubElement(root, "part-list")
    for pid, pname in [("P1", "Flugelhorn in Bb"), ("P2", "Guitar"), ("P3", "Upright Bass")]:
        sp = ET.SubElement(plist, "score-part", id=pid)
        ET.SubElement(sp, "part-name").text = pname

    parts = {pid: ET.SubElement(root, "part", id=pid) for pid in ["P1", "P2", "P3"]}

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

    def dyn_elem(level="pp"):
        d = ET.Element("dynamics")
        ET.SubElement(d, level)
        return d

    for m in range(64):
        chord = CHORDS[m]
        base = chord.split("/")[0]
        voicing = GUITAR_VOICINGS.get(base, GUITAR_VOICINGS["Bm(add9)"])

        # Flugelhorn
        meas = add_measure(parts["P1"], m, attrs_first=(m == 0), chord=chord)
        if m == 63:
            wedge = ET.SubElement(meas, "direction", placement="below")
            ET.SubElement(ET.SubElement(wedge, "direction-type"), "wedge", type="diminuendo")
        for note_tup in (MELODY[m] if isinstance(MELODY[m][0], (list, tuple)) else (MELODY[m],)):
            if note_tup[0] == "R":
                _, _, _, dur, ntype = note_tup
                meas.append(rest_elem(dur, ntype))
            else:
                step, alter, octave, dur, ntype = note_tup[:5]
                dot = note_tup[5] if len(note_tup) > 5 else False
                n = note_elem(step, alter, octave, dur, ntype, dot)
                n.append(dyn_elem("ppp" if m >= 61 else "pp"))
                meas.append(n)

        # Guitar
        meas = add_measure(parts["P2"], m, attrs_first=(m == 0), chord=None)
        gd = GUITAR_DENSITY[m] if m < len(GUITAR_DENSITY) else 2
        if gd == 0:
            meas.append(rest_elem(16, "whole"))
        elif gd == 4 and m == 32:
            for s, a, o, dur in GTR_COUNTER_33:
                n = note_elem(s, a, o, dur, "quarter" if dur == 4 else "half")
                n.append(dyn_elem("pp"))
                meas.append(n)
        elif gd == 4 and m == 35:
            for s, a, o, dur in GTR_COUNTER_36:
                n = note_elem(s, a, o, dur, "half")
                n.append(dyn_elem("pp"))
                meas.append(n)
        else:
            n_notes = max(1, min(gd, 4))
            for i, (s, a, o) in enumerate(voicing[:n_notes]):
                n = note_elem(s, a, o, 16, "whole")
                if i > 0:
                    n.insert(0, ET.Element("chord"))
                n.append(dyn_elem("pp"))
                meas.append(n)

        # Bass
        meas = add_measure(parts["P3"], m, attrs_first=(m == 0), chord=None)
        bd = BASS_DENSITY[m] if m < len(BASS_DENSITY) else 1
        if bd == 0:
            meas.append(rest_elem(16, "whole"))
        else:
            br = BASS_ROOTS[m] if m < len(BASS_ROOTS) else "B"
            s, a = bass_pitch(br)
            bn = note_elem(s, a, 2, 16, "whole")
            bn.append(dyn_elem("pp"))
            meas.append(bn)

    tree = ET.ElementTree(root)
    out = Path(__file__).parent / "MusicXML" / f"fractured_motion_orbit_trio_density_v{version}.musicxml"
    tree.write(str(out), encoding="unicode", method="xml", xml_declaration=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    import sys
    v = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    main(v)
