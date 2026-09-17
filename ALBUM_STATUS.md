# ECM Album 2027 — Canonical File Status

Reviewed and pruned 17 September 2026. **One canonical version per piece.** If you add a version, update this file or the ambiguity comes back.

## Lineup
Flugelhorn in Bb / Guitar / Upright Bass (+ optional alto sax on 3 tracks).
Drummerless, after Kenny Wheeler, *Angel Song* (ECM, 1997).

## Canonical scores — ensemble lineup

| Piece | Canonical file | Key / Tempo | Bars | Status |
|:--|:--|:--|:--|:--|
| The Mirror (Chamber Field) | `Mirror-Chamber/..._V1.musicxml` | Ab, 52 | 60 | Lead track |
| Lyrical Expansion | `Lyrical-Expansion/..._V2.musicxml` | Ab, 54, 3/4 | 56 | Repaired; extend to ~110 bars |
| First Light (Suspended Radiance) | `FirstLight-Chamber/..._V1.musicxml` | G, 50 | 60 | Ready |
| Harmolodic Sketch (Gravitational Axis) | `HarmolodicSketch-Gravitational/..._V1.musicxml` | G, 48 | 58 | Ready |
| Orbit — ECM Chamber | `Orbit-Slowed/..._V3.musicxml` | C, 56, 3/4 | 52 | **Guitar part unwritten (14 notes)** |
| Interlude: Quiet Field | `Interlude-Reset/..._V3.musicxml` | D, 48, 3/4 | 25 | Ready — do not extend |
| North Light | `NorthLight-Pivot/..._V1.musicxml` | E, 46 | 32 | Album opener |

## Canonical scores — guitar + string quartet (arrangeable to lineup)

| Piece | Canonical file | Notes |
|:--|:--|:--|
| Myrtle's Prayer | `.../Myrtles_Prayer/V3_..._GCE10.musicxml` | Best transfer candidate. Vln I → flugelhorn, viola → alto, cello → bass. |
| Unreliable Gravity | `.../Unreliable_Gravity/V1_....musicxml` | Longest piece; album closer. |
| Sylva Narrative | `.../Sylva_Narrative/V3_..._Final.musicxml` | Only forward-moving piece (100bpm). |
| Glass Engine | `.../Glass_Engine/V9_....musicxml` | Richest harmony; guitar needs thinning by ~half. |

## Removed 17 Sep 2026 (recoverable from git history)

- **Fractured Motion — ECM Chamber (V1–V5)** — 41 bars, 8 guitar notes, all 5 files corrupt. Not a composition yet.
- **Eviscerating Angels (V4, V5)** — 5/4 at 76bpm is high-risk without a drummer; tonal outlier.
- **21 superseded versions** — later version numbers were consistently *worse*: `Myrtle's Prayer V5` lost 68% of the guitar part, `Harmolodic V4` lost two sections, `First Light V2/V3` put the flugelhorn below its range, `Mirror V3` lost a quarter of the melody.

## Validation gate — ACTIVE

Scores are checked on every commit by `tools/validate_scores.py`.

**One-time setup per machine** (hook config is local and cannot be committed):

```
setup-hooks.bat        (Windows)
./setup-hooks.sh       (Mac/Linux)
```

Manual runs:

```
python tools/validate_scores.py --all       # every tracked score
python tools/validate_scores.py --staged    # what you're about to commit
```

Blocks a commit on: malformed XML, missing `<part-list>`, a declared part with no
music, zero measures, out-of-range octaves. Warns on: a part under 6% sounding
notes (unwritten rather than deliberately sparse), missing tempo marking.
The 6% threshold sits well below the sparsest legitimate part in this repo
(North Light's flugelhorn, 32%), so real ECM sparseness passes untouched.
Emergency override: `SKIP_SCORE_CHECK=1 git commit ...`

Regression-tested against the two faults that actually occurred here: it fails
the broken Lyrical Expansion V1 and names the exact fix, and it flags Orbit V1's
empty guitar part.

## Where the bad files came from

There is no generator script. Nothing in this repo emits these scores — the two
HTML apps produce a different, simpler MusicXML with no tempo directions at all.
The `<software>` tags name a working method rather than a program
(`GCE-Jazz V1.0`, `DTE v2.1`, `Breath-Stop`), and the quartet pieces sit under
`Documents/Cursor AI Projects/`. These files were written as raw MusicXML text by
AI sessions.

Two distinct producers are visible in the formatting. The quartet family is
pretty-printed with `<sound tempo="63" />` and is well-formed throughout. The
chamber-trio family is compact with `<sound tempo="52"/>` and is where all seven
broken files occurred. The failure was intermittent — 7 of 20 files — which is
why a validation gate is the right fix and a code patch is not.

## The original fault

Seven files were emitted with an unclosed metronome direction:

```xml
<!-- broken -->
</metronome></direction-type>
<sound tempo="54"/>
<!-- correct -->
</metronome></direction-type></direction>
<sound tempo="54"/>
```

This makes the file unopenable in Sibelius, MuseScore and Dorico. `Lyrical_Expansion_ECM_V2` has been patched; the other six files were deleted. The commit gate above catches any recurrence.

## Next actions

1. Write the guitar part for `Orbit — ECM Chamber V3`. Best harmonic material in the repo, ~60% unwritten.
2. Extend `Lyrical Expansion V2` to ~110 bars with an embedded dialogue improvisation; promote to title track.
3. Generate flugelhorn/guitar/bass lead-sheet PDFs — this repo currently has **zero** printable parts.
4. Verify authorship on any title imported from the GCE-Jazz repo before release.


## The Mirror — repairs, 2026-09-18

Three faults found and fixed in `Mirror-Chamber/Mirror_Chamber_ECM_V1.musicxml`:

1. **Guitar was one bar short** (59 bars against 60). Inserted bar 40 as a whole
   rest. All three parts now 60 bars.
2. **Flugelhorn transposition was wrong.** The part carried `transpose -2` and a
   written key of Ab major (-4) — i.e. declared as a Bb instrument but with
   concert-pitch notes and a concert key signature. Any notation program would
   have played and printed it a tone flat. Notes transposed up a major 2nd and
   written key set to Bb major (-2), so the part now reads correctly for the
   player and sounds as composed. Sounding pitch is now identical to the
   original written pitch.
3. **Flugelhorn went too high.** Bar 28 would have been written C#6 after
   correction, well above the register where the instrument stays reliable.
   Lowered to concert F#5 (written G#5), which also improves the contour —
   the phrase now descends from the bar 26 peak instead of leaping to a bare root.

Also added **29 chord symbols** across the form, derived from the bass roots and
guitar dyads. The file previously had none, so it could not be read or improvised
over. Form: Abmaj9 / Absus / Ab7 / Abm — B–E chromatic pair — Bmaj7 with B/E
oscillation through Sections B and C — Ab pedal and silence — Dbmaj9 / Dbm —
Abmaj7 with the closing descent.

Written flugelhorn range is now D4–Bb5. The single Bb5 (bar 26, concert Ab5, the
sixth over B major) is the one demanding note; it can drop an octave if the
player prefers.

Still to do on this piece: the alto part through Sections B, C and D.
