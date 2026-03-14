"""
Build script for Best-Option Desktop Application
Creates executable for Windows, macOS, and Linux
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ Error: Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result

def clean_build_dirs():
    """Clean previous build directories"""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = [
        'dist',
        'build',
        'frontend/dist',
        'frontend/dist-electron',
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"   Removed: {dir_path}")

def install_dependencies():
    """Install required build dependencies"""
    print("\n📦 Installing build dependencies...")
    
    # Install PyInstaller for backend
    run_command("pip install pyinstaller")
    
    # Install frontend dependencies
    run_command("npm install", cwd="frontend")

def build_backend():
    """Build backend executable using PyInstaller"""
    print("\n🔨 Building backend executable...")
    
    # Check if spec file exists
    if not os.path.exists("build_backend.spec"):
        print("❌ Error: build_backend.spec not found")
        sys.exit(1)
    
    # Build using spec file
    run_command("pyinstaller build_backend.spec --clean")
    
    print("✅ Backend build complete!")

def build_frontend():
    """Build frontend with Vite"""
    print("\n🔨 Building frontend...")
    
    run_command("npm run build", cwd="frontend")
    
    print("✅ Frontend build complete!")

def build_electron():
    """Build Electron desktop app"""
    print("\n🔨 Building Electron desktop app...")
    
    run_command("npm run electron:build", cwd="frontend")
    
    print("✅ Electron build complete!")

def create_portable_package():
    """Create portable package with backend and frontend"""
    print("\n📦 Creating portable package...")
    
    # Create package directory
    package_dir = Path("dist/best-option-portable")
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy backend
    backend_src = Path("dist/best-option-backend")
    if backend_src.exists():
        shutil.copytree(backend_src, package_dir / "backend", dirs_exist_ok=True)
        print("   ✓ Backend copied")
    
    # Copy frontend build
    frontend_src = Path("frontend/dist")
    if frontend_src.exists():
        shutil.copytree(frontend_src, package_dir / "frontend", dirs_exist_ok=True)
        print("   ✓ Frontend copied")
    
    # Create startup script for Windows
    startup_script = package_dir / "start.bat"
    with open(startup_script, 'w') as f:
        f.write('@echo off\n')
        f.write('echo Starting Best-Option Application...\n')
        f.write('start "" "backend\\best-option-backend.exe"\n')
        f.write('timeout /t 3 /nobreak > nul\n')
        f.write('start "" "http://localhost:8000"\n')
        f.write('echo Application started!\n')
        f.write('echo Backend: http://127.0.0.1:8000\n')
        f.write('echo.\n')
        f.write('pause\n')
    print("   ✓ Startup script created")
    
    # Create README
    readme = package_dir / "README.txt"
    with open(readme, 'w') as f:
        f.write("Best-Option Desktop Application\n")
        f.write("=" * 50 + "\n\n")
        f.write("To start the application:\n")
        f.write("1. Double-click 'start.bat'\n")
        f.write("2. The backend will start on http://127.0.0.1:8000\n")
        f.write("3. Your browser will open automatically\n\n")
        f.write("To stop the application:\n")
        f.write("- Close the command window\n\n")
        f.write("For support: https://github.com/RahulEdward/starterkit\n")
    print("   ✓ README created")
    
    print(f"\n✅ Portable package created at: {package_dir}")

def main():
    """Main build process"""
    print("\n" + "="*60)
    print("Best-Option Desktop Application - Build Script")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found. Run this script from the project root.")
        sys.exit(1)
    
    try:
        # Step 1: Clean previous builds
        clean_build_dirs()
        
        # Step 2: Install dependencies
        install_dependencies()
        
        # Step 3: Build backend
        build_backend()
        
        # Step 4: Build frontend
        build_frontend()
        
        # Step 5: Build Electron app (optional)
        print("\n❓ Build Electron desktop app? (y/n): ", end="")
        choice = input().lower()
        if choice == 'y':
            build_electron()
        
        # Step 6: Create portable package
        create_portable_package()
        
        print("\n" + "="*60)
        print("✅ BUILD COMPLETE!")
        print("="*60)
        print("\nBuild artifacts:")
        print("  - Backend executable: dist/best-option-backend/")
        print("  - Frontend build: frontend/dist/")
        print("  - Electron app: frontend/dist-electron/")
        print("  - Portable package: dist/best-option-portable/")
        print("\nTo run the portable version:")
        print("  cd dist/best-option-portable")
        print("  start.bat")
        print("\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
