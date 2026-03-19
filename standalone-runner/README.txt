==========================================================
  Automation Flow Runner - Portable Version
==========================================================

FOR USERS
---------

Simply double-click: run.bat

That's it! No installation, no setup, just run.


FOR DEVELOPERS (Preparing Distribution)
----------------------------------------

Before distributing to users:

1. Run: prepare_portable.bat
   - Downloads Python 3.11.9 (~30MB)
   - Installs all dependencies
   - Creates python/ folder
   - Takes 2-5 minutes

2. Test: run.bat
   - Verify everything works

3. Package: 
   - Zip the entire standalone-runner folder
   - Size will be ~150MB

4. Distribute:
   - Send to users
   - They extract and run.bat - done!


WHAT'S INCLUDED
---------------

run.bat              - Start the automation (users click this)
runner.py            - Automation engine
flow.json            - Your automation flow
assets/              - Image assets
python/              - Portable Python 3.11.9 (created by prepare_portable.bat)
requirements.txt     - Dependencies (already installed in python/)


ADVANTAGES
----------

✓ No Python installation required
✓ No dependency issues
✓ No internet connection needed (after preparation)
✓ Works on any Windows PC
✓ Self-contained (~150MB)
✓ Delete folder = complete uninstall


TROUBLESHOOTING
---------------

Q: run.bat shows "Python not found"
A: Run prepare_portable.bat first to create python/ folder

Q: prepare_portable.bat download fails
A: Check internet connection, or manually download:
   https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip

Q: Can I use on Mac/Linux?
A: This version is Windows-only. For Mac/Linux, install Python 3.8+
   and run: python3 runner.py


SYSTEM REQUIREMENTS
-------------------

- Windows 10/11 (64-bit)
- ~150MB disk space
- No other requirements!


==========================================================


SYSTEM REQUIREMENTS
-------------------

- Python 3.8 or higher
- Windows 10/11, macOS 10.14+, or Ubuntu 18.04+
- At least 1GB available memory
- Internet connection (first run only)


USAGE INSTRUCTIONS
------------------

1. Place your flow.json file in this folder
2. Place any required images in the assets/ folder
3. Run the startup script for your platform
4. The flow will execute automatically


ASSET PATH HANDLING
--------------------

The runner automatically handles asset paths:
- Place images in assets/ folder
- Reference them by filename in your flow
- Paths are automatically resolved


TROUBLESHOOTING
---------------

Q: "Python not detected"
A: Install Python from https://www.python.org/downloads/

Q: "Dependency installation failed"
A: Try manual installation:
   - Windows: run install_deps.bat
   - Mac/Linux: run install_deps.sh

Q: "flow.json not found"
A: Make sure flow.json is in the same folder as runner.py

Q: "Image not found"
A: Check that images are in the assets/ folder


FEATURES
--------

✓ No server required - standalone execution
✓ Automatic dependency management
✓ Cross-platform support (Windows/Mac/Linux)
✓ Automatic asset path resolution
✓ Full feature support from original tool
✓ Real-time execution logging

NEW IN v2.0:
✓ Multi-scale image matching (auto DPI adaptation)
✓ Intelligent image preprocessing
✓ Works across different DPI settings (100%-200%)
✓ Robust to display color/brightness differences
✓ Enhanced cross-device compatibility


SUPPORTED ACTIONS
-----------------

Recognition:
- Find Image
- Find Text (OCR)
- Find Window
- Check Color

Operations:
- Click / Double Click
- Drag
- Scroll
- Type Text
- Hotkey
- Launch Program
- Activate/Close Window

Logic:
- Wait
- Condition
- End

Data:
- Variables
- Clipboard Copy/Paste
- Message Box
- Log
- Screenshot


ADVANCED USAGE
--------------

For developers:
- runner.py contains all execution logic
- Modify runner.py to add custom actions
- Flow format follows original backend schema


NOTES
-----

- Press Ctrl+C to stop execution at any time
- Logs are displayed in real-time in the console
- Failed dependency installs may require manual intervention
- OCR features require paddleocr (included in requirements)


VERSION INFORMATION
-------------------

Version: 2.0 - Enhanced Cross-Device Compatibility
Last Updated: January 2026
Compatible with: Original automation-tool backend

NEW IN v2.0:
✓ Multi-scale template matching (automatic DPI adaptation)
✓ Image preprocessing for robust recognition
✓ Cross-device compatibility (100%-200% DPI)
✓ Enhanced color/brightness tolerance
✓ Detailed matching logs (scale + confidence)

See UPGRADE_V2.0.md for complete documentation.


SUPPORT
-------

For issues or questions:
1. Check README for common problems
2. Review console logs for error messages
3. Verify all files are in correct locations


==========================================================
