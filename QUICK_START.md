# Quick Start Guide - Best-Option Desktop App

## Running Without Building EXE

The easiest way to run the application is without building an EXE:

### Step 1: Start Backend

```bash
python app.py
```

Backend will run on `http://127.0.0.1:8000`

### Step 2: Start Frontend (Development Mode)

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173`

### Step 3: Run as Desktop App (Optional)

```bash
cd frontend
npm run electron
```

This opens the app in an Electron window instead of browser.

---

## Building Portable Version (Without Installer)

Due to Windows permissions issues with electron-builder, here's a simpler approach:

### Method 1: Manual Packaging

1. **Build Frontend:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Package with Electron:**
   ```bash
   npm install -g electron-packager
   electron-packager . Best-Option --platform=win32 --arch=x64 --out=../dist-manual
   ```

3. **Find the app:**
   - Location: `dist-manual/Best-Option-win32-x64/`
   - Run: `Best-Option.exe`

### Method 2: Use Electron Forge (Alternative)

1. **Install Electron Forge:**
   ```bash
   cd frontend
   npm install --save-dev @electron-forge/cli
   npx electron-forge import
   ```

2. **Build:**
   ```bash
   npm run make
   ```

---

## Distribution Package

To create a distributable package:

1. **Build frontend:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Copy files to distribution folder:**
   ```bash
   mkdir dist-package
   xcopy /E /I frontend\dist dist-package\frontend\dist
   copy frontend\main.js dist-package\
   copy frontend\preload.js dist-package\
   copy frontend\package.json dist-package\
   copy app.py dist-package\
   copy requirements.txt dist-package\
   xcopy /E /I broker dist-package\broker
   xcopy /E /I database dist-package\database
   xcopy /E /I routes dist-package\routes
   xcopy /E /I utils dist-package\utils
   ```

3. **Create startup script (`start.bat`):**
   ```batch
   @echo off
   start /B python app.py
   timeout /t 2
   cd frontend
   npm run electron
   ```

4. **Zip the folder** and distribute

---

## Troubleshooting Electron-Builder

The error "Cannot create symbolic link: A required privilege is not held by the client" occurs because:

1. Windows requires admin rights to create symbolic links
2. electron-builder tries to extract winCodeSign with symlinks

### Solutions:

**Option A: Run as Administrator**
- Right-click Command Prompt
- Select "Run as Administrator"
- Run build command

**Option B: Enable Developer Mode (Windows 10/11)**
1. Settings → Update & Security → For Developers
2. Enable "Developer Mode"
3. Restart terminal
4. Try building again

**Option C: Use Alternative Packager**
- Use `electron-packager` instead (shown above)
- Use `electron-forge`
- Use manual packaging

---

## Recommended Approach for Users

**For Development:**
- Run backend: `python app.py`
- Run frontend: `cd frontend && npm run dev`
- Access at: `http://localhost:5173`

**For Distribution:**
1. Use `electron-packager` to create portable app
2. Include Python installer in package
3. Provide startup script
4. Zip and distribute

**For Professional Distribution:**
1. Enable Windows Developer Mode
2. Run Command Prompt as Administrator
3. Build with electron-builder
4. Sign the executable (optional)

---

## Current Status

✅ Backend: Fully functional
✅ Frontend: Fully functional  
✅ Electron Integration: Working
❌ Installer Build: Requires admin/developer mode

The application works perfectly - the only issue is creating the installer package, which is optional for development and testing.

---

## Next Steps

1. Test the app in development mode
2. If you need an EXE, enable Developer Mode or run as admin
3. For quick distribution, use electron-packager
4. For professional distribution, resolve the permissions issue

Need help? Check BUILD_INSTRUCTIONS.md for detailed information.
