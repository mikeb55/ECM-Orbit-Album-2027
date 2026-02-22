@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM FIX_ECM_REPO_KEEP_LOCAL.bat
REM - Removes non-album items from GitHub repo (untracks them)
REM - Keeps local copies (uses git rm --cached)
REM - Creates local backup copy before untracking
REM - Commits + pushes cleanup
REM ============================================================

set "REPO=C:\Users\mike\Documents\Cursor AI Projects\ECM-Orbit-Album-2027"
set "LOG=%REPO%\FIX_ECM_REPO_KEEP_LOCAL.log"
set "BRANCH=main"
set "EXPORT=%REPO%\_NONALBUM_LOCAL_BACKUP"

REM Album allowlist (top-level dirs you intend to keep tracked)
set "KEEP_DIRS=Album Mirror-Chamber FirstLight-Chamber NorthLight-Pivot Fractured-Slowed Orbit-Slowed HarmolodicSketch-Gravitational Lyrical-Expansion Interlude-Reset"

REM Known non-album dirs seen on GitHub
set "NONALBUM_DIRS=Documents profiles backups backup-20250917 Mike Songs 2025"

REM Known non-album root artifacts (quintet + gml tooling) seen on GitHub
set "NONALBUM_GLOBS=quintet*.html *.js *.sh bulletproof_integrated.html index*.html INTEGRATION_NOTES.md"

> "%LOG%" echo FIX_ECM_REPO_KEEP_LOCAL
>>"%LOG%" echo Started: %DATE% %TIME%
>>"%LOG%" echo Repo: %REPO%
>>"%LOG%" echo ============================================================

echo ============================================================
echo FIX ECM ORBIT REPO (REMOVE NON-ALBUM FROM GITHUB, KEEP LOCAL)
echo Repo: %REPO%
echo Log : %LOG%
echo ============================================================
echo.

if not exist "%REPO%\.git\" (
  echo ERROR: No .git found at %REPO%
  >>"%LOG%" echo ERROR: No .git found at %REPO%
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

echo --- Git status (before) ---
git status
echo.
>>"%LOG%" echo --- git status (before) ---
git status >>"%LOG%" 2>&1
>>"%LOG%" echo.

echo --- Checkout + pull ---
git checkout %BRANCH% >>"%LOG%" 2>&1
git pull --rebase origin %BRANCH% >>"%LOG%" 2>&1

REM Create local backup folder
if not exist "%EXPORT%\" mkdir "%EXPORT%" >nul 2>&1

echo.
echo --- Backing up non-album items to: %EXPORT% ---
>>"%LOG%" echo Backing up non-album items to: %EXPORT%

REM Copy non-album directories if they exist
for %%D in (%NONALBUM_DIRS%) do (
  if exist "%%~D\" (
    echo   Copy dir: %%~D
    >>"%LOG%" echo Copy dir: %%~D
    xcopy "%%~D" "%EXPORT%\%%~D\" /E /I /H /Y >nul
  )
)

REM Copy non-album root files matching globs (only if they exist)
for %%G in (%NONALBUM_GLOBS%) do (
  for %%F in (%%G) do (
    if exist "%%~F" (
      echo   Copy file: %%~F
      >>"%LOG%" echo Copy file: %%~F
      copy /Y "%%~F" "%EXPORT%\" >nul
    )
  )
)

echo.
echo --- Untracking non-album content (keeps local files) ---
>>"%LOG%" echo Untracking non-album content (git rm --cached)

REM Untrack directories (keep local)
for %%D in (%NONALBUM_DIRS%) do (
  if exist "%%~D\" (
    echo   git rm -r --cached "%%~D"
    git rm -r --cached "%%~D" >>"%LOG%" 2>&1
  )
)

REM Untrack root files/globs (keep local)
for %%G in (%NONALBUM_GLOBS%) do (
  echo   git rm --cached %%G
  git rm --cached %%G >>"%LOG%" 2>&1
)

REM Ensure we do NOT accidentally untrack album dirs:
REM (No action here; allowlist is informational.)

echo.
echo --- Update .gitignore to avoid re-adding backups/junk ---
>>"%LOG%" echo Updating .gitignore
(
  echo.
  echo # ---- Auto-ignore non-album material (local only) ----
  echo _NONALBUM_LOCAL_BACKUP/
  echo _QUARANTINE/
  echo Documents/
  echo profiles/
  echo backups/
  echo backup-20250917/
  echo Mike Songs 2025/
  echo quintet*.html
  echo *.sh
) >> ".gitignore"

git add .gitignore >>"%LOG%" 2>&1

echo.
echo --- Review staged changes ---
git status
echo.
>>"%LOG%" echo --- git status (staged) ---
git status >>"%LOG%" 2>&1
>>"%LOG%" echo.

REM Commit if something is staged
git diff --cached --quiet
if not errorlevel 1 (
  echo Nothing staged. Exiting.
  >>"%LOG%" echo Nothing staged. Exiting.
  popd >nul
  pause
  exit /b 0
)

echo --- Commit + push cleanup ---
git commit -m "Cleanup: remove non-album content from ECM-Orbit-Album-2027 (kept locally in backup)" >>"%LOG%" 2>&1
git push origin %BRANCH% >>"%LOG%" 2>&1

echo.
echo ============================================================
echo DONE.
echo - GitHub repo cleaned (non-album untracked + removed from current main)
echo - Local copies kept
echo - Local backup folder: %EXPORT%
echo IMPORTANT: history still contains old files until we run a purge.
echo ============================================================
echo.
popd >nul
pause
endlocal
