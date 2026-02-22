"""Create HarmolodicSketch_melody_V2.mid - Bb written pitch (flugelhorn), tempo 48, 4 divisions per quarter.
V2 edits: bar 34 E->F (signature contour), bar 44 remove E (G-C-D-rest)."""
import os

# Bb written pitch events from V2:
# M5: G4 half(8), C4 quarter(4), rest(4)
# M7: B3 half(8), rest(8)
# M9: G4 half(8), C4 quarter(4), B3 quarter(4)
# M10: E4 half(8), D4 half(8)
# M32: D4 whole(16)
# M34: F4 whole(16)  <- signature contour (E->F)
# M36: B3 whole(16)
# M44: G4 quarter(4), C4 quarter(4), D4 quarter(4), rest(4)
# M57: E4 quarter(4)

EVENTS = [
    (16, None), (16, None), (16, None), (16, None),  # M1-4
    (8, 67), (4, 60), (4, None),  # M5: G4, C4, rest
    (16, None),  # M6
    (8, 59), (8, None),  # M7: B3, rest
    (16, None),  # M8
    (8, 67), (4, 60), (4, 59),  # M9
    (8, 64), (8, 62),  # M10: E4, D4
    (16, None), (16, None), (16, None), (16, None), (16, None), (16, None),  # M11-16
    (16, None), (16, None), (16, None), (16, None), (16, None), (16, None),  # M17-22
    (16, None), (16, None), (16, None), (16, None), (16, None), (16, None),  # M23-28
    (16, None), (16, None), (16, None),  # M29-31
    (16, 62),  # M32: D4
    (16, None),  # M33
    (16, 65),  # M34: F4 (signature contour)
    (16, None),  # M35
    (16, 59),  # M36: B3
    (16, None), (16, None), (16, None), (16, None), (16, None), (16, None),  # M37-42
    (16, None),  # M43
    (4, 67), (4, 60), (4, 62), (4, None),  # M44: G4, C4, D4, rest
    (16, None), (16, None), (16, None), (16, None), (16, None), (16, None),  # M45-50
    (16, None), (16, None), (16, None), (16, None), (16, None), (16, None),  # M51-56
    (4, 64),  # M57: E4
]

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(BASE, "melody", "HarmolodicSketch_melody_V2.mid")


def main():
    try:
        from midiutil import MIDIFile
    except ImportError:
        try:
            from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
            mid = MidiFile(ticks_per_beat=4)
            track = MidiTrack()
            mid.tracks.append(track)
            track.append(MetaMessage("set_tempo", tempo=bpm2tempo(48)))
            track.append(MetaMessage("time_signature", numerator=4, denominator=4))
            tick = 0
            for dur, note in EVENTS:
                if note is not None:
                    track.append(Message("note_on", note=note, velocity=64, time=tick))
                    tick = 0
                    track.append(Message("note_off", note=note, velocity=0, time=dur))
                else:
                    tick += dur
            mid.save(OUT_PATH)
            print(f"Wrote: {OUT_PATH} (mido)")
            return
        except ImportError:
            _write_midi_raw()
            return

    mf = MIDIFile(1, ticks_per_quarternote=4)
    mf.addTempo(0, 0, 48)
    mf.addTimeSignature(0, 0, 4, 4, 24)
    beat = 0.0
    for dur, note in EVENTS:
        if note is not None:
            mf.addNote(0, 0, note, beat, dur / 4.0, 64)
        beat += dur / 4.0
    with open(OUT_PATH, "wb") as f:
        mf.writeFile(f)
    print(f"Wrote: {OUT_PATH} (midiutil)")


def _write_midi_raw():
    """Write MIDI file using struct (no deps)."""
    import struct

    def varint(val):
        val &= 0xFFFFFFFF
        out = []
        while val > 0x7F:
            out.append((val & 0x7F) | 0x80)
            val >>= 7
        out.append(val & 0x7F)
        return bytes(out)

    ticks_per_beat = 4
    tempo = 500000  # 48 BPM
    track_data = bytearray()
    track_data.extend(bytes([0xFF, 0x51, 3]) + struct.pack(">I", tempo)[1:4])
    track_data.extend(bytes([0xFF, 0x58, 4, 4, 2, 24, 8]))
    abs_tick = 0
    for dur, note in EVENTS:
        if note is not None:
            track_data.extend(varint(abs_tick))
            track_data.extend(bytes([0x90, note, 64]))
            abs_tick = 0
            track_data.extend(varint(dur))
            track_data.extend(bytes([0x80, note, 0]))
        else:
            abs_tick += dur
    track_data.extend(varint(abs_tick))
    track_data.extend(bytes([0xFF, 0x2F, 0]))

    with open(OUT_PATH, "wb") as f:
        f.write(b"MThd")
        f.write(struct.pack(">I", 6))
        f.write(struct.pack(">HHH", 1, 1, ticks_per_beat))
        f.write(b"MTrk")
        f.write(struct.pack(">I", len(track_data)))
        f.write(track_data)
    print(f"Wrote: {OUT_PATH} (raw)")


if __name__ == "__main__":
    main()
