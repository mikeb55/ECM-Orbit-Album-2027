@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM ECM_ORBIT_REPO_REPAIR.bat
REM - Runs only in ECM-Orbit-Album-2027
REM - Backup non-album to _NONALBUM_LOCAL_BACKUP (copy, keep local)
REM - Untrack non-album via git rm --cached
REM - Add/replace single block in .gitignore (no duplicate)
REM - Commit, push main, force-push main to home/mike
REM - Verify and report remaining junk
REM ============================================================

set "REPO=C:\Users\mike\Documents\Cursor AI Projects\ECM-Orbit-Album-2027"
set "LOG=%REPO%\ECM_ORBIT_REPO_REPAIR.log"
set "BATDIR=%~dp0"
set "EXPORT=%REPO%\_NONALBUM_LOCAL_BACKUP"

> "%LOG%" echo ECM_ORBIT_REPO_REPAIR
>>"%LOG%" echo Started: %DATE% %TIME%
>>"%LOG%" echo Repo: %REPO%
>>"%LOG%" echo ============================================================

echo ============================================================
echo ECM ORBIT REPO REPAIR
echo Repo: %REPO%
echo Log:  %LOG%
echo ============================================================
echo.

if not exist "%REPO%\.git\" (
  echo ERROR: No .git found at %REPO%
  echo This folder is not a git repository. Cannot proceed.
  >>"%LOG%" echo ERROR: No .git at %REPO%
  echo.
  pause
  exit /b 1
)

pushd "%REPO%" >nul

where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: git not found on PATH.
  >>"%LOG%" echo ERROR: git not found on PATH.
  popd >nul
  pause
  exit /b 1
)

REM Enforce correct working directory
for /f "delims=" %%A in ('git rev-parse --show-toplevel') do set "TOP=%%A"
set "TOPN=!TOP:/=\!"
if /I not "!TOPN!"=="%REPO%" (
  echo ERROR: Git top-level does not match. Expected: %REPO%
  echo Actual: !TOP!
  >>"%LOG%" echo ERROR: Top-level mismatch
  popd >nul
  pause
  exit /b 1
)

echo --- Git status (before) ---
git status
echo.
>>"%LOG%" echo --- git status (before) ---
git status >>"%LOG%" 2>&1
>>"%LOG%" echo.

REM Create backup folder
if not exist "%EXPORT%\" mkdir "%EXPORT%" >nul 2>&1

echo --- Backing up non-album items to %EXPORT% ---
>>"%LOG%" echo Backing up to %EXPORT%

set "NONALBUM_DIRS=Documents profiles backups backup-20250917 Mike Songs 2025"
for %%D in (%NONALBUM_DIRS%) do (
  if exist "%%~D\" (
    echo   Copy dir: %%~D
    >>"%LOG%" echo Copy dir: %%~D
    xcopy "%%~D" "%EXPORT%\%%~D\" /E /I /H /Y >nul 2>&1
  )
)

for %%F in (quintet*.html *.js *.sh bulletproof_integrated.html index*.html index-enhanced.html INTEGRATION_NOTES.md apply_intervals.js batch-operations-universal.js complete_profiles.js fix.js gml-shared-memory.js profile_loader.js quintet-enhanced.html rapid_composer_memory.js rhythm_patterns.js structure_generator.js ui-improvements-universal.js) do (
  if exist "%%~F" (
    echo   Copy file: %%~F
    >>"%LOG%" echo Copy file: %%~F
    copy /Y "%%~F" "%EXPORT%\" >nul 2>&1
  )
)

if exist "profiles\" (
  xcopy "profiles" "%EXPORT%\profiles\" /E /I /H /Y >nul 2>&1
)

echo.
echo --- Untracking non-album content (git rm --cached, keep local) ---
>>"%LOG%" echo Untracking non-album

REM Untrack by pattern - everything not in allowlist
REM Allowlist: Album Mirror-Chamber FirstLight-Chamber NorthLight-Pivot Fractured-Slowed Orbit-Slowed HarmolodicSketch-Gravitational Lyrical-Expansion Interlude-Reset README.md .gitignore

REM Untrack known junk dirs
for %%D in (Documents profiles backups backup-20250917 "Mike Songs 2025") do (
  git rm -r --cached "%%~D" >>"%LOG%" 2>&1
)

REM Untrack root junk files
git rm --cached quintet*.html >>"%LOG%" 2>&1
git rm --cached *.js >>"%LOG%" 2>&1
git rm --cached *.sh >>"%LOG%" 2>&1
git rm --cached bulletproof_integrated.html >>"%LOG%" 2>&1
git rm --cached index.html >>"%LOG%" 2>&1
git rm --cached index-enhanced.html >>"%LOG%" 2>&1
git rm --cached INTEGRATION_NOTES.md >>"%LOG%" 2>&1

REM Untrack Documents/ paths (from parent-repo bleed)
git rm -r --cached "Documents" >>"%LOG%" 2>&1

echo.
echo --- Update .gitignore (replace block if exists, no duplicate) ---
>>"%LOG%" echo Updating .gitignore

set "GITIGNORE=%REPO%\.gitignore"
set "GITTMP=%REPO%\.gitignore.tmp"
set "BLOCK_START=# ---- ECM_ORBIT_NONALBUM_IGNORE_START ----"
set "BLOCK_END=# ---- ECM_ORBIT_NONALBUM_IGNORE_END ----"

set "inblock=0"
set "wroteblock=0"
if exist "%GITTMP%" del "%GITTMP%"

for /f "usebackq delims=" %%L in ("%GITIGNORE%") do (
  set "line=%%L"
  echo !line! | findstr /C:"%BLOCK_END%" >nul 2>&1
  if not errorlevel 1 (
    set "inblock=0"
  ) else (
    echo !line! | findstr /C:"%BLOCK_START%" >nul 2>&1
    if not errorlevel 1 (
      set "inblock=1"
      if "!wroteblock!"=="0" (
        echo.>> "%GITTMP%"
        echo %BLOCK_START%>> "%GITTMP%"
        echo _NONALBUM_LOCAL_BACKUP/>> "%GITTMP%"
        echo _QUARANTINE/>> "%GITTMP%"
        echo Documents/>> "%GITTMP%"
        echo profiles/>> "%GITTMP%"
        echo backups/>> "%GITTMP%"
        echo backup-20250917/>> "%GITTMP%"
        echo Mike Songs 2025/>> "%GITTMP%"
        echo quintet*.html>> "%GITTMP%"
        echo %BLOCK_END%>> "%GITTMP%"
        set "wroteblock=1"
      )
    ) else (
      if "!inblock!"=="0" echo !line!>> "%GITTMP%"
    )
  )
)

if "!wroteblock!"=="0" (
  echo.>> "%GITTMP%"
  echo %BLOCK_START%>> "%GITTMP%"
  echo _NONALBUM_LOCAL_BACKUP/>> "%GITTMP%"
  echo _QUARANTINE/>> "%GITTMP%"
  echo Documents/>> "%GITTMP%"
  echo profiles/>> "%GITTMP%"
  echo backups/>> "%GITTMP%"
  echo backup-20250917/>> "%GITTMP%"
  echo Mike Songs 2025/>> "%GITTMP%"
  echo quintet*.html>> "%GITTMP%"
  echo %BLOCK_END%>> "%GITTMP%"
)

move /Y "%GITTMP%" "%GITIGNORE%" >nul

git add .gitignore >>"%LOG%" 2>&1

echo.
echo --- Commit and push ---
>>"%LOG%" echo Commit and push

git add -A >>"%LOG%" 2>&1
git status
echo.

git diff --cached --quiet 2>nul
if not errorlevel 1 (
  echo Nothing staged. Skipping commit.
  >>"%LOG%" echo Nothing staged.
) else (
  git commit -m "Repo repair: remove non-album content from tracking (kept locally in _NONALBUM_LOCAL_BACKUP)" >>"%LOG%" 2>&1
  git push origin main >>"%LOG%" 2>&1
  echo.
  echo --- Force-push main to origin home/mike ---
  git push --force origin main:home/mike >>"%LOG%" 2>&1
)

echo.
echo ============================================================
echo VERIFICATION
echo ============================================================
>>"%LOG%" echo ============================================================
>>"%LOG%" echo VERIFICATION
>>"%LOG%" echo ============================================================

echo.
echo git rev-parse --show-toplevel:
git rev-parse --show-toplevel
>>"%LOG%" echo Top-level:
git rev-parse --show-toplevel >>"%LOG%" 2>&1

echo.
echo git branch -vv:
git branch -vv
>>"%LOG%" echo Branch:
git branch -vv >>"%LOG%" 2>&1

echo.
echo git remote -v:
git remote -v
>>"%LOG%" echo Remotes:
git remote -v >>"%LOG%" 2>&1

echo.
echo git ls-remote --heads origin:
git ls-remote --heads origin
>>"%LOG%" echo Remote heads:
git ls-remote --heads origin >>"%LOG%" 2>&1

echo.
echo git status:
git status
>>"%LOG%" echo Status:
git status >>"%LOG%" 2>&1

echo.
echo Remaining tracked paths matching junk patterns:
>>"%LOG%" echo Remaining junk:
set "FOUND_JUNK=0"
for /f "delims=" %%P in ('git ls-files 2^>nul ^| findstr /I /C:"Mike Songs 2025" /C:"quintet" /C:"profiles" /C:"backups" /C:"backup-20250917" /C:"home/mike" /C:"Documents"') do (
  echo   %%P
  >>"%LOG%" echo %%P
  set "FOUND_JUNK=1"
)
if "!FOUND_JUNK!"=="0" (
  echo   (none)
  >>"%LOG%" echo (none)
)

echo.
>>"%LOG%" echo Finished: %DATE% %TIME%
>>"%LOG%" echo ============================================================

popd >nul

echo ============================================================
echo Done. Log: %LOG%
echo Press any key to close.
echo ============================================================
pause >nul
endlocal
