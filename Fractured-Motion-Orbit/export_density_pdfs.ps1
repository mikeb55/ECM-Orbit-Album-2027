# Export Fractured Motion Orbit Trio Density PDFs via MuseScore 4
# Requires: MuseScore 4 installed at "C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
# Usage: .\export_density_pdfs.ps1 [version]

param([int]$Version = 1)

$mscore = "C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
$base = Split-Path -Parent $MyInvocation.MyCommand.Path
$xml = Join-Path $base "MusicXML\fractured_motion_orbit_trio_density_v$Version.musicxml"
$outDir = Join-Path $base "LeadSheets"

if (-not (Test-Path $xml)) {
    Write-Error "MusicXML not found: $xml. Run: py generate_orbit_trio_density.py $Version"
    exit 1
}

if (-not (Test-Path $mscore)) {
    Write-Error "MuseScore 4 not found at $mscore"
    exit 1
}

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

# Full score PDF
& $mscore -o "$outDir\fractured_motion_orbit_trio_density_v$Version.pdf" $xml
Write-Host "Exported: fractured_motion_orbit_trio_density_v$Version.pdf"

# Score + all parts in one PDF (for printing)
& $mscore -P -o "$outDir\fractured_motion_orbit_trio_density_v${Version}_score_and_parts.pdf" $xml
Write-Host "Exported: fractured_motion_orbit_trio_density_v${Version}_score_and_parts.pdf"

Write-Host ""
Write-Host "For individual part PDFs (flugel, guitar, bass):"
Write-Host "  Open $xml in MuseScore, File > Export Parts, select each part, export as PDF."
Write-Host "  Save as: fractured_motion_orbit_flugel_v$Version.pdf, _guitar_v$Version.pdf, _bass_v$Version.pdf"
