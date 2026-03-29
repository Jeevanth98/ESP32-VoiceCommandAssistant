"""
Telegram Launch Diagnostic
===========================
Diagnoses why "open telegram" opens Documents folder instead of Telegram app.

Run: python diagnose_telegram.py
"""

import subprocess
import os
import re
from commands.open_app import _resolve_app, extract_app_name, APP_REGISTRY

def check_telegram_installation():
    """Check where Telegram is installed and how."""
    print("="*70)
    print("Telegram Installation Diagnostic")
    print("="*70)
    print()
    
    # Check 1: Is Telegram in the registry?
    print("1. Checking APP_REGISTRY")
    print("-" * 60)
    if "telegram" in APP_REGISTRY:
        cmd, friendly = APP_REGISTRY["telegram"]
        print(f"✅ Found in registry:")
        print(f"   Key: telegram")
        print(f"   Command: {cmd}")
        print(f"   Friendly name: {friendly}")
    else:
        print("❌ NOT found in APP_REGISTRY")
    print()
    
    # Check 2: Test the resolution
    print("2. Testing app resolution")
    print("-" * 60)
    result = _resolve_app("telegram")
    if result:
        cmd, friendly = result
        print(f"✅ Resolution successful:")
        print(f"   Command: {cmd}")
        print(f"   Name: {friendly}")
    else:
        print("❌ Resolution failed - would fall back to file_search")
    print()
    
    # Check 3: Test the current UWP path
    print("3. Testing registered UWP path")
    print("-" * 60)
    current_uwp = "explorer.exe shell:AppsFolder\\TelegramMessenger.TelegramDesktop_t4vj0pshhgkwm!App"
    print(f"Command: {current_uwp}")
    print()
    print("Attempting to launch... (will close automatically if successful)")
    try:
        subprocess.Popen(current_uwp, shell=True, 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Launch command executed")
        print("   Did Telegram open? (Check your taskbar)")
    except Exception as e:
        print(f"❌ Launch failed: {e}")
    print()
    
    # Check 4: Find Telegram installations
    print("4. Searching for Telegram installations")
    print("-" * 60)
    
    # Common installation locations
    search_paths = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
        os.path.join(os.environ.get('APPDATA', ''), 'Telegram Desktop'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Telegram Desktop'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Telegram Desktop'),
    ]
    
    telegram_exes = []
    
    for path in search_paths:
        if os.path.exists(path):
            print(f"Scanning: {path}")
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower() == "telegram.exe":
                        full_path = os.path.join(root, file)
                        telegram_exes.append(full_path)
                        print(f"  ✅ Found: {full_path}")
                # Don't go too deep
                if root.count(os.sep) - path.count(os.sep) > 2:
                    break
    
    if not telegram_exes:
        print("❌ No Telegram.exe found in common locations")
    print()
    
    # Check 5: List UWP Telegram packages
    print("5. Checking UWP/Store installations")
    print("-" * 60)
    print("Querying Windows Store packages... (may take a few seconds)")
    try:
        result = subprocess.run(
            ["powershell", "-Command", 
             "Get-AppxPackage | Where-Object {$_.Name -like '*Telegram*'} | Select-Object Name, PackageFamilyName, InstallLocation"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Found Telegram UWP packages:")
            print(result.stdout)
            
            # Try to extract PackageFamilyName
            lines = result.stdout.split('\n')
            for line in lines:
                if 'PackageFamilyName' in line or '_' in line:
                    print(f"\n💡 If you see a PackageFamilyName above, use it like:")
                    print(f"   explorer.exe shell:AppsFolder\\<PackageFamilyName>!App")
                    break
        else:
            print("❌ No Telegram UWP packages found")
            print("   You likely have the desktop version installed")
    except Exception as e:
        print(f"⚠️  Could not query UWP packages: {e}")
    print()
    
    # Check 6: Test if "start telegram" works
    print("6. Testing 'start telegram' command")
    print("-" * 60)
    print("Attempting: start telegram")
    try:
        subprocess.Popen("start telegram", shell=True, 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Command executed")
        print("   Did Telegram open? (Check your taskbar)")
    except Exception as e:
        print(f"❌ Failed: {e}")
    print()
    
    # Recommendations
    print("="*70)
    print("Recommendations")
    print("="*70)
    print()
    
    if telegram_exes:
        print("✅ Found desktop Telegram installation(s):")
        for exe in telegram_exes:
            print(f"   {exe}")
        print()
        print("📝 Recommended fix in open_app.py (line 32):")
        print("   Change from:")
        print('     "telegram": ("explorer.exe shell:AppsFolder\\...", "Telegram"),')
        print("   To:")
        print(f'     "telegram": ("{telegram_exes[0]}", "Telegram"),')
        print()
        print("   OR simply:")
        print('     "telegram": ("start telegram", "Telegram"),')
        print()
    else:
        print("⚠️  Could not locate Telegram installation")
        print()
        print("Options:")
        print("  1. Install Telegram from:")
        print("     - Microsoft Store (UWP version)")
        print("     - https://desktop.telegram.org (Desktop version)")
        print()
        print("  2. If already installed, manually find Telegram.exe and update open_app.py")
        print()
    
    # Check why file_search might be opening Documents
    print("="*70)
    print("Why Documents folder might open")
    print("="*70)
    print()
    print("If Telegram is not found in APP_REGISTRY, the code falls back to file_search.")
    print("file_search might be finding a folder/file named 'telegram' or similar.")
    print()
    print("To verify:")
    print("  1. Check if you have a folder/file named 'telegram' in Documents")
    print("  2. Run: python main.py")
    print("  3. Try: open telegram")
    print("  4. Watch the debug output for [OPEN-APP] messages")
    print()


if __name__ == "__main__":
    try:
        check_telegram_installation()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
