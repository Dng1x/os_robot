#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable Python Environment Preparation Script
Downloads and configures a portable Python environment for distribution
"""

import os
import sys
import urllib.request
import zipfile
import subprocess
import shutil
from pathlib import Path

PYTHON_VERSION = "3.11.9"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
PYTHON_DIR = Path("python")

def print_step(step, total, message):
    """Print progress message"""
    print(f"\n[{step}/{total}] {message}")
    print("=" * 60)

def download_file(url, dest):
    """Download file with progress"""
    print(f"Downloading from: {url}")
    print("Please wait...")
    
    def reporthook(count, block_size, total_size):
        if total_size > 0:
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\rProgress: {percent}%")
            sys.stdout.flush()
    
    urllib.request.urlretrieve(url, dest, reporthook)
    print("\n")

def main():
    auto_mode = "--auto" in sys.argv or "-y" in sys.argv
    
    print("""
╔════════════════════════════════════════════════════════════╗
║  Portable Python Environment Preparation                   ║
╚════════════════════════════════════════════════════════════╝

This script will download and configure a portable Python
environment for distribution.

After completion, you can package the entire folder and
distribute it to users (no Python installation needed).

Download size: ~30MB
Final size: ~150MB
""")
    
    if not auto_mode:
        input("Press Enter to continue...")
    
    # Check if python folder exists
    if PYTHON_DIR.exists():
        print(f"\n[!] Warning: {PYTHON_DIR} folder already exists.")
        if auto_mode:
            choice = 'y'
        else:
            choice = input("Do you want to recreate it? (y/n): ").lower()
        
        if choice == 'y':
            print(f"Removing existing {PYTHON_DIR} folder...")
            shutil.rmtree(PYTHON_DIR)
        else:
            print("Skipping download, using existing folder.")
            return 0
    
    try:
        # Step 1: Download Python
        print_step(1, 5, "Downloading Python embeddable package")
        python_zip = "python-embed.zip"
        download_file(PYTHON_URL, python_zip)
        
        # Step 2: Extract Python
        print_step(2, 5, "Extracting Python")
        PYTHON_DIR.mkdir(exist_ok=True)
        with zipfile.ZipFile(python_zip, 'r') as zip_ref:
            zip_ref.extractall(PYTHON_DIR)
        os.remove(python_zip)
        print("✓ Extraction complete")
        
        # Step 3: Configure Python for pip
        print_step(3, 5, "Configuring Python for pip")
        pth_file = PYTHON_DIR / f"python{PYTHON_VERSION.replace('.', '')[:3]}._pth"
        
        if pth_file.exists():
            content = pth_file.read_text()
            content = content.replace("#import site", "import site")
            pth_file.write_text(content)
            print("✓ Configuration complete")
        else:
            print(f"[!] Warning: Could not find {pth_file}")
        
        # Step 4: Install pip
        print_step(4, 5, "Installing pip")
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        get_pip_file = PYTHON_DIR / "get-pip.py"
        
        print("Downloading get-pip.py...")
        urllib.request.urlretrieve(get_pip_url, get_pip_file)
        
        python_exe = PYTHON_DIR / "python.exe"
        print("Installing pip...")
        subprocess.run([str(python_exe), str(get_pip_file), "--quiet"], check=True)
        get_pip_file.unlink()
        print("✓ Pip installed")
        
        # Step 5: Install dependencies
        print_step(5, 5, "Installing dependencies")
        requirements_file = Path("requirements.txt")
        
        if not requirements_file.exists():
            print("[!] Warning: requirements.txt not found")
            print("Skipping dependency installation")
        else:
            print("Installing dependencies from requirements.txt...")
            print("This may take a few minutes...\n")
            
            result = subprocess.run(
                [str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=False
            )
            
            if result.returncode == 0:
                print("\n✓ Dependencies installed successfully")
            else:
                print("\n[!] Some dependencies failed to install")
                print("You may need to install them manually")
                return 1
        
        # Success
        print("\n" + "=" * 60)
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  Preparation Complete!                                     ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"""
✓ Portable Python environment ready in {PYTHON_DIR}/ folder

Next steps:
  1. Test: run.bat (or python runner.py)
  2. Package: zip the entire standalone-runner folder
  3. Distribute: send to users (~150MB)

Users can extract and run immediately - no installation needed!
""")
        return 0
        
    except urllib.error.URLError as e:
        print(f"\n[ERROR] Download failed: {e}")
        print("\nPossible causes:")
        print("  - No internet connection")
        print("  - Firewall blocking download")
        print("  - Proxy settings")
        print("\nYou can manually download from:")
        print(f"  {PYTHON_URL}")
        return 1
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    if "--auto" not in sys.argv:
        input("\nPress Enter to exit...")
    sys.exit(exit_code)
