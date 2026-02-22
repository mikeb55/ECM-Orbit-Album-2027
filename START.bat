 @echo off
setlocal EnableExtensions

REM =========================================================
REM ECM Orbit Album 2027 - Safe Start (NO POWERSHELL)
REM - Switch to home/mike
REM - Fetch + pull fast-forward only (no surprise merges)
REM - Open repo in Cursor
REM - Write START-log.txt on every run
REM =========================================================

set "REPO=%~dp0"
set "BRANCH=home/mike"
set "LOG=%REPO%START-log.txt"

REM --- Start log ---
> "%LOG%" echo ===== START.bat run %DATE% %TIME% =====
>>"%LOG%" echo Repo: "%REPO%"
>>"%LOG%" echo Branch: "%BRANCH%"

echo.
echo ECM Orbit Safe Start
echo Repo: "%REPO%"
echo Log : "%LOG%"
echo.

REM --- cd into repo folder ---
cd /d "%REPO%" 1>>"%LOG%" 2>>&1
if errorlevel 1 (
  echo ERROR: Could not cd into repo folder.
  >>"%LOG%" echo ERROR: Could not cd into repo folder.
  pause
  exit /b 1
)

REM --- Ensure git exists ---
where git 1>>"%LOG%" 2>>&1
if errorlevel 1 (
  echo ERROR: Git not found on PATH.
  echo Install Git or restart terminal/session after install.
  >>"%LOG%" echo ERROR: Git not found on PATH.
  pause
  exit /b 1
)

REM --- Fetch latest ---
echo Running: git fetch origin --prune
>>"%LOG%" echo Running: git fetch origin --prune
git fetch origin --prune 1>>"%LOG%" 2>>&1
if errorlevel 1 (
  echo ERROR: git fetch failed. See START-log.txt
  >>"%LOG%" echo ERROR: git fetch failed.
  pause
  exit /b 1
)

REM --- Switch/create safe machine branch ---
>>"%LOG%" echo Checking local branch "%BRANCH%"...
git show-ref --verify --quiet "refs/heads/%BRANCH%" 1>>"%LOG%" 2>>&1
if errorlevel 1 (
  >>"%LOG%" echo Local branch missing. Checking remote origin/%BRANCH%...
  git show-ref --verify --quiet "refs/remotes/origin/%BRANCH%" 1>>"%LOG%" 2>>&1
  if errorlevel 1 (
    echo Creating %BRANCH% from origin/main...
    >>"%LOG%" echo Creating %BRANCH% from origin/main...
    git switch -c "%BRANCH%" origin/main 1>>"%LOG%" 2>>&1
    if errorlevel 1 (
      echo ERROR: Failed to create %BRANCH% from origin/main. See START-log.txt
      >>"%LOG%" echo ERROR: Failed to create branch from origin/main.
      pause
      exit /b 1
    )

    echo Publishing %BRANCH% to origin...
    >>"%LOG%" echo Publishing %BRANCH% to origin...
    git push -u origin "%BRANCH%" 1>>"%LOG%" 2>>&1
    if errorlevel 1 (
      echo ERROR: Failed to push %BRANCH% to origin. See START-log.txt
      >>"%LOG%" echo ERROR: Failed to push branch.
      pause
      exit /b 1
    )
  ) else (
    echo Creating local %BRANCH% tracking origin/%BRANCH%...
    >>"%LOG%" echo Creating local %BRANCH% tracking origin/%BRANCH%...
    git switch -c "%BRANCH%" "origin/%BRANCH%" 1>>"%LOG%" 2>>&1
    if errorlevel 1 (
      echo ERROR: Failed to track origin/%BRANCH%. See START-log.txt
      >>"%LOG%" echo ERROR: Failed to track remote branch.
      pause
      exit /b 1
    )
  )
) else (
  echo Switching to %BRANCH%...
  >>"%LOG%" echo Switching to %BRANCH%...
  git switch "%BRANCH%" 1>>"%LOG%" 2>>&1
  if errorlevel 1 (
    echo ERROR: Failed to switch to %BRANCH%. See START-log.txt
    >>"%LOG%" echo ERROR: Failed to switch branch.
    pause
    exit /b 1
  )
)

REM --- Pull safely (fast-forward only) ---
git config pull.ff only 1>>"%LOG%" 2>>&1
echo Running: git pull --ff-only
>>"%LOG%" echo Running: git pull --ff-only
git pull --ff-only 1>>"%LOG%" 2>>&1
if errorlevel 1 (
  echo ERROR: Pull blocked (diverged). Fix via GitHub PR (home/mike -> main).
  >>"%LOG%" echo ERROR: Pull blocked (diverged).
  pause
  exit /b 1
)

REM --- Open Cursor ---
where cursor 1>>"%LOG%" 2>>&1
if %ERRORLEVEL%==0 goto OPEN_CURSOR_CMD

if exist "%LOCALAPPDATA%\Programs\cursor\Cursor.exe" goto OPEN_CURSOR_EXE

echo ERROR: Cursor not found. Open the folder manually in Cursor:
echo "%REPO%"
>>"%LOG%" echo ERROR: Cursor not found.
pause
exit /b 1

:OPEN_CURSOR_CMD
echo Opening Cursor...
>>"%LOG%" echo Opening Cursor via PATH command.
start "" cursor .
exit /b 0

:OPEN_CURSOR_EXE
echo Opening Cursor...
>>"%LOG%" echo Opening Cursor via fallback exe.
start "" "%LOCALAPPDATA%\Programs\cursor\Cursor.exe" "%REPO%"
exit /b 0
