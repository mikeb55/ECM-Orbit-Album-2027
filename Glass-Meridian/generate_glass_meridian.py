#!/usr/bin/env python3
"""Generate Glass Meridian – ECM-Orbit trio (Guitar, Upright Bass, Flugelhorn). 72 bars."""
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "http://www.musicxml.org/ns/3.1"

# Form: A(16) B(16) C(12) Interlude(4) A'(24)
# Harmony: E Dorian -> G major (chromatic mediant) -> Db Lydian -> pivot -> E Dorian
# No ii-V-I, no functional dominants

CHORDS = (
    # A 1-16: E Dorian
    ["Em7", "Em(add9)", "Em7/D", "Am7", "Em7", "Em(add9)", "Em7/D", "Bm7",
     "Em7", "Em(add9)", "Am7", "Em7", "Em(add9)", "Em7/D", "Am7", "Em7"]
    # B 17-32: G major
    + ["G", "Gmaj7", "G(add4)", "G/B", "G", "Gmaj7", "G(add4)", "D/F#",
      "G", "Gmaj7", "G(add4)", "Em7", "G", "Gmaj7", "G(add4)", "G"]
    # C 33-44: Db Lydian
    + ["Dbmaj7(#11)", "Db(add4)", "Dbmaj7(#11)", "Db(add4)", "Dbmaj7(#11)", "Db(add4)",
      "Dbmaj7(#11)", "Db(add4)", "Dbmaj7(#11)", "Db(add4)", "Dbmaj7(#11)", "Db(add4)"]
    # Interlude 45-48: pivot
    + ["E/G#", "Em7", "Em7", "Em7"]
    # A' 49-72: E Dorian return
    + ["Em7", "Em(add9)", "Em7/D", "Am7", "Em7", "Em(add9)", "Em7/D", "Bm7",
      "Em7", "Em(add9)", "Am7", "Em7", "Em(add9)", "Em7/D", "Am7", "Em7",
      "Em7", "Em(add9)", "Am7", "Em7", "Em(add9)", "Em7/D", "Em7", "Em7"]
)

# Flugelhorn: lyrical, rhythmically active, motif repeated in altered rhythm
# Core motif: E-G-B-A (Dorian colour)
# durations: 2=eighth, 4=quarter, 8=half, 16=whole
MELODY = [
    # A 1-16: E Dorian, motif statement
    (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 1
    (("E", 0, 4, 2, "eighth"), ("E", 0, 4, 2, "eighth"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 4, "quarter"), ("A", 0, 4, 4, "quarter")),  # 2 altered
    (("G", 0, 4, 8, "half"), ("A", 0, 4, 8, "half")),  # 3
    (("B", 0, 4, 4, "quarter"), ("A", 0, 4, 4, "quarter"), ("G", 0, 4, 8, "half")),  # 4
    (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 5 motif
    (("E", 0, 4, 2, "eighth"), ("G", 0, 4, 2, "eighth"), ("B", 0, 4, 4, "quarter"), ("A", 0, 4, 8, "half")),  # 6
    (("F", 1, 4, 4, "quarter"), ("E", 0, 4, 4, "quarter"), ("D", 0, 4, 8, "half")),  # 7
    (("E", 0, 4, 8, "half"), ("F", 1, 4, 8, "half")),  # 8
    (("B", 0, 4, 4, "quarter"), ("C", 1, 5, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 9
    (("A", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("E", 0, 4, 8, "half")),  # 10
    (("E", 0, 4, 2, "eighth"), ("E", 0, 4, 2, "eighth"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 11 motif
    (("G", 0, 4, 8, "half"), ("A", 0, 4, 8, "half")),  # 12
    (("E", 0, 4, 16, "whole")),  # 13
    (("B", 0, 4, 4, "quarter"), ("A", 0, 4, 4, "quarter"), ("G", 0, 4, 8, "half")),  # 14
    (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 15
    (("A", 0, 4, 8, "half"), ("G", 0, 4, 8, "half")),  # 16
    # B 17-32: G major, expanded
    (("G", 0, 5, 4, "quarter"), ("B", 0, 5, 4, "quarter"), ("D", 0, 5, 8, "half")),  # 17
    (("E", 0, 5, 4, "quarter"), ("D", 0, 5, 4, "quarter"), ("B", 0, 5, 8, "half")),  # 18
    (("G", 0, 5, 2, "eighth"), ("A", 0, 5, 2, "eighth"), ("B", 0, 5, 4, "quarter"), ("D", 0, 5, 8, "half")),  # 19
    (("D", 0, 5, 8, "half"), ("E", 0, 5, 8, "half")),  # 20
    (("G", 0, 5, 4, "quarter"), ("B", 0, 5, 4, "quarter"), ("D", 0, 5, 4, "quarter"), ("E", 0, 5, 4, "quarter")),  # 21
    (("B", 0, 5, 8, "half"), ("A", 0, 5, 8, "half")),  # 22
    (("G", 0, 5, 4, "quarter"), ("F", 1, 5, 4, "quarter"), ("E", 0, 5, 8, "half")),  # 23
    (("D", 0, 5, 16, "whole")),  # 24
    (("G", 0, 5, 4, "quarter"), ("B", 0, 5, 4, "quarter"), ("D", 0, 5, 8, "half")),  # 25
    (("E", 0, 5, 8, "half"), ("D", 0, 5, 8, "half")),  # 26
    (("B", 0, 5, 2, "eighth"), ("B", 0, 5, 2, "eighth"), ("D", 0, 5, 4, "quarter"), ("E", 0, 5, 8, "half")),  # 27
    (("G", 0, 5, 16, "whole")),  # 28
    (("D", 0, 5, 4, "quarter"), ("E", 0, 5, 4, "quarter"), ("G", 0, 5, 8, "half")),  # 29
    (("B", 0, 5, 8, "half"), ("A", 0, 5, 8, "half")),  # 30
    (("G", 0, 5, 4, "quarter"), ("B", 0, 5, 4, "quarter"), ("D", 0, 5, 8, "half")),  # 31
    (("E", 0, 5, 16, "whole")),  # 32
    # C 33-44: Db Lydian — one sustained fragile tone (bar 36)
    (("F", 0, 5, 4, "quarter"), ("G", 0, 5, 4, "quarter"), ("A", -1, 5, 8, "half")),  # 33 Db Lyd
    (("G", 0, 5, 8, "half"), ("F", 0, 5, 8, "half")),  # 34
    (("G", 0, 5, 16, "whole")),  # 35 sustained fragile (ppp)
    (("D", -1, 5, 8, "half"), ("F", 0, 5, 8, "half")),  # 36
    (("F", 0, 5, 4, "quarter"), ("G", 0, 5, 4, "quarter"), ("A", -1, 5, 8, "half")),  # 37
    (("G", 0, 5, 16, "whole")),  # 38
    (("A", -1, 5, 4, "quarter"), ("G", 0, 5, 4, "quarter"), ("F", 0, 5, 8, "half")),  # 39
    (("F", 0, 5, 8, "half"), ("D", -1, 5, 8, "half")),  # 40
    (("G", 0, 5, 4, "quarter"), ("A", -1, 5, 4, "quarter"), ("G", 0, 5, 8, "half")),  # 41
    (("F", 0, 5, 16, "whole")),  # 42
    (("D", -1, 5, 8, "half"), ("F", 0, 5, 8, "half")),  # 43
    (("G", 0, 5, 16, "whole")),  # 44
    # Interlude 45-48
    (("E", 0, 4, 8, "half"), ("G", 1, 4, 8, "half")),  # 45 pivot
    (("E", 0, 4, 8, "half"), ("B", 0, 4, 8, "half")),  # 46
    (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("A", 0, 4, 8, "half")),  # 47
    (("B", 0, 4, 16, "whole")),  # 48
    # A' 49-72: return, extended
    (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 49
    (("E", 0, 4, 2, "eighth"), ("E", 0, 4, 2, "eighth"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 50
    (("G", 0, 4, 8, "half"), ("A", 0, 4, 8, "half")),  # 51
    (("B", 0, 4, 4, "quarter"), ("A", 0, 4, 4, "quarter"), ("G", 0, 4, 8, "half")),  # 52
    (("E", 0, 4, 16, "whole")),  # 53
    (("B", 0, 4, 4, "quarter"), ("A", 0, 4, 4, "quarter"), ("G", 0, 4, 8, "half")),  # 54
    (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 55
    (("A", 0, 4, 8, "half"), ("G", 0, 4, 8, "half")),  # 56
    (("E", 0, 4, 2, "eighth"), ("G", 0, 4, 2, "eighth"), ("B", 0, 4, 4, "quarter"), ("A", 0, 4, 8, "half")),  # 57
    (("F", 1, 4, 4, "quarter"), ("E", 0, 4, 4, "quarter"), ("D", 0, 4, 8, "half")),  # 58
    (("E", 0, 4, 8, "half"), ("F", 1, 4, 8, "half")),  # 59
    (("B", 0, 4, 4, "quarter"), ("C", 1, 5, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 60
    (("G", 0, 4, 8, "half"), ("A", 0, 4, 8, "half")),  # 61
    (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 62
    (("A", 0, 4, 8, "half"), ("G", 0, 4, 8, "half")),  # 63
    (("E", 0, 4, 16, "whole")),  # 64
    (("B", 0, 4, 4, "quarter"), ("A", 0, 4, 4, "quarter"), ("G", 0, 4, 8, "half")),  # 65
    (("E", 0, 4, 8, "half"), ("F", 1, 4, 8, "half")),  # 66
    (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 67
    (("A", 0, 4, 8, "half"), ("G", 0, 4, 8, "half")),  # 68
    (("E", 0, 4, 2, "eighth"), ("E", 0, 4, 2, "eighth"), ("G", 0, 4, 4, "quarter"), ("B", 0, 4, 8, "half")),  # 69
    (("G", 0, 4, 16, "whole")),  # 70
    (("E", 0, 4, 8, "half"), ("B", 0, 4, 8, "half")),  # 71
    (("E", 0, 4, 16, "whole")),  # 72
]

# V2 ECM upgrades: melodic leap, asymmetry, harmonic stillness, pulse restraint
CHORDS_V2 = (
    ["Em7", "Em(add9)", "Em7/D", "Am7", "Em(add9)", "Em(add9)", "Em7/D", "Bm7"]  # 5-6: sustained
    + ["Em7", "Em(add9)", "Am7", "Em7", "Em(add9)", "Em7/D", "Am7", "Em7"]
    + list(CHORDS[16:])
)
MELODY_V2 = list(MELODY)
# Bar 4: remove B, add 1 beat silence; stepwise A→G before leap → A quarter, G quarter, rest half
MELODY_V2[3] = (("A", 0, 4, 4, "quarter"), ("G", 0, 4, 4, "quarter"), ("R", 0, 0, 8, "half"))
# Bar 5: defining leap G4→E5 (M6), stepwise before (G from bar 4), 1 beat stillness after, no harmonic reinforcement
# E5 quarter, rest quarter, rest half
MELODY_V2[4] = (("E", 0, 5, 4, "quarter"), ("R", 0, 0, 4, "quarter"), ("R", 0, 0, 8, "half"))

# Guitar: bars 1-8 avoid repeating – vary per bar
GUITAR_BARS_1_8_V2 = [
    [("E", 0, 3), ("B", 0, 4)],  # bar 1: 2 half notes
    [("A", 0, 3), ("E", 0, 4)],  # bar 2
    [("B", 0, 4), ("F", 1, 4)],  # bar 3
    [],  # bar 4 rest (gd=0)
    [("B", 0, 4), ("F", 1, 4)],  # bar 5: no E, avoid reinforcing leap
    [("E", 0, 3), ("A", 0, 4)],  # bar 6
    [("B", 0, 4), ("F", 1, 4)],  # bar 7
    [("E", 0, 3), ("B", 0, 4)],  # bar 8
]
# Bass bars 1-8: whole/half only, no quarter subdivision; bars 5-6 sustain E root
BASS_BARS_1_8_V2 = [
    [("E", 0, 2, 8), ("E", 0, 2, 8)],  # bar 1: 2 half notes
    [("B", 0, 2, 8), ("E", 0, 2, 8)],  # bar 2
    [("E", 0, 2, 8), ("D", 0, 2, 8)],  # bar 3
    None,  # bar 4 rest
    [("E", 0, 2, 16)],  # bar 5: whole note E (harmonic stillness)
    [("E", 0, 2, 16)],  # bar 6: whole note E
    [("E", 0, 2, 8), ("G", 0, 2, 8)],  # bar 7
    [("E", 0, 2, 8), ("B", 0, 2, 8)],  # bar 8
]

# V3 ceiling: inevitability, break mirroring, harmonic stillness, unresolved ending
CHORDS_V3 = list(CHORDS_V2)
CHORDS_V3[11] = "Em(add9)"   # bar 12: add stillness (with 13)
CHORDS_V3[64] = "Em(add9)"   # bar 65: no change during G sustain (with 65)
CHORDS_V3[65] = "Em(add9)"   # bar 66: sustain through extended tone

MELODY_V3 = list(MELODY_V2)
# Bar 65: remove A, extend G +1 beat → B quarter, G dotted half
MELODY_V3[64] = (("B", 0, 4, 4, "quarter"), ("G", 0, 4, 12, "half", True))  # dotted half
# Bar 66: harmony unchanged; bar 67: break mirror (quarter,half,quarter vs quarter,quarter,half)
MELODY_V3[66] = (("E", 0, 4, 4, "quarter"), ("G", 0, 4, 8, "half"), ("B", 0, 4, 4, "quarter"))
# Bar 71: extend E +1 beat → E dotted half, B quarter
MELODY_V3[70] = (("E", 0, 4, 12, "half", True), ("B", 0, 4, 4, "quarter"))  # dotted half
# Bar 72: unresolved B, 1 beat silence
MELODY_V3[71] = (("B", 0, 4, 8, "half"), ("R", 0, 0, 8, "half"))

# V3 bass: bars 65-66 root only; bar 72 rest
BASS_FINAL_THIRD_V3 = {64: [("E", 0, 2, 16)], 65: [("E", 0, 2, 16)], 71: None}  # 71 = bar 72 rest

# V3 guitar: bar 12 no inner-voice (sustained); bar 72 rest
GUITAR_STILLNESS_V3 = 11   # bar 12 index
GUITAR_ENDING_REST_V3 = 71  # bar 72

# Guitar: open 4ths/5ths ostinato in A, counter-line in C
# Ostinato pattern (2 bars): E-B | A-E | B-F# | E-A  (4ths/5ths)
GUITAR_OSTINATO_A = [  # bars 1-16, 49-72
    ("E", 0, 3), ("B", 0, 4), ("A", 0, 3), ("E", 0, 4),  # bar 1
    ("B", 0, 4), ("F", 1, 4), ("E", 0, 3), ("A", 0, 4),  # bar 2
]
GUITAR_B = [  # G major voicings, open
    ("G", 0, 3), ("D", 0, 4), ("B", 0, 4), ("G", 0, 4),
    ("D", 0, 4), ("A", 0, 4), ("G", 0, 3), ("B", 0, 4),
]
GUITAR_C_COUNTER = [  # C section counter-line (33-44): Db Lydian colour
    ("D", -1, 4), ("G", 0, 4), ("A", -1, 4), ("G", 0, 4),
    ("F", 0, 4), ("G", 0, 4), ("A", -1, 4), ("F", 0, 4),
]

# Bass: 2-bar motif in A, expands in B, suspended pedal in Db
BASS_MOTIF_A = [("E", 0, 2, 4), ("B", 0, 2, 4), ("E", 0, 2, 4), ("D", 0, 2, 4)]  # bar 1
BASS_MOTIF_A2 = [("E", 0, 2, 4), ("G", 0, 2, 4), ("E", 0, 2, 4), ("B", 0, 2, 4)]  # bar 2
BASS_B = [  # G major, expanded range
    ("G", 0, 2, 4), ("D", 0, 3, 4), ("G", 0, 2, 4), ("B", 0, 2, 4),
    ("G", 0, 2, 4), ("D", 0, 3, 4), ("E", 0, 2, 4), ("B", 0, 2, 4),
]
BASS_DB_PEDAL = ("D", -1, 2, 16)  # Db pedal, whole note

# Density map: 0=rest, 1=sparse (2 notes), 2=full ostinato/motif, 3=counter/pedal
# 1-8 low | 9-16 ostinato | 17-32 motion | 33-44 expansion | 45-48 thin | 49-60 rebuild | 61-72 reduction
GUITAR_DENSITY = (
    [1, 1, 1, 0, 1, 1, 1, 1]  # 1-8 low
    + [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]  # 9-16 ostinato
    + [2] * 16  # 17-32 motion
    + [3] * 12  # 33-44 counter-line
    + [1, 1, 1, 0]  # 45-48 thin
    + [2] * 12  # 49-60 rebuild
    + [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # 61-72 reduction
)
BASS_DENSITY = (
    [1, 1, 1, 0, 1, 1, 1, 1]  # 1-8 low
    + [2] * 8 + [2] * 8  # 9-32
    + [3] * 12  # 33-44 pedal
    + [1, 1, 1, 0]  # 45-48 thin, bar 48 silence before return
    + [2] * 12  # 49-60 rebuild
    + [2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1]  # 61-72 reduction
)


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


def main(version: int = 1):
    root = ET.Element("score-partwise", version="3.1", xmlns=NS)
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = "Glass Meridian"
    ET.SubElement(work, "creator", type="composer").text = "Mike Bryant"
    ident = ET.SubElement(root, "identification")
    enc = ET.SubElement(ident, "encoding")
    ET.SubElement(enc, "encoding-date").text = "2026-02-23"
    sw = f"Glass Meridian ECM V{version} (GCE ≥9.85)" if version == 3 else (
        f"Glass Meridian ECM V{version} (GCE ≥9.7)" if version == 2 else f"Glass Meridian V{version} / GCE-Jazz V1.0")
    ET.SubElement(enc, "software").text = sw
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
            ET.SubElement(k, "fifths").text = "1"  # E minor / G major
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
                ET.SubElement(metro, "per-minute").text = "84"
                ET.SubElement(measure, "sound", tempo="84")
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

    def dyn_elem(level="mp"):
        d = ET.Element("dynamics")
        ET.SubElement(d, level)
        return d

    chords = CHORDS_V3 if version == 3 else (CHORDS_V2 if version == 2 else CHORDS)
    melody = MELODY_V3 if version == 3 else (MELODY_V2 if version == 2 else MELODY)

    for m in range(72):
        chord = chords[m]
        meas_f = add_measure(parts["P1"], m, attrs_first=(m == 0), chord=chord)

        # Flugelhorn
        flug_dyn = "ppp" if m == 34 else ("pp" if m >= 60 else "mp")
        for note_tup in (melody[m] if isinstance(melody[m][0], (list, tuple)) else (melody[m],)):
            if note_tup[0] == "R":
                _, _, _, dur, ntype = note_tup
                meas_f.append(rest_elem(dur, ntype))
            else:
                step, alter, octave, dur, ntype = note_tup[:5]
                dot = note_tup[5] if len(note_tup) > 5 else False
                n = note_elem(step, alter, octave, dur, ntype, dot)
                n.append(dyn_elem(flug_dyn))
                meas_f.append(n)

        # Guitar (density map)
        meas_g = add_measure(parts["P2"], m, attrs_first=(m == 0), chord=None)
        gd = GUITAR_DENSITY[m] if m < len(GUITAR_DENSITY) else 2
        gtr_dyn = "pp" if m >= 60 else "mp"
        if version in (2, 3) and m < 8:  # V2/V3: bars 1-8 avoid repeating comp pattern
            pat = GUITAR_BARS_1_8_V2[m]
            if not pat:
                meas_g.append(rest_elem(16, "whole"))
            else:
                for s, a, o in pat:
                    n = note_elem(s, a, o, 8, "half")
                    n.append(dyn_elem(gtr_dyn))
                    meas_g.append(n)
        elif version == 3 and m == GUITAR_ENDING_REST_V3:
            meas_g.append(rest_elem(16, "whole"))
        elif version == 3 and m == GUITAR_STILLNESS_V3:
            for s, a, o in [("B", 0, 4), ("E", 0, 3)]:
                n = note_elem(s, a, o, 8, "half")
                n.append(dyn_elem(gtr_dyn))
                meas_g.append(n)
        elif gd == 0:
            meas_g.append(rest_elem(16, "whole"))
        elif gd == 1:  # sparse: 2 notes
            if 16 <= m <= 31:
                pat = GUITAR_B
            elif 32 <= m <= 43:
                pat = GUITAR_C_COUNTER
            else:
                pat = GUITAR_OSTINATO_A
            idx = m % 2
            for i in [0, 2]:
                s, a, o = pat[(idx * 4 + i) % len(pat)]
                n = note_elem(s, a, o, 8, "half")
                n.append(dyn_elem(gtr_dyn))
                meas_g.append(n)
        elif gd == 3:  # C section counter-line
            idx = (m - 32) % 2
            for i in range(4):
                s, a, o = GUITAR_C_COUNTER[(idx * 4 + i) % 8]
                n = note_elem(s, a, o, 4, "quarter")
                n.append(dyn_elem(gtr_dyn))
                meas_g.append(n)
        else:  # gd == 2: full ostinato
            if 16 <= m <= 31:
                pat = GUITAR_B
            else:
                pat = GUITAR_OSTINATO_A
            idx = m % 2
            for i in range(4):
                s, a, o = pat[(idx * 4 + i) % len(pat)]
                n = note_elem(s, a, o, 4, "quarter")
                n.append(dyn_elem(gtr_dyn))
                meas_g.append(n)

        # Bass (density map)
        meas_b = add_measure(parts["P3"], m, attrs_first=(m == 0), chord=None)
        bd = BASS_DENSITY[m] if m < len(BASS_DENSITY) else 2
        bass_dyn = "pp" if m >= 60 else "mp"
        if version in (2, 3) and m < 8:  # V2/V3: no subdivision, bars 5-6 sustain root
            bv = BASS_BARS_1_8_V2[m]
            if bv is None:
                meas_b.append(rest_elem(16, "whole"))
            else:
                for s, a, o, dur in bv:
                    n = note_elem(s, a, o, dur, "whole" if dur == 16 else "half")
                    n.append(dyn_elem(bass_dyn))
                    meas_b.append(n)
        elif version == 3 and m in BASS_FINAL_THIRD_V3:
            bv = BASS_FINAL_THIRD_V3[m]
            if bv is None:
                meas_b.append(rest_elem(16, "whole"))
            else:
                for s, a, o, dur in bv:
                    n = note_elem(s, a, o, dur, "whole")
                    n.append(dyn_elem(bass_dyn))
                    meas_b.append(n)
        elif bd == 0:
            meas_b.append(rest_elem(16, "whole"))
        elif bd == 3:  # Db pedal
            s, a, o, dur = BASS_DB_PEDAL
            n = note_elem(s, a, o, dur, "whole")
            n.append(dyn_elem(bass_dyn))
            meas_b.append(n)
        elif bd == 1:  # sparse: 2 notes
            motif = BASS_MOTIF_A if m % 2 == 0 else BASS_MOTIF_A2
            for s, a, o, dur in [motif[0], motif[1]]:
                n = note_elem(s, a, o, dur * 2, "half")
                n.append(dyn_elem(bass_dyn))
                meas_b.append(n)
        elif 16 <= m <= 31:  # B expanded
            idx = m % 2
            for s, a, o, dur in (BASS_B[:4] if idx == 0 else BASS_B[4:]):
                n = note_elem(s, a, o, dur, "quarter")
                n.append(dyn_elem(bass_dyn))
                meas_b.append(n)
        else:  # A, Interlude, A': 2-bar motif
            idx = m % 2
            motif = BASS_MOTIF_A if idx == 0 else BASS_MOTIF_A2
            for s, a, o, dur in motif:
                n = note_elem(s, a, o, dur, "quarter")
                n.append(dyn_elem(bass_dyn))
                meas_b.append(n)

    tree = ET.ElementTree(root)
    if version == 3:
        out = Path(r"C:\Users\mike\Documents\Cursor AI Projects\ECM-Orbit-Album-2027\Glass Meridian") / "Glass_Meridian_ECM_V3.musicxml"
    else:
        out_name = f"Glass_Meridian_ECM_V2.musicxml" if version == 2 else f"glass_meridian_v{version}.musicxml"
        out = Path(__file__).parent / "MusicXML" / out_name
    tree.write(str(out), encoding="unicode", method="xml", xml_declaration=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    import sys
    v = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    main(v)
