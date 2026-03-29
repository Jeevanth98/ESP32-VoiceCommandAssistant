"""
Fix Telegram Launch
===================
Automatically fixes the Telegram launch command in open_app.py
by detecting the correct installation type.

Run: python fix_telegram.py
"""

import subprocess
import os
import re

def find_telegram():
    """Find Telegram installation and return the best launch command."""
    
    print("Searching for Telegram...")
    print()
    
    # Method 1: Check if "start telegram" works (simplest)
    print("Testing: start telegram")
    try:
        # This doesn't actually launch, just checks if the command resolves
        result = subprocess.run(
            ["where", "telegram"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ Found via PATH: {result.stdout.strip()}")
            return ("start telegram", "Telegram")
    except Exception as e:
        print(f"   Not found via PATH")
    
    print()
    
    # Method 2: Search for Telegram.exe in common locations
    print("Searching common installation directories...")
    search_paths = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Telegram Desktop'),
        os.path.join(os.environ.get('APPDATA', ''), 'Telegram Desktop'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Telegram Desktop'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Telegram Desktop'),
    ]
    
    for path in search_paths:
        telegram_exe = os.path.join(path, "Telegram.exe")
        if os.path.isfile(telegram_exe):
            print(f"✅ Found: {telegram_exe}")
            return (f'"{telegram_exe}"', "Telegram")
    
    print("   No Telegram.exe found in common locations")
    print()
    
    # Method 3: Try UWP package query
    print("Checking for UWP/Store installation...")
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-AppxPackage | Where-Object {$_.Name -like '*Telegram*'} | Select-Object PackageFamilyName -First 1 | ForEach-Object {$_.PackageFamilyName}"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            package_family = result.stdout.strip()
            print(f"✅ Found UWP package: {package_family}")
            uwp_cmd = f"explorer.exe shell:AppsFolder\\{package_family}!App"
            return (uwp_cmd, "Telegram")
    except Exception as e:
        print(f"   Could not query UWP packages: {e}")
    
    print()
    print("❌ Could not find Telegram installation")
    return None


def update_open_app_py(launch_cmd, friendly_name):
    """Update the Telegram entry in open_app.py"""
    
    file_path = os.path.join(os.path.dirname(__file__), "commands", "open_app.py")
    
    if not os.path.isfile(file_path):
        print(f"❌ Could not find {file_path}")
        return False
    
    print(f"\nUpdating {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the telegram line
    pattern = r'("telegram":\s+\()([^)]+)(\),\s+"Telegram"\),)'
    
    # New value
    new_value = f'"{launch_cmd}", "{friendly_name}"'
    replacement = f'"telegram":         ({new_value}),'
    
    # Check if pattern exists
    if '"telegram":' not in content:
        print("⚠️  Could not find telegram entry in APP_REGISTRY")
        return False
    
    # Replace
    old_line = re.search(r'"telegram":\s+\([^)]+\),.*?"Telegram"\),', content)
    if old_line:
        old_text = old_line.group(0)
        new_text = replacement
        content = content.replace(old_text, new_text)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Successfully updated open_app.py")
        print()
        print("Changed from:")
        print(f"  {old_text[:80]}...")
        print("To:")
        print(f"  {new_text}")
        return True
    else:
        print("❌ Could not parse telegram entry")
        return False


def main():
    print("="*70)
    print("Telegram Launch Fix")
    print("="*70)
    print()
    
    # Find Telegram
    result = find_telegram()
    
    if not result:
        print()
        print("="*70)
        print("Manual Fix Required")
        print("="*70)
        print()
        print("Please:")
        print("  1. Verify Telegram is installed")
        print("  2. Find Telegram.exe location manually")
        print("  3. Update commands/open_app.py line 32:")
        print('     "telegram": ("<path_to_telegram.exe>", "Telegram"),')
        print()
        print("Common locations:")
        print("  - %LOCALAPPDATA%\\Programs\\Telegram Desktop\\Telegram.exe")
        print("  - %APPDATA%\\Telegram Desktop\\Telegram.exe")
        print("  - C:\\Program Files\\Telegram Desktop\\Telegram.exe")
        return
    
    launch_cmd, friendly_name = result
    
    print()
    print("="*70)
    print("Recommended Fix")
    print("="*70)
    print()
    print(f"Launch command: {launch_cmd}")
    print(f"Friendly name: {friendly_name}")
    print()
    
    # Ask for confirmation
    response = input("Apply this fix to commands/open_app.py? (y/n): ").strip().lower()
    
    if response == 'y':
        if update_open_app_py(launch_cmd, friendly_name):
            print()
            print("="*70)
            print("✅ Fix Applied Successfully!")
            print("="*70)
            print()
            print("Next steps:")
            print("  1. Restart the assistant: python main.py")
            print("  2. Try: open telegram")
            print("  3. Telegram should now launch correctly!")
        else:
            print()
            print("❌ Failed to apply fix. Please update manually.")
    else:
        print()
        print("Fix not applied. You can manually update commands/open_app.py")
        print(f"Change line 32 to:")
        print(f'  "telegram": ({launch_cmd}, "{friendly_name}"),')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
