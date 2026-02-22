"""Export melody-only assets from HarmolodicSketch V4 (measures 1-57, P1 flugelhorn)."""
import copy
import os
from music21 import converter, stream, tempo

BASE = os.path.dirname(os.path.abspath(__file__))
SCORE_DIR = os.path.join(BASE, "score")
MELODY_DIR = os.path.join(BASE, "melody")


def main():
    os.makedirs(MELODY_DIR, exist_ok=True)
    v4_path = os.path.join(SCORE_DIR, "HarmolodicSketch_Gravitational_ECM_V4.musicxml")
    score = converter.parse(v4_path)
    flugel_full = score.parts[0]
    flugel = flugel_full.measures(1, 57)

    # Concert melody: transpose +2 to concert pitch, no chord symbols, P1 only
    concert_stream = stream.Score()
    concert_part = flugel.transpose(2)
    concert_part.partName = "Flugelhorn (concert)"
    concert_stream.insert(0, concert_part)
    concert_stream.metadata = score.metadata
    concert_path = os.path.join(MELODY_DIR, "HarmolodicSketch_melody_concert_V1.musicxml")
    concert_stream.write("musicxml", fp=concert_path)
    print(f"Wrote: {concert_path}")

    # Bb melody: written pitch (keep transpose -2 for flugelhorn)
    bb_stream = stream.Score()
    bb_part = copy.deepcopy(flugel)
    bb_part.partName = "Flugelhorn in Bb"
    bb_stream.insert(0, bb_part)
    bb_stream.metadata = score.metadata
    bb_path = os.path.join(MELODY_DIR, "HarmolodicSketch_melody_Bb_V1.musicxml")
    bb_stream.write("musicxml", fp=bb_path)
    print(f"Wrote: {bb_path}")

    # MIDI: Bb part as written, tempo 48, divisions 4 per quarter
    midi_stream = stream.Score()
    midi_part = copy.deepcopy(flugel)
    midi_stream.insert(0, tempo.MetronomeMark(number=48))
    midi_stream.insert(0, midi_part)
    midi_path = os.path.join(MELODY_DIR, "HarmolodicSketch_melody_V1.mid")
    midi_stream.write("midi", fp=midi_path)
    print(f"Wrote: {midi_path}")


if __name__ == "__main__":
    main()
