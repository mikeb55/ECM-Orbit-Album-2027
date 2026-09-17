#!/usr/bin/env python3
"""
MusicXML validation gate for ECM-Orbit-Album-2027.

Blocks commits containing scores that no notation program could open, and warns
about scores that open fine but are missing content.

Rationale: seven files in this repo (all Lyrical-Expansion and Fractured-Slowed
versions) shipped with an unclosed <direction> element and were unopenable in
Sibelius, MuseScore and Dorico. They sat broken in the repo for months because
nothing checked. Separately, Orbit ECM Chamber V1 was committed with a guitar
part containing zero notes. This catches both classes of fault.

Usage:
    python tools/validate_scores.py [files...]    # explicit files
    python tools/validate_scores.py --staged      # git staged files (hook mode)
    python tools/validate_scores.py --all         # every tracked score

Exit codes: 0 = pass (warnings allowed), 1 = at least one blocking error.
Override in an emergency with SKIP_SCORE_CHECK=1 git commit ...
"""

import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

SCORE_EXT = (".musicxml", ".xml", ".mxl")

# A part with a sounding-note ratio below this is almost certainly unwritten
# rather than deliberately sparse. Tuned so that genuine ECM sparseness passes:
# the sparsest legitimate part in this repo is North Light's flugelhorn at 0.32.
EMPTY_PART_THRESHOLD = 0.06

RED = "\033[31m"
YEL = "\033[33m"
GRN = "\033[32m"
OFF = "\033[0m"
if not sys.stdout.isatty() or os.name == "nt":
    RED = YEL = GRN = OFF = ""


def strip_ns(text):
    """Remove default namespace so ElementTree paths stay simple."""
    return re.sub(r'\sxmlns="[^"]+"', "", text)


def validate(path):
    """Return (errors, warnings) for one score file."""
    errors, warnings = [], []

    if path.endswith(".mxl"):
        return errors, warnings  # compressed; zip integrity only, skip

    try:
        with open(path, encoding="utf-8", errors="strict") as fh:
            raw = fh.read()
    except UnicodeDecodeError as exc:
        return [f"not valid UTF-8: {exc}"], warnings
    except OSError as exc:
        return [f"unreadable: {exc}"], warnings

    try:
        root = ET.fromstring(strip_ns(raw))
    except ET.ParseError as exc:
        line = getattr(exc, "position", (None,))[0]
        hint = ""
        # The exact fault that broke seven files in this repo.
        if "</metronome></direction-type>" in raw and "</direction>" in raw:
            if re.search(r"</metronome></direction-type>\s*\n\s*<sound", raw):
                hint = (
                    "  -> looks like the known bug: <direction> is never closed. "
                    "Change '</metronome></direction-type>' to "
                    "'</metronome></direction-type></direction>'"
                )
        errors.append(f"malformed XML at line {line}: {exc.msg if hasattr(exc,'msg') else exc}{chr(10) + hint if hint else ''}")
        return errors, warnings

    if root.tag not in ("score-partwise", "score-timewise"):
        errors.append(f"root element is <{root.tag}>, expected <score-partwise>")
        return errors, warnings

    declared = [p.get("id") for p in root.findall(".//score-part")]
    if not declared:
        errors.append("no <part-list> — no notation program will render this")
        return errors, warnings

    parts = root.findall(".//part")
    if not parts:
        errors.append("part-list declared but no <part> content")
        return errors, warnings

    names = {
        p.get("id"): (p.findtext("part-name") or p.get("id"))
        for p in root.findall(".//score-part")
    }

    # Declared parts that never appear as content, and vice versa.
    present = {p.get("id") for p in parts}
    for pid in declared:
        if pid not in present:
            errors.append(f"part '{names.get(pid, pid)}' declared but has no music")

    total_measures = 0
    for part in parts:
        pid = part.get("id")
        label = names.get(pid, pid)
        measures = part.findall("measure")
        if not measures:
            errors.append(f"part '{label}' has zero measures")
            continue
        total_measures = max(total_measures, len(measures))

        notes = part.findall(".//note")
        sounding = [n for n in notes if n.find("rest") is None]
        if not notes:
            errors.append(f"part '{label}' has no notes or rests at all")
            continue
        ratio = len(sounding) / len(notes)
        if ratio <= EMPTY_PART_THRESHOLD:
            warnings.append(
                f"part '{label}' is {ratio:.0%} sounding "
                f"({len(sounding)} notes in {len(measures)} bars) — likely unwritten, not sparse"
            )

        # Pitches outside plausible written range usually mean an octave slip.
        for note in sounding:
            pitch = note.find("pitch")
            if pitch is None:
                continue
            octave = pitch.findtext("octave")
            if octave is not None and not (0 <= int(octave) <= 9):
                errors.append(f"part '{label}' has out-of-range octave {octave}")
                break

    if total_measures == 0:
        errors.append("score contains no measures")

    # Parts of unequal length will not line up in performance. This caught
    # The Mirror, where the guitar was one bar short of the other two parts.
    lengths = {p.get("id"): len(p.findall("measure")) for p in parts}
    if len(set(lengths.values())) > 1:
        detail = ", ".join(
            f"{names.get(k, k)}={v}" for k, v in sorted(lengths.items(), key=lambda kv: -kv[1])
        )
        errors.append(f"parts have different bar counts ({detail})")

    if not root.findall(".//sound[@tempo]") and not root.findall(".//metronome"):
        warnings.append("no tempo marking found")

    return errors, warnings


def collect(args):
    if "--staged" in args:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True, check=False,
        ).stdout
        return [f for f in out.splitlines() if f.endswith(SCORE_EXT) and os.path.exists(f)]
    if "--all" in args:
        out = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=False
        ).stdout
        return [f for f in out.splitlines() if f.endswith(SCORE_EXT) and os.path.exists(f)]
    return [f for f in args if f.endswith(SCORE_EXT)]


def main():
    files = collect(sys.argv[1:])
    if not files:
        return 0

    failed = 0
    warned = 0
    for path in sorted(files):
        errors, warnings = validate(path)
        if errors:
            failed += 1
            print(f"{RED}FAIL{OFF}  {path}")
            for e in errors:
                print(f"      {RED}x{OFF} {e}")
        elif warnings:
            warned += 1
            print(f"{YEL}WARN{OFF}  {path}")
        else:
            print(f"{GRN}ok{OFF}    {path}")
        for w in warnings:
            print(f"      {YEL}!{OFF} {w}")

    print(f"\n{len(files)} score(s) checked — {failed} failed, {warned} with warnings")
    if failed:
        print(
            f"\n{RED}Commit blocked.{OFF} These files cannot be opened by Sibelius, "
            f"MuseScore or Dorico.\nFix them, or override with: "
            f"SKIP_SCORE_CHECK=1 git commit ..."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
