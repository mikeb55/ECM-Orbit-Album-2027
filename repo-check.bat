@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM ECM Orbit Album - Repo Check (stays open + writes log)
REM ============================================================

set "REPO=C:\Users\mike\Documents\Cursor AI Projects\ECM-Orbit-Album-2027"
set "LOG=%~dp0ECM_Orbit_Repo_Check.log"

REM Start fresh log
> "%LOG%" echo ECM ORBIT ALBUM 2027 - GIT REPO CHECK LOG
>>"%LOG%" echo Started: %DATE% %TIME%
>>"%LOG%" echo Repo: "%REPO%"
>>"%LOG%" echo ============================================================

echo ============================================================
echo ECM ORBIT ALBUM 2027 - GIT REPO CHECK
echo Repo: "%REPO%"
echo Log:  "%LOG%"
echo ============================================================
echo.

if not exist "%REPO%\" (
  echo ERROR: Repo folder does not exist:
  echo   "%REPO%"
  echo.
  >>"%LOG%" echo ERROR: Repo folder does not exist: "%REPO%"
  goto :END
)

pushd "%REPO%" >nul

where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: git is not on PATH.
  echo Install Git for Windows or fix PATH.
  echo.
  >>"%LOG%" echo ERROR: git not found on PATH.
  popd >nul
  goto :END
)

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo ERROR: This folder is not a git repository (no .git).
  echo   "%REPO%"
  echo.
  >>"%LOG%" echo ERROR: Not a git repository: "%REPO%"
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
  echo Expected:
  echo   %REPO%
  echo Actual:
  echo   !TOP!
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

echo Last commit:
git --no-pager log -1 --oneline
echo.
>>"%LOG%" echo Last commit:
git --no-pager log -1 --oneline >>"%LOG%" 2>&1
>>"%LOG%" echo.

echo Unpushed commits (if upstream set):
git rev-list --count --left-right @{upstream}...HEAD 2>nul
if errorlevel 1 (
  echo   (No upstream configured for this branch.)
  >>"%LOG%" echo (No upstream configured for this branch.)
) else (
  >>"%LOG%" echo Unpushed commits count above.
)
echo.
>>"%LOG%" echo.

popd >nul

:END
>>"%LOG%" echo Finished: %DATE% %TIME%
>>"%LOG%" echo ============================================================

echo ============================================================
echo Done. Press any key to close.
echo (If it still closes, open the log file next to this .bat)
echo ============================================================
pause >nul
endlocal
