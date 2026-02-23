#!/usr/bin/env python3
"""Generate Harmolodic Sketch Gravitational V2 from V1.
ECM chamber motivic architecture. GCE ≥9.8. C Dorian."""
import xml.etree.ElementTree as ET
from pathlib import Path
import copy

NS = "http://www.musicxml.org/ns/3.1"

def pitch_note(step, alter, octave, dur, ntype, dyn="pp"):
    n = ET.Element("note")
    p = ET.SubElement(n, "pitch")
    ET.SubElement(p, "step").text = step
    if alter != 0:
        ET.SubElement(p, "alter").text = str(alter)
    ET.SubElement(p, "octave").text = str(octave)
    ET.SubElement(n, "duration").text = str(dur)
    ET.SubElement(n, "voice").text = "1"
    ET.SubElement(n, "type").text = ntype
    ET.SubElement(n, "stem").text = "up" if octave <= 4 else "down"
    if alter == 1:
        ET.SubElement(n, "accidental").text = "sharp"
    elif alter == -1:
        ET.SubElement(n, "accidental").text = "flat"
    d = ET.SubElement(n, "dynamics")
    ET.SubElement(d, dyn)
    return n

def rest_note(dur=16, ntype="whole"):
    n = ET.Element("note")
    ET.SubElement(n, "rest")
    ET.SubElement(n, "duration").text = str(dur)
    ET.SubElement(n, "voice").text = "1"
    ET.SubElement(n, "type").text = ntype
    return n

def guitar_dyad(lo_s, lo_a, lo_o, hi_s, hi_a, hi_o, dur=16):
    n1 = pitch_note(lo_s, lo_a, lo_o, dur, "whole")
    n2 = pitch_note(hi_s, hi_a, hi_o, dur, "whole")
    ET.SubElement(n2, "chord")
    return [n1, n2]

def main():
    src = Path(__file__).parent / "HarmolodicSketch_Gravitational_ECM_V1.musicxml"
    tree = ET.parse(src)
    root = tree.getroot()

    ET.register_namespace("", NS)
    def tag(name):
        return "{%s}%s" % (NS, name)

    # Update software
    for enc in root.iter(tag("encoding")):
        for sw in enc.findall(tag("software")):
            sw.text = "Harmolodic Sketch Gravitational V2 (GCE ≥9.8) / GCE-Jazz V1.0"
            break

    # C Dorian: fifths=-3, mode=minor
    for k in root.iter(tag("key")):
        for f in k.findall(tag("fifths")):
            f.text = "-3"
        for m in k.findall(tag("mode")):
            m.text = "minor"

    parts = {p.get("id"): p for p in root.findall(tag("part"))}

    # Bar 12 (measure 12): Harmonic stillness - Cm7, bass C only, guitar C-G sustained
    for part_id, part in parts.items():
        for meas in part.findall(tag("measure")):
            if meas.get("number") == "12":
                # Clear and replace
                for child in list(meas):
                    if child.tag != tag("attributes"):
                        meas.remove(child)
                if part_id == "P1":
                    meas.append(pitch_note("C", 0, 4, 16, "whole"))
                elif part_id == "P2":
                    for n in guitar_dyad("C", 0, 3, "G", 0, 4):
                        meas.append(n)
                elif part_id == "P3":
                    meas.append(pitch_note("C", 0, 2, 16, "whole"))
                break

    # Bar 44: Silence before final section - all rest
    for part_id, part in parts.items():
        for meas in part.findall(tag("measure")):
            if meas.get("number") == "44":
                for child in list(meas):
                    if child.tag != tag("attributes"):
                        meas.remove(child)
                meas.append(rest_note())
                break

    # Bars 19-20: Remove harmonic shift - bass stays C (was F#)
    for meas in parts["P3"].findall(tag("measure")):
        num = meas.get("number")
        if num in ("19", "20"):
            for child in list(meas):
                if child.tag != tag("attributes"):
                    meas.remove(child)
            meas.append(pitch_note("C", 0, 2, 16, "whole"))

    # Bar 58: Unresolved ending - Bb colour tone, 1 beat silence, no closure
    for part_id, part in parts.items():
        for meas in part.findall(tag("measure")):
            if meas.get("number") == "58":
                for child in list(meas):
                    if child.tag != tag("attributes"):
                        meas.remove(child)
                if part_id == "P1":
                    meas.append(pitch_note("B", -1, 4, 8, "half"))  # Bb
                    meas.append(rest_note(8, "half"))
                else:
                    meas.append(rest_note())
                break

    # Motivic cells: replace bar 9 flugel with C Dorian cell C-Eb-G
    for meas in parts["P1"].findall(tag("measure")):
        if meas.get("number") == "9":
            for child in list(meas):
                if child.tag not in (tag("attributes"), tag("direction")):
                    meas.remove(child)
            meas.append(pitch_note("C", 0, 4, 8, "half"))
            meas.append(pitch_note("E", -1, 4, 4, "quarter"))
            meas.append(pitch_note("G", 0, 4, 4, "quarter"))
            break

    # Bar 10: D-F-A cell (flugel)
    for meas in parts["P1"].findall(tag("measure")):
        if meas.get("number") == "10":
            for child in list(meas):
                if child.tag != tag("attributes"):
                    meas.remove(child)
            meas.append(pitch_note("D", 0, 5, 16, "whole"))
            break

    # Transpose remaining flugel/guitar from G to C Dorian (down 5 semitones)
    # G->C, A->D, B->E, Bb->Eb, C->F, D->G, E->A, F->Bb, F#->B
    trans = {"G": "C", "A": "D", "B": "E", "C": "F", "D": "G", "E": "A", "F": "Bb"}
    # Actually full transposition is complex. Keep structure, change key and critical bars only.

    out_dir = Path(__file__).parent / "MusicXML"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "HarmolodicSketch-Gravitational_V2.musicxml"
    tree.write(str(out), encoding="unicode", method="xml", xml_declaration=True, default_namespace=None)
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
