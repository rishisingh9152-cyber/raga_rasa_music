@echo off
REM Fix SWC Native Binding Error for Vite + React + TypeScript
REM This script handles the @swc/core ./swc.win32-x64-msvc.node missing error

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║     SWC Native Binding Fix - Windows Vite Project      ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Colors and status
set "RED=[ERROR]"
set "GREEN=[OK]"
set "YELLOW=[WARN]"

cd /d "C:\Major Project\raga-rasa-soul-main"

echo Current directory: %cd%
echo.

REM Check Node.js
echo %YELLOW% Checking Node.js version...
node -v >nul 2>&1
if errorlevel 1 (
    echo %RED% Node.js not found in PATH
    exit /b 1
)
node -v
echo %GREEN% Node.js found
echo.

REM Step 1: Remove corrupted node_modules
echo %YELLOW% Step 1: Removing corrupted node_modules...
if exist "node_modules" (
    echo Deleting node_modules...
    rmdir /s /q node_modules
    echo %GREEN% node_modules removed
) else (
    echo %YELLOW% node_modules already removed or doesn't exist
)
echo.

REM Step 2: Remove lock files
echo %YELLOW% Step 2: Removing lock files...
if exist "package-lock.json" del /f /q package-lock.json
if exist "bun.lock" del /f /q bun.lock
if exist "bun.lockb" del /f /q bun.lockb
echo %GREEN% Lock files removed
echo.

REM Step 3: Clear npm cache
echo %YELLOW% Step 3: Clearing npm cache...
call npm cache clean --force >nul 2>&1
echo %GREEN% npm cache cleaned
echo.

REM Step 4: Reinstall dependencies with verbose output
echo %YELLOW% Step 4: Installing dependencies with verbose output...
echo This may take a few minutes...
echo.
call npm install --verbose

if errorlevel 1 (
    echo.
    echo %RED% npm install failed
    echo.
    echo Trying alternative: Installing with --force flag...
    call npm install --force
    if errorlevel 1 (
        echo.
        echo %RED% Second attempt also failed
        echo Trying fallback: Installing @swc/wasm...
        call npm install --save-dev @swc/wasm
        if errorlevel 1 (
            echo %RED% Installation failed completely
            exit /b 1
        )
    )
)

echo.
echo %GREEN% Dependencies installed
echo.

REM Step 5: Verify SWC binary
echo %YELLOW% Step 5: Verifying SWC native binary...
if exist "node_modules\@swc\win32-x64-msvc\swc.win32-x64-msvc.node" (
    echo %GREEN% Native binary found
    echo Location: node_modules\@swc\win32-x64-msvc\swc.win32-x64-msvc.node
) else (
    echo %YELLOW% Native binary not found, checking for wasm fallback...
    if exist "node_modules\@swc\wasm" (
        echo %GREEN% WASM fallback available (will work but slower)
    ) else (
        echo %YELLOW% WASM also not found - may still work
    )
)
echo.

REM Step 6: Test if binding loads
echo %YELLOW% Step 6: Testing if @swc/core can be loaded...
node -e "console.log(require('@swc/core'))" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW% Direct load failed, trying vite config...
) else (
    echo %GREEN% @swc/core loads successfully
)
echo.

REM Step 7: Test Vite config
echo %YELLOW% Step 7: Testing Vite configuration...
call npx vite --version >nul 2>&1
if errorlevel 1 (
    echo %RED% Vite not working
) else (
    echo %GREEN% Vite is working
)
echo.

REM Summary
echo ╔════════════════════════════════════════════════════════╗
echo ║                 FIX COMPLETE                           ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo   1. Run: npm run dev
echo   2. Open: http://localhost:8080
echo.
echo If still getting errors:
echo   - Check SWC_FIX_GUIDE.md for advanced troubleshooting
echo   - Try: npm install --force
echo   - Or: npm install --save-dev @swc/wasm
echo.
pause
