@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Do not optimise phrasing. Do not balance symmetry. Preserve asymmetry.

set "WORK=%TEMP%\ecm_quintet_migration_%RANDOM%%RANDOM%"
set "ECM_URL=https://github.com/mikeb55/ECM-Orbit-Album-2027.git"
set "QUINTET_URL=https://github.com/mikeb55/gml-quintet-composer.git"

mkdir "%WORK%" >nul 2>&1
cd /d "%WORK%"

echo === Cloning repos to: %WORK% ===
git clone "%ECM_URL%" ecm || goto :ERR
git clone "%QUINTET_URL%" quintet || goto :ERR

REM ----------------------------
REM 1) COPY Quintet/GML files BACK into gml-quintet-composer
REM ----------------------------
cd /d "%WORK%\ecm"
git fetch origin >nul 2>&1

REM ECM repo is currently showing junk on branch home/mike
git checkout "home/mike" || goto :ERR

cd /d "%WORK%\quintet"
git checkout main >nul 2>&1
git pull --rebase origin main || goto :ERR

REM Create folders if needed
if not exist "js\" mkdir "js" >nul 2>&1

echo === Copying Quintet/GML artifacts from ECM -^> Quintet (only if missing) ===

REM Root HTML artifacts
for %%F in (
  "quintet-enhanced.html"
  "quintet_composer_v2.0_with_profiles.html"
  "quintet_composer_v3.0_harmonic.html"
  "quintet_composer_v7_final.html"
  "quintet_composer_v9_LAST_KNOWN_GOOD.html"
  "quintet_composer_v9_WORKING.html"
  "quintet_composer_v13_PRODUCTION.html"
  "quintet_composer_v16_HARMONIZED.html"
  "bulletproof_integrated.html"
  "index.html"
  "index-enhanced.html"
  "INTEGRATION_NOTES.md"
) do (
  if not exist "%%~F" (
    if exist "%WORK%\ecm\%%~F" copy /Y "%WORK%\ecm\%%~F" "%%~F" >nul
  )
)

REM Directories (profiles/backups) - copy if missing
for %%D in ("profiles" "backups" "backup-20250917") do (
  if exist "%WORK%\ecm\%%~D\" (
    if not exist "%%~D\" (
      xcopy "%WORK%\ecm\%%~D" "%%~D\" /E /I /H /Y >nul
    )
  )
)

REM JS files found in ECM root -^> put into quintet/js/ (only if missing)
for %%J in (
  "apply_intervals.js"
  "batch-operations-universal.js"
  "complete_profiles.js"
  "fix.js"
  "gml-shared-memory.js"
  "profile_loader.js"
  "rapid_composer_memory.js"
  "rhythm_patterns.js"
  "structure_generator.js"
  "ui-improvements-universal.js"
) do (
  if exist "%WORK%\ecm\%%~J" (
    if not exist "js\%%~J" (
      copy /Y "%WORK%\ecm\%%~J" "js\%%~J" >nul
    )
  )
)

REM Commit + push to quintet repo (only if changes)
git status
git status --porcelain | findstr /r "." >nul 2>&1
if errorlevel 1 (
  echo === No changes needed in quintet repo ===
) else (
  git add -A
  git commit -m "Restore Quintet/GML artifacts that were mistakenly committed to ECM-Orbit-Album-2027" || goto :ERR
  git push origin main || goto :ERR
)

REM ----------------------------
REM 2) CLEAN ECM repo (remove Quintet/GML + personal folders) from home/mike
REM ----------------------------
cd /d "%WORK%\ecm"
git checkout "home/mike" || goto :ERR
git pull --rebase origin "home/mike" || goto :ERR

echo === Removing non-album content from ECM (home/mike) ===

REM Remove personal folders (these should NOT be in any repo)
git rm -r --ignore-unmatch "Documents" >nul 2>&1
git rm -r --ignore-unmatch "Mike Songs 2025" >nul 2>&1

REM Remove Quintet/GML artifacts from ECM root
git rm -f --ignore-unmatch ^
  quintet-enhanced.html ^
  quintet_composer_v2.0_with_profiles.html ^
  quintet_composer_v3.0_harmonic.html ^
  quintet_composer_v7_final.html ^
  quintet_composer_v9_LAST_KNOWN_GOOD.html ^
  quintet_composer_v9_WORKING.html ^
  quintet_composer_v13_PRODUCTION.html ^
  quintet_composer_v16_HARMONIZED.html ^
  bulletproof_integrated.html ^
  index.html ^
  index-enhanced.html ^
  INTEGRATION_NOTES.md >nul 2>&1

REM Remove folders used by Quintet/GML
git rm -r --ignore-unmatch "profiles" "backups" "backup-20250917" >nul 2>&1

REM Remove JS tooling files from ECM root
git rm -f --ignore-unmatch ^
  apply_intervals.js ^
  batch-operations-universal.js ^
  complete_profiles.js ^
  fix.js ^
  gml-shared-memory.js ^
  profile_loader.js ^
  rapid_composer_memory.js ^
  rhythm_patterns.js ^
  structure_generator.js ^
  ui-improvements-universal.js >nul 2>&1

REM Commit + push ECM cleanup if changes
git status
git status --porcelain | findstr /r "." >nul 2>&1
if errorlevel 1 (
  echo === No changes needed in ECM repo ===
) else (
  git add -A
  git commit -m "Cleanup: remove Quintet/GML tooling and personal folders (belongs in gml-quintet-composer)" || goto :ERR
  git push origin "home/mike" || goto :ERR
)

echo.
echo === DONE ===
echo Quintet repo updated, ECM home/mike cleaned.
echo Work folder: %WORK%
echo.
pause
exit /b 0

:ERR
echo.
echo ERROR: Migration failed. Work folder preserved for inspection:
echo   %WORK%
echo.
pause
exit /b 1
