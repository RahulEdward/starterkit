# Building Best-Option Desktop Application

This guide explains how to build the Best-Option application into standalone executables.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Git (optional)

## Build Methods

### Method 1: Automated Build (Windows)

The easiest way to build on Windows:

```bash
build.bat
```

This will:
1. Install PyInstaller
2. Build backend executable
3. Install frontend dependencies
4. Build frontend with Vite
5. Build Electron desktop app

### Method 2: Manual Build

#### Step 1: Install Build Dependencies

```bash
# Install PyInstaller for backend
pip install pyinstaller

# Install frontend dependencies
cd frontend
npm install
cd ..
```

#### Step 2: Build Backend

```bash
# Build backend executable
pyinstaller build_backend.spec --clean
```

Output: `dist/best-option-backend/best-option-backend.exe`

#### Step 3: Build Frontend

```bash
cd frontend

# Build frontend static files
npm run build

# Build Electron desktop app
npm run electron:build

cd ..
```

Outputs:
- Frontend: `frontend/dist/`
- Electron: `frontend/dist-electron/`

### Method 3: Python Build Script

```bash
python build.py
```

This interactive script will guide you through the build process.

## Build Outputs

After building, you'll have:

### 1. Backend Executable
- **Location**: `dist/best-option-backend/`
- **File**: `best-option-backend.exe` (Windows)
- **Usage**: Run directly, starts FastAPI server on port 8000

### 2. Frontend Build
- **Location**: `frontend/dist/`
- **Type**: Static HTML/CSS/JS files
- **Usage**: Serve with any web server or open index.html

### 3. Electron Desktop App
- **Location**: `frontend/dist-electron/`
- **File**: `Best-Option Setup.exe` (Windows installer)
- **Type**: Standalone desktop application
- **Usage**: Install and run like any desktop app

## Running the Built Application

### Option 1: Run Backend + Open Browser

```bash
# Start backend
cd dist/best-option-backend
best-option-backend.exe

# Open browser to http://localhost:8000
```

### Option 2: Run Electron App

```bash
# Install the Electron app
cd frontend/dist-electron
"Best-Option Setup.exe"

# Or run portable version
cd frontend/dist-electron/win-unpacked
Best-Option.exe
```

## Distribution

### For End Users

Distribute one of these:

1. **Electron Installer** (Recommended)
   - File: `frontend/dist-electron/Best-Option Setup.exe`
   - Size: ~150-200 MB
   - Includes everything (backend + frontend)
   - Easy installation

2. **Portable Package**
   - Create a folder with:
     - `dist/best-option-backend/` (backend)
     - `frontend/dist/` (frontend)
     - `start.bat` (startup script)
   - Zip and distribute
   - No installation required

3. **Backend Only**
   - File: `dist/best-option-backend/best-option-backend.exe`
   - Users need a web browser
   - Smaller size (~50-80 MB)

## Troubleshooting

### PyInstaller Issues

If PyInstaller fails:

```bash
# Clean previous builds
rmdir /s /q build dist

# Rebuild
pyinstaller build_backend.spec --clean --noconfirm
```

### Missing Dependencies

If the executable fails to run:

```bash
# Check for missing modules
pyinstaller --hidden-import=module_name build_backend.spec
```

### Electron Build Issues

If Electron build fails:

```bash
cd frontend

# Clean node_modules
rmdir /s /q node_modules
npm install

# Clean build cache
rmdir /s /q dist dist-electron

# Rebuild
npm run build
npm run electron:build
```

### Large File Size

To reduce executable size:

1. Use UPX compression (already enabled in spec file)
2. Exclude unnecessary dependencies
3. Use `--onefile` mode (slower startup)

## Platform-Specific Builds

### Windows
- Default build creates `.exe` files
- NSIS installer for Electron app
- Tested on Windows 10/11

### macOS
- Requires macOS to build
- Creates `.dmg` installer
- Code signing required for distribution

### Linux
- Creates AppImage
- Works on most distributions
- May need additional dependencies

## Advanced Configuration

### Custom Icon

1. Place icon files in `frontend/build/`:
   - `icon.ico` (Windows)
   - `icon.icns` (macOS)
   - `icon.png` (Linux)

2. Rebuild Electron app

### Backend Port

To change backend port, edit `app.py`:

```python
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)  # Change port here
```

### Environment Variables

Create `.env` file in the same directory as the executable:

```env
API_KEY_PEPPER=your_pepper_here
DATABASE_URL=sqlite:///./best_option.db
```

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/build.yml`:

```yaml
name: Build Application

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: build.bat
      - uses: actions/upload-artifact@v3
        with:
          name: best-option-windows
          path: |
            dist/
            frontend/dist-electron/
```

## Support

For build issues:
- GitHub Issues: https://github.com/RahulEdward/starterkit/issues
- Check logs in `build/` directory
- Verify all dependencies are installed

## License

MIT License - See LICENSE file for details
