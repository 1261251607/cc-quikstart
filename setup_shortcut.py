"""Create a desktop shortcut for cc-cat with the cat icon."""
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.environ["USERPROFILE"], "Desktop")
LNK_PATH = os.path.join(DESKTOP, "cc-cat.lnk")
PYTHONW = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")

# Fallback: search PATH for real pythonw.exe (skip 0-byte Windows App Execution Aliases)
if not os.path.isfile(PYTHONW) or os.path.getsize(PYTHONW) == 0:
    import shutil
    for cmd in ("pythonw", "pythonw.exe"):
        p = shutil.which(cmd)
        if p and os.path.isfile(p) and os.path.getsize(p) > 0:
            PYTHONW = p
            break

if not os.path.isfile(PYTHONW) or os.path.getsize(PYTHONW) == 0:
    print("ERROR: Cannot find a real pythonw.exe. Install Python from python.org.")
    sys.exit(1)

ps = f'''
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut("{LNK_PATH}")
$lnk.TargetPath = "{PYTHONW}"
$lnk.Arguments = '"{os.path.join(SCRIPT_DIR, "cc_cat.py")}"'
$lnk.WorkingDirectory = "{SCRIPT_DIR}"
$lnk.IconLocation = "{os.path.join(SCRIPT_DIR, "cat.ico")},0"
$lnk.WindowStyle = 7
$lnk.Save()
'''

print(f"Target: {PYTHONW}")
print(f"Script: {os.path.join(SCRIPT_DIR, 'cc_cat.py')}")
result = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
if result.returncode == 0:
    print(f"Done! Shortcut created on your desktop: {LNK_PATH}")
else:
    print(f"ERROR: {result.stderr.decode()}")
    sys.exit(1)
