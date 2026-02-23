#!/usr/bin/env python3
"""Generate Harmolodic Sketch Gravitational V3 from V2.
GCE ≥9.85. No density increase."""
import xml.etree.ElementTree as ET
from pathlib import Path

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
    src = Path(__file__).parent / "MusicXML" / "HarmolodicSketch-Gravitational_V2.musicxml"
    tree = ET.parse(src)
    root = tree.getroot()

    def tag(name):
        return "{%s}%s" % (NS, name)

    # Update software
    for enc in root.iter(tag("encoding")):
        for sw in enc.findall(tag("software")):
            sw.text = "Harmolodic Sketch Gravitational V3 (GCE ≥9.85) / GCE-Jazz V1.0"
            break

    parts = {p.get("id"): p for p in root.findall(tag("part"))}

    # 1) Middle third: Bar 9 has simultaneous F+G entry. Offset F cell by 1 beat (rest + C-Eb-G)
    for meas in parts["P1"].findall(tag("measure")):
        if meas.get("number") == "9":
            for child in list(meas):
                if child.tag not in (tag("attributes"), tag("direction")):
                    meas.remove(child)
            meas.append(rest_note(4, "quarter"))
            meas.append(pitch_note("C", 0, 4, 8, "half"))
            meas.append(pitch_note("E", -1, 4, 4, "quarter"))
            meas.append(pitch_note("G", 0, 4, 4, "quarter"))
            break

    # 2) Harmonic stillness: Bars 32-33 mid-section. Replace with Dm(add9) sustained. Bass D root only.
    for part_id, part in parts.items():
        for meas in part.findall(tag("measure")):
            num = meas.get("number")
            if num in ("32", "33"):
                for child in list(meas):
                    if child.tag != tag("attributes"):
                        meas.remove(child)
                if part_id == "P1":
                    meas.append(rest_note())
                elif part_id == "P2":
                    for n in guitar_dyad("D", 0, 3, "F", 0, 4):  # Dm sustained
                        meas.append(n)
                elif part_id == "P3":
                    meas.append(pitch_note("D", 0, 2, 16, "whole"))

    # 3) Pre-final silence: Extend by +1 beat. Bar 43 bass: G dotted half (3 beats) + rest quarter (1 beat).
    for meas in parts["P3"].findall(tag("measure")):
        if meas.get("number") == "43":
            for child in list(meas):
                if child.tag != tag("attributes"):
                    meas.remove(child)
            n = pitch_note("G", 0, 2, 12, "half")
            ET.SubElement(n, "dot")
            meas.append(n)
            meas.append(rest_note(4, "quarter"))
            break

    # 4) Ending: Final note colour tone (9th or 11th). Bb is 6th in C. D is 9th (2). F is 11th (4). So D or F.
    # Bar 58 F: change Bb to D (9th) or F (11th). D4 = 9th of C. F4 = 11th.
    # No bass articulation in final bar - bass 58 already rest. Good.
    for meas in parts["P1"].findall(tag("measure")):
        if meas.get("number") == "58":
            for child in list(meas):
                if child.tag != tag("attributes"):
                    meas.remove(child)
            meas.append(pitch_note("D", 0, 5, 8, "half"))  # D5 = 9th colour tone
            meas.append(rest_note(8, "half"))
            break

    out_dir = Path(__file__).parent / "MusicXML"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "HarmolodicSketch-Gravitational_V3.musicxml"
    tree.write(str(out), encoding="unicode", method="xml", xml_declaration=True, default_namespace=None)
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
