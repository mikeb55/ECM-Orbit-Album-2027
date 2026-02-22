@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM ECM ORBIT - ONE FILE CHECK + QUARANTINE (single .bat)
REM - Stays open
REM - Writes log next to this .bat
REM - Validates repo root is correct folder
REM - Shows git status/branch/upstream/remotes
REM - Detects quintet*.html and classifies:
REM   - TRACKED (in git) -> reports safe removal command
REM   - UNTRACKED -> auto-moves to _QUARANTINE (non-destructive)
REM ============================================================

set "REPO=C:\Users\mike\Documents\Cursor AI Projects\ECM-Orbit-Album-2027"
set "BATDIR=%~dp0"
set "LOG=%BATDIR%ECM_Orbit_OneCheck.log"
set "QUAR=%REPO%\_QUARANTINE"

> "%LOG%" echo ECM ORBIT ONE FILE CHECK LOG
>>"%LOG%" echo Started: %DATE% %TIME%
>>"%LOG%" echo Repo expected: "%REPO%"
>>"%LOG%" echo Bat location: "%BATDIR%"
>>"%LOG%" echo ============================================================

echo ============================================================
echo ECM ORBIT - ONE FILE CHECK
echo Repo expected: "%REPO%"
echo Log file:      "%LOG%"
echo ============================================================
echo.

if not exist "%REPO%\" (
  echo ERROR: Repo folder does not exist.
  echo "%REPO%"
  >>"%LOG%" echo ERROR: Repo folder missing: "%REPO%"
  goto :END
)

pushd "%REPO%" >nul

where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: git not found on PATH.
  >>"%LOG%" echo ERROR: git not found on PATH.
  popd >nul
  goto :END
)

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo ERROR: This folder is not a git repo (no .git).
  >>"%LOG%" echo ERROR: Not a git repo: "%REPO%"
  popd >nul
  goto :END
)

for /f "usebackq delims=" %%A in (`git rev-parse --show-toplevel`) do set "TOP=%%A"
set "TOPN=!TOP:/=\!"
set "REPON=%REPO%"

echo Git top-level:
echo   !TOP!
echo.
>>"%LOG%" echo Git top-level: !TOP!

if /I not "!TOPN!"=="!REPON!" (
  echo WARNING: Git top-level does NOT match expected repo folder.
  echo Expected: %REPO%
  echo Actual:   !TOP!
  echo.
  >>"%LOG%" echo WARNING: Top-level mismatch. Expected "%REPO%" Actual "!TOP!"
) else (
  echo OK: Git top-level matches expected repo folder.
  echo.
  >>"%LOG%" echo OK: Top-level matches expected.
)

echo Branch / upstream:
git branch -vv
echo.
>>"%LOG%" echo Branch / upstream:
git branch -vv >>"%LOG%" 2>&1
>>"%LOG%" echo.

echo Remotes:
git remote -v
echo.
>>"%LOG%" echo Remotes:
git remote -v >>"%LOG%" 2>&1
>>"%LOG%" echo.

echo Status:
git status
echo.
>>"%LOG%" echo Status:
git status >>"%LOG%" 2>&1
>>"%LOG%" echo.

REM ------------------------------------------------------------
REM QUINTET FILES DIAGNOSIS
REM ------------------------------------------------------------
echo ============================================================
echo CHECKING FOR UNEXPECTED quintet*.html FILES
echo ============================================================
>>"%LOG%" echo ============================================================
>>"%LOG%" echo Checking for unexpected quintet*.html files
>>"%LOG%" echo ============================================================

REM 1) List any matching files present in folder
set "FOUND_ANY=0"
for %%F in ("%REPO%\quintet*.html") do (
  if exist "%%~fF" (
    set "FOUND_ANY=1"
  )
)

if "!FOUND_ANY!"=="0" (
  echo None found in repo root (quintet*.html).
  echo.
  >>"%LOG%" echo None found in repo root (quintet*.html).
  goto :DONE_QUINTET
)

echo Found these files in repo root:
dir /b "%REPO%\quintet*.html"
echo.
>>"%LOG%" echo Found these files in repo root:
for /f "delims=" %%L in ('dir /b "%REPO%\quintet*.html"') do >>"%LOG%" echo %%L
>>"%LOG%" echo.

REM 2) Determine which are tracked by git
echo Tracked-by-git (if any):
git ls-files "quintet*.html"
echo.
>>"%LOG%" echo Tracked-by-git (if any):
git ls-files "quintet*.html" >>"%LOG%" 2>&1
>>"%LOG%" echo.

REM 3) Auto-quarantine only UNTRACKED files (safe move)
if not exist "%QUAR%\" mkdir "%QUAR%" >nul 2>&1

set "MOVED=0"
for /f "delims=" %%L in ('dir /b "%REPO%\quintet*.html"') do (
  REM Check if tracked
  git ls-files --error-unmatch "%%L" >nul 2>&1
  if errorlevel 1 (
    REM Not tracked -> move to quarantine
    move /Y "%REPO%\%%L" "%QUAR%\" >nul
    set "MOVED=1"
    echo QUARANTINED (untracked): %%L
    >>"%LOG%" echo QUARANTINED (untracked): %%L
  ) else (
    echo TRACKED (not moved): %%L
    >>"%LOG%" echo TRACKED (not moved): %%L
  )
)

echo.
if "!MOVED!"=="1" (
  echo Untracked quintet*.html files were moved to:
  echo   "%QUAR%"
  echo.
  >>"%LOG%" echo Untracked quintet*.html files moved to "%QUAR%".
) else (
  echo No untracked quintet*.html files to quarantine.
  echo.
  >>"%LOG%" echo No untracked quintet*.html files to quarantine.
)

REM 4) If tracked files exist, print safe removal command (DO NOT RUN)
set "HAS_TRACKED=0"
for /f "delims=" %%T in ('git ls-files "quintet*.html"') do (
  set "HAS_TRACKED=1"
)

if "!HAS_TRACKED!"=="1" (
  echo NOTE: Some quintet*.html files are TRACKED by git.
  echo If you want them removed from the repo, run:
  echo   git rm -f quintet*.html ^&^& git commit -m "Remove unrelated quintet HTML files" ^&^& git push
  echo.
  >>"%LOG%" echo NOTE: tracked quintet*.html exist. Suggested removal:
  >>"%LOG%" echo git rm -f quintet*.html ^&^& git commit -m "Remove unrelated quintet HTML files" ^&^& git push
  >>"%LOG%" echo.
)

:DONE_QUINTET

REM Show status again after any quarantine moves
echo ============================================================
echo STATUS AFTER QUARANTINE CHECK
echo ============================================================
git status
echo.
>>"%LOG%" echo ============================================================
>>"%LOG%" echo Status after quarantine check:
git status >>"%LOG%" 2>&1
>>"%LOG%" echo.

popd >nul

:END
>>"%LOG%" echo Finished: %DATE% %TIME%
>>"%LOG%" echo ============================================================

echo ============================================================
echo Done. Press any key to close.
echo Log: "%LOG%"
echo ============================================================
pause >nul
endlocal
