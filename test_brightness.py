"""
Brightness Control Test
========================
Tests different methods of controlling screen brightness on Windows.

Run: python test_brightness.py
"""

import subprocess


def test_screen_brightness_control():
    """Test the screen_brightness_control library."""
    print("Method 1: screen_brightness_control library")
    print("-" * 60)
    try:
        import screen_brightness_control as sbc
        
        # Try to get brightness
        current = sbc.get_brightness()
        if isinstance(current, list):
            print(f"✅ Multiple displays detected: {current}")
            current = current[0] if current else None
        else:
            print(f"✅ Single display brightness: {current}%")
        
        if current is not None:
            print(f"   Current brightness: {current}%")
            return True, current
        else:
            print("❌ Could not read brightness")
            return False, None
            
    except ImportError:
        print("❌ screen_brightness_control not installed")
        print("   Install with: pip install screen-brightness-control")
        return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


def test_wmi_brightness():
    """Test Windows WMI method."""
    print("\nMethod 2: Windows WMI (PowerShell)")
    print("-" * 60)
    try:
        # Get brightness
        cmd_get = 'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"'
        result = subprocess.run(cmd_get, capture_output=True, text=True, shell=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            brightness = int(result.stdout.strip())
            print(f"✅ WMI brightness: {brightness}%")
            return True, brightness
        else:
            print("❌ WMI query failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()[:100]}")
            return False, None
            
    except subprocess.TimeoutExpired:
        print("❌ WMI query timeout (>10 seconds)")
        return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


def test_brightness_set():
    """Test setting brightness."""
    print("\nTesting Brightness Adjustment")
    print("-" * 60)
    
    # First, get current brightness using working method
    sbc_works, sbc_level = test_screen_brightness_control()
    wmi_works, wmi_level = test_wmi_brightness()
    
    if not sbc_works and not wmi_works:
        print("\n❌ Cannot test brightness adjustment - no working method found")
        return False
    
    current = sbc_level if sbc_works else wmi_level
    print(f"\nCurrent brightness: {current}%")
    print(f"Will test by increasing to {min(100, current + 10)}%")
    print("(Don't worry, will restore original value)")
    
    input("\nPress Enter to test brightness adjustment (or Ctrl+C to skip)...")
    
    # Try screen_brightness_control
    if sbc_works:
        try:
            import screen_brightness_control as sbc
            test_value = min(100, current + 10)
            print(f"\nSetting to {test_value}% with screen_brightness_control...")
            sbc.set_brightness(test_value)
            
            import time
            time.sleep(1)
            
            new = sbc.get_brightness()
            if isinstance(new, list):
                new = new[0]
            
            print(f"✅ Set to {new}%")
            
            # Restore
            print(f"Restoring to {current}%...")
            sbc.set_brightness(current)
            print("✅ Restored")
            return True
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # Try WMI
    if wmi_works:
        try:
            test_value = min(100, current + 10)
            print(f"\nSetting to {test_value}% with WMI...")
            cmd = f'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{test_value})"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Command executed")
                
                import time
                time.sleep(1)
                
                # Restore
                print(f"Restoring to {current}%...")
                cmd = f'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{current})"'
                subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
                print("✅ Restored")
                return True
            else:
                print(f"❌ WMI set failed")
                
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return False


def main():
    print("="*70)
    print("Brightness Control Diagnostic")
    print("="*70)
    print("\nTesting different methods to control screen brightness on Windows 11...\n")
    
    sbc_works, sbc_level = test_screen_brightness_control()
    wmi_works, wmi_level = test_wmi_brightness()
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    
    if sbc_works or wmi_works:
        print("\n✅ At least one method works!")
        if sbc_works:
            print(f"   ✓ screen_brightness_control: {sbc_level}%")
        if wmi_works:
            print(f"   ✓ Windows WMI: {wmi_level}%")
        print()
        
        # Test adjustment
        try:
            test_brightness_set()
        except KeyboardInterrupt:
            print("\n\nSkipped adjustment test")
            
    else:
        print("\n❌ No working brightness control method found")
        print()
        print("Possible reasons:")
        print("  1. External monitor without software brightness control")
        print("     → Use monitor hardware buttons instead")
        print()
        print("  2. Laptop with restricted WMI access")
        print("     → Try running as Administrator")
        print()
        print("  3. Brightness control disabled in Windows")
        print("     → Check Windows Settings → System → Display")
        print()
        print("  4. Driver issues")
        print("     → Update display drivers")
        print()
    
    print("="*70)
    print("\nRecommendations")
    print("="*70)
    print()
    
    if sbc_works or wmi_works:
        print("✅ The updated brightness.py should work now!")
        print("   Test with: python main.py")
        print("   Try: brightness up")
    else:
        print("⚠️  Software brightness control is not available on your system.")
        print()
        print("Alternatives:")
        print("  • Use Windows Settings → System → Display → Brightness")
        print("  • Use Windows + A (Quick Settings) → Brightness slider")
        print("  • Use monitor hardware buttons (for external displays)")
        print("  • Use keyboard brightness keys (Fn + brightness keys)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
