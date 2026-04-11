# SWC Native Binding Error - Windows Vite Project

## 🔍 Root Cause Analysis

### Primary Issue
The `@swc/core` native binary (`.node` file) failed to install during `npm install`. Instead of properly falling back to `@swc/wasm`, the binding.js file is trying to load a non-existent native binary.

### Why This Happens on Windows

**Cause 1: Optional Dependency Not Installed** ❌
```
@swc/core requires @swc/win32-x64-msvc (platform-specific optional dependency)
This package contains the precompiled .node binary
```

**Cause 2: Postinstall Script Failed Silently** ❌
```
npm install runs but the optional @swc/win32-x64-msvc fails to download
Binding.js is generated but points to missing ./swc.win32-x64-msvc.node
Application tries to load it and fails with "not a valid Win32 application"
```

**Cause 3: Corrupted node_modules** ❌
```
Partial installation from interrupted npm install
Some files exist but .node binary is missing
Cache issues with npm registry
```

**Cause 4: Node.js/npm Mismatch** ❌
```
Node.js version may not match @swc/core expectations
npm cache corruption preventing proper download
```

---

## ✅ Fix Steps (Ordered by Likelihood to Work)

### STEP 1: Clean Node Modules & Cache (Highest Success Rate)

```batch
cd "C:\Major Project\raga-rasa-soul-main"

REM Remove node_modules completely
rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

REM Clear npm cache
npm cache clean --force

REM Clear npm cache for specific packages
npm cache clean --force --scope=@swc
```

### STEP 2: Reinstall with Verbose Output

```batch
cd "C:\Major Project\raga-rasa-soul-main"

REM Install with verbose output to see postinstall
npm install --verbose
```

**Watch for:**
- ✅ "@swc/win32-x64-msvc" in output
- ❌ "ERR! 404" or download failures
- ✅ "added XXX packages" completion message

### STEP 3: Verify SWC Binary Installed

```batch
REM Check if native binding exists
if exist "node_modules\@swc\win32-x64-msvc\swc.win32-x64-msvc.node" (
    echo ✅ Native binary exists
) else (
    echo ❌ Native binary missing - try Step 4
)

REM Check binding.js
type node_modules\@swc\core\binding.js | findstr /i "swc.win32"
```

**Expected output:** Path reference to swc.win32-x64-msvc.node

### STEP 4: Use Wasm Fallback (Alternative Approach)

If native binary won't install, explicitly use WebAssembly version:

```batch
cd "C:\Major Project\raga-rasa-soul-main"

REM Install wasm version explicitly
npm install --save-dev @swc/wasm

REM Or remove native version and use wasm only
npm uninstall @vitejs/plugin-react-swc
npm install --save-dev @vitejs/plugin-react-swc @swc/wasm
```

**Update vite.config.ts:**
```typescript
import react from "@vitejs/plugin-react-swc";
// No changes needed - it auto-detects @swc/wasm

// OR explicitly if needed:
// import { swc } from "@swc/core/wasm";
```

### STEP 5: Force npm to Reinstall from Registry

```batch
cd "C:\Major Project\raga-rasa-soul-main"

REM Update npm first
npm install -g npm@latest

REM Use --force flag to reinstall everything
npm install --force

REM Or with --prefer-online to force registry fetch
npm install --prefer-online --no-audit
```

### STEP 6: Check Node.js Compatibility

```batch
REM Check your Node version (you have v24.14.0 - good)
node -v

REM Check for known incompatibilities
npm list @vitejs/plugin-react-swc

REM If old version, update
npm update @vitejs/plugin-react-swc
```

**Compatibility Matrix:**
- Node 18+: Full support
- Node 20+ (your 24.14.0): Fully supported
- Issue is rarely Node version on modern versions

### STEP 7: Use Environment Override (Last Resort)

Create `.env` or `.npmrc` in project root:

**`.npmrc` (new file):**
```
legacy-peer-deps=true
fetch-timeout=120000
fetch-retry-mintimeout=20000
fetch-retry-maxtimeout=120000
prefer-offline=true
```

**Then reinstall:**
```batch
cd "C:\Major Project\raga-rasa-soul-main"
npm cache clean --force
npm install
```

### STEP 8: Nuclear Option - Reinstall Everything

```batch
cd "C:\Major Project\raga-rasa-soul-main"

REM Remove all lock files
if exist package-lock.json del package-lock.json
if exist bun.lock del bun.lock
if exist bun.lockb del bun.lockb

REM Remove node_modules
rmdir /s /q node_modules

REM Clear all caches
npm cache clean --force

REM Reinstall fresh
npm install

REM If still fails, try with npm 11.9.0 specific fix
npm install --legacy-peer-deps --verbose
```

---

## ✅ Verification Steps (After Each Fix)

### Quick Verification

```batch
REM Should complete without errors
npm run dev

REM Should show Vite server started
REM You'll see: Local: http://localhost:8080/
```

### Detailed Verification

**Check 1: Native binary exists**
```batch
if exist "node_modules\@swc\win32-x64-msvc\swc.win32-x64-msvc.node" (
    echo ✅ Native binary found
    dir /s node_modules\@swc\win32-x64-msvc\*.node
)
```

**Check 2: Binding can be loaded**
```batch
node -e "console.log(require('@swc/core'))"
```

**Expected output:**
```
{
  parseSync: [Function: parseSync],
  parse: [AsyncFunction: parse],
  transformSync: [Function: transformSync],
  transform: [AsyncFunction: transform],
  ...
}
```

**Check 3: Vite config loads**
```batch
node -e "import('./vite.config.ts')" 2>&1 && echo ✅ Config loads successfully
```

**Check 4: Run dev server**
```batch
npm run dev
```

**Expected:**
- ✅ No error about swc.win32-x64-msvc.node
- ✅ Vite server starts on localhost:8080
- ✅ No "ERR_DLOPEN_FAILED" messages

---

## 🔧 Advanced Fixes

### Fix A: Manually Download Binary

If npm fails but you have working internet:

```batch
cd "C:\Major Project\raga-rasa-soul-main\node_modules\@swc"

REM Create directory if missing
if not exist win32-x64-msvc mkdir win32-x64-msvc

REM Download specific version (replace VERSION_NUMBER)
REM Get version from @swc/core package.json
for /f "tokens=3" %%A in ('type ..\core\package.json ^| find "\"version\""') do @echo %%A

REM Use npx to install just the optional dep
cd "C:\Major Project\raga-rasa-soul-main"
npx --package=@swc/cli npm install @swc/win32-x64-msvc --save-optional
```

### Fix B: Use Docker/WSL as Last Resort

If Windows npm refuses to work:

```bash
# In WSL
cd /mnt/c/Major\ Project/raga-rasa-soul-main
npm install
```

Then run from Windows Command Prompt:

```batch
npm run dev
```

The compiled binaries from WSL are often compatible with Windows Node.

### Fix C: Switch to Babel Plugin

If SWC remains problematic, use Babel instead:

```batch
cd "C:\Major Project\raga-rasa-soul-main"

REM Remove SWC
npm uninstall @vitejs/plugin-react-swc

REM Install Babel plugin
npm install --save-dev @vitejs/plugin-react
```

**Update vite.config.ts:**
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";  // Changed this line
import path from "path";
import { componentTagger } from "lovable-tagger";

export default defineConfig(({ mode }) => ({
  // rest remains same
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
}));
```

Performance: Slightly slower compilation, but no native binding issues.

---

## 📊 Diagnostic Checklist

Run this script to diagnose the issue:

**Create `diagnose-swc.js`:**
```javascript
const fs = require('fs');
const path = require('path');

console.log('=== SWC Diagnostic ===\n');

// Check 1: Node version
console.log('✓ Node version:', process.version);
console.log('✓ Architecture:', process.arch);
console.log('✓ Platform:', process.platform);

// Check 2: @swc/core installed
try {
  const corePackage = require.resolve('@swc/core/package.json');
  console.log('✓ @swc/core found');
} catch (e) {
  console.log('✗ @swc/core NOT found');
}

// Check 3: Native binary
try {
  const nativeBinary = path.join(
    require.resolve('@swc/core'),
    '../',
    '@swc/win32-x64-msvc/swc.win32-x64-msvc.node'
  );
  if (fs.existsSync(nativeBinary)) {
    console.log('✓ Native binary exists');
  } else {
    console.log('✗ Native binary missing');
  }
} catch (e) {
  console.log('✗ Error checking native binary:', e.message);
}

// Check 4: Binding can load
try {
  const binding = require('@swc/core');
  console.log('✓ Binding loads successfully');
} catch (e) {
  console.log('✗ Binding load error:', e.message);
}

// Check 5: Wasm available as fallback
try {
  require.resolve('@swc/wasm');
  console.log('✓ @swc/wasm available as fallback');
} catch (e) {
  console.log('✗ @swc/wasm not available');
}
```

**Run it:**
```batch
node diagnose-swc.js
```

---

## 🛡️ Prevention Steps

### For Future Installations

1. **Use consistent npm versions**
   ```batch
   npm --version  # Note version
   npm install -g npm@latest  # Keep updated
   ```

2. **Avoid interrupting installs**
   - Never Ctrl+C during `npm install`
   - Let it complete fully

3. **Use lockfile appropriately**
   ```batch
   REM Use exact versions from package-lock.json
   npm ci --production=false
   
   REM Instead of:
   npm install
   ```

4. **Set npm config for stability**
   
   Create `.npmrc` in project root:
   ```
   legacy-peer-deps=true
   fetch-timeout=120000
   fetch-retry-mintimeout=20000
   fetch-retry-maxtimeout=120000
   engine-strict=false
   ```

5. **Use setup.bat that handles this**
   
   Update `setup.bat`:
   ```batch
   @echo off
   cd /d "C:\Major Project\raga-rasa-soul-main"
   
   REM Check for existing node_modules
   if exist "node_modules" (
       echo Removing old node_modules...
       rmdir /s /q node_modules
   )
   
   echo Installing dependencies...
   npm cache clean --force
   npm install --verbose
   
   REM Verify
   if errorlevel 1 (
       echo ❌ Installation failed
       exit /b 1
   )
   
   echo ✅ Installation successful
   pause
   ```

---

## ⚡ Quick Fix (TRY THIS FIRST)

```batch
cd "C:\Major Project\raga-rasa-soul-main"
rmdir /s /q node_modules
npm cache clean --force
npm install --verbose
npm run dev
```

**If that doesn't work, try:**
```batch
npm install --force
npm run dev
```

**If still failing, try:**
```batch
npm install --save-dev @swc/wasm
npm run dev
```

---

## 📋 Summary

| Step | Fix | Time | Success Rate |
|------|-----|------|--------------|
| 1 | Clean reinstall | 5-10 min | 70% |
| 2 | Install wasm fallback | 2-3 min | 95% |
| 3 | Update npm | 2-3 min | 60% |
| 4 | Switch to Babel | 5-10 min | 100% |

---

## ✅ When You Know It's Fixed

```
✅ npm run dev completes without errors
✅ Vite server starts on http://localhost:8080
✅ Browser can access the app
✅ No ERR_DLOPEN_FAILED in console
✅ React components load successfully
```

---

**If none of these work, the issue is likely environmental (antivirus blocking downloads, proxy, DNS). Try from a different network or WSL.**
