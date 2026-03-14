# Build Instructions for Best-Option Desktop Application

## Prerequisites

Before building, ensure you have:
- **Node.js** 16+ installed
- **Python** 3.8+ installed
- **npm** or **yarn** package manager
- **Git** (for version control)

## Build Options

### Option 1: Simple Electron Build (Recommended for Development)

This builds only the Electron frontend. Backend runs separately.

#### Steps:

1. **Run the build script:**
   ```bash
   build-simple.bat
   ```

2. **Find the installer:**
   - Location: `frontend\dist-electron\`
   - File: `Best-Option Setup.exe`

3. **Running the app:**
   - Install the app using the setup file
   - Start the backend separately: `python app.py`
   - Launch the Best-Option app

#### Pros:
- Faster build time
- Easier to debug
- Backend can be updated independently

#### Cons:
- Requires Python installed on user's machine
- Two separate processes to manage

---

### Option 2: Full Build with Bundled Backend (Advanced)

This bundles both frontend and backend into a single installer.

#### Steps:

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Run the full build script:**
   ```bash
   build.bat
   ```

3. **Find the outputs:**
   - Backend: `dist\best-option-backend.exe`
   - Frontend installer: `frontend\dist-electron\Best-Option Setup.exe`

4. **Manual packaging:**
   - Copy `best-option-backend.exe` to `frontend\dist-electron\resources\backend\`
   - Rebuild the installer to include the backend

#### Pros:
- Single installer for users
- No Python required on user's machine
- Professional distribution

#### Cons:
- Longer build time
- Larger installer size (~100MB+)
- More complex setup

---

## Manual Build Steps

### Building Frontend Only

```bash
cd frontend
npm install
npm run build
npm run electron:build
```

### Building Backend Only

```bash
pip install pyinstaller
pyinstaller build_backend.spec --clean --noconfirm
```

---

## Build Configuration

### Electron Builder Config

Located in `frontend/package.json`:

```json
"build": {
  "appId": "com.bestoption.app",
  "productName": "Best-Option",
  "directories": {
    "output": "dist-electron"
  },
  "win": {
    "target": ["nsis"],
    "icon": "build/icon.ico"
  }
}
```

### PyInstaller Config

Located in `build_backend.spec`:
- Bundles all Python dependencies
- Includes broker plugins
- Packages database modules
- Creates single executable

---

## Customization

### Change App Icon

1. Create/replace icon file: `frontend/build/icon.ico`
2. Update `package.json` build config
3. Rebuild

### Change App Name

1. Edit `frontend/package.json`:
   ```json
   "productName": "Your-App-Name"
   ```
2. Rebuild

### Add/Remove Files

Edit `build_backend.spec` to include/exclude files:
```python
datas=[
    ('your_folder', 'your_folder'),
    ('your_file.txt', '.'),
]
```

---

## Distribution

### For End Users

**Simple Distribution (Recommended):**
1. Share `Best-Option Setup.exe` from `frontend\dist-electron\`
2. Provide instructions to install Python and run backend
3. Create a startup script for users

**Professional Distribution:**
1. Bundle backend executable with installer
2. Create auto-start scripts
3. Package everything in NSIS installer

### Installer Features

The NSIS installer includes:
- Desktop shortcut creation
- Start menu entry
- Custom installation directory
- Uninstaller
- Auto-update capability (if configured)

---

## Troubleshooting

### Build Fails

**Error: "Python not found"**
- Install Python 3.8+
- Add Python to PATH

**Error: "Node not found"**
- Install Node.js 16+
- Restart terminal

**Error: "npm install failed"**
- Delete `node_modules` folder
- Delete `package-lock.json`
- Run `npm install` again

### Backend Executable Issues

**Error: "Module not found"**
- Add missing module to `hiddenimports` in `build_backend.spec`
- Rebuild

**Error: "File not found"**
- Add missing file to `datas` in `build_backend.spec`
- Rebuild

### Electron Build Issues

**Error: "electron-builder failed"**
- Check `package.json` build config
- Ensure `dist` folder exists
- Run `npm run build` first

---

## Development vs Production

### Development Mode

```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Electron (optional)
cd frontend
npm run electron:dev
```

### Production Build

```bash
# Build everything
build-simple.bat

# Or full build
build.bat
```

---

## File Sizes

Approximate sizes:
- Frontend installer: ~80-100 MB
- Backend executable: ~50-70 MB
- Total distribution: ~150 MB

---

## Next Steps

After building:
1. Test the installer on a clean Windows machine
2. Verify all features work
3. Create user documentation
4. Set up auto-update mechanism (optional)
5. Sign the executable (optional, for Windows SmartScreen)

---

## Support

For build issues:
- Check logs in `frontend\dist-electron\`
- Review PyInstaller warnings
- Test on clean environment
- Contact: support@best-option.com
