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

## Known generator bug — FIXED IN FILES, NOT IN CODE

Seven files were emitted with an unclosed metronome direction:

```xml
<!-- broken -->
</metronome></direction-type>
<sound tempo="54"/>
<!-- correct -->
</metronome></direction-type></direction>
<sound tempo="54"/>
```

This makes the file unopenable in Sibelius, MuseScore and Dorico. `Lyrical_Expansion_ECM_V2` has been patched. **The generator that produced this has not been fixed** — check every new chamber export until it is.

## Next actions

1. Write the guitar part for `Orbit — ECM Chamber V3`. Best harmonic material in the repo, ~60% unwritten.
2. Extend `Lyrical Expansion V2` to ~110 bars with an embedded dialogue improvisation; promote to title track.
3. Generate flugelhorn/guitar/bass lead-sheet PDFs — this repo currently has **zero** printable parts.
4. Verify authorship on any title imported from the GCE-Jazz repo before release.
