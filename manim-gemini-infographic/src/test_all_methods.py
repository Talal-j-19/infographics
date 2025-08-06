#!/usr/bin/env python3
"""
Test All Methods - Try all implemented SVG export methods one by one
"""

import sys
import time
from pathlib import Path


def test_method_1_improved_download(html_file, output_svg):
    """Test Method 1: Improved Download with D3.js validation"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 1: Improved Download")
    print("="*60)
    print("Description: Waits for D3.js completion, validates SVG content")
    print("Features: Auto-download, content validation, timing control")
    
    try:
        from improved_download import improved_download_svg
        result = improved_download_svg(html_file, output_svg)
        
        if result:
            print("✅ METHOD 1 SUCCESS!")
            return True, "Improved download worked"
        else:
            print("❌ METHOD 1 FAILED!")
            return False, "Improved download timed out"
            
    except Exception as e:
        print(f"❌ METHOD 1 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_2_bulletproof_download(html_file, output_svg):
    """Test Method 2: Bulletproof Download"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 2: Bulletproof Download")
    print("="*60)
    print("Description: Always shows download button, works with any HTML")
    print("Features: Robust HTML handling, fallback SVG, manual backup")
    
    try:
        from bulletproof_download import bulletproof_download_svg
        result = bulletproof_download_svg(html_file, output_svg)
        
        if result:
            print("✅ METHOD 2 SUCCESS!")
            return True, "Bulletproof download worked"
        else:
            print("❌ METHOD 2 FAILED!")
            return False, "Bulletproof download timed out"
            
    except Exception as e:
        print(f"❌ METHOD 2 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_3_simple_auto_download(html_file, output_svg):
    """Test Method 3: Simple Auto Download"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 3: Simple Auto Download")
    print("="*60)
    print("Description: Basic auto-download approach")
    print("Features: Simple timing, basic validation")
    
    try:
        from simple_auto_download import simple_auto_download_svg
        result = simple_auto_download_svg(html_file, output_svg)
        
        if result:
            print("✅ METHOD 3 SUCCESS!")
            return True, "Simple auto download worked"
        else:
            print("❌ METHOD 3 FAILED!")
            return False, "Simple auto download timed out"
            
    except Exception as e:
        print(f"❌ METHOD 3 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_4_robust_chrome_download(html_file, output_svg):
    """Test Method 4: Robust Chrome Download"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 4: Robust Chrome Download")
    print("="*60)
    print("Description: Enhanced Chrome download with local D3.js")
    print("Features: Local D3.js, robust timing, enhanced validation")
    
    try:
        from robust_svg_export import robust_svg_export
        result = robust_svg_export(html_file, output_svg)
        
        if result:
            print("✅ METHOD 4 SUCCESS!")
            return True, "Robust Chrome download worked"
        else:
            print("❌ METHOD 4 FAILED!")
            return False, "Robust Chrome download failed"
            
    except Exception as e:
        print(f"❌ METHOD 4 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_5_puppeteer_export(html_file, output_svg):
    """Test Method 5: Puppeteer Export"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 5: Puppeteer Export")
    print("="*60)
    print("Description: Node.js Puppeteer headless browser")
    print("Features: Headless rendering, programmatic control")
    
    try:
        from puppeteer_svg_export import puppeteer_svg_export
        result = puppeteer_svg_export(html_file, output_svg)
        
        if result:
            print("✅ METHOD 5 SUCCESS!")
            return True, "Puppeteer export worked"
        else:
            print("❌ METHOD 5 FAILED!")
            return False, "Puppeteer export failed"
            
    except Exception as e:
        print(f"❌ METHOD 5 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_6_isolated_export(html_file, output_svg):
    """Test Method 6: Isolated SVG Export"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 6: Isolated SVG Export")
    print("="*60)
    print("Description: Isolated browser instance to prevent conflicts")
    print("Features: Clean environment, conflict prevention")
    
    try:
        from isolated_svg_export import isolated_svg_export
        result = isolated_svg_export(html_file, output_svg)
        
        if result:
            print("✅ METHOD 6 SUCCESS!")
            return True, "Isolated export worked"
        else:
            print("❌ METHOD 6 FAILED!")
            return False, "Isolated export failed"
            
    except Exception as e:
        print(f"❌ METHOD 6 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_7_copy_existing(html_file, output_svg):
    """Test Method 7: Copy Existing SVG"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 7: Copy Existing SVG")
    print("="*60)
    print("Description: Copy from existing SVG file if available")
    print("Features: Fast fallback, no rendering needed")
    
    try:
        # Look for existing SVG in the same directory
        html_path = Path(html_file)
        existing_svg = html_path.parent / "infographic.svg"
        
        if existing_svg.exists():
            import shutil
            shutil.copy2(existing_svg, output_svg)
            print("✅ METHOD 7 SUCCESS!")
            return True, "Copied existing SVG file"
        else:
            print("❌ METHOD 7 FAILED!")
            return False, "No existing SVG file found"
            
    except Exception as e:
        print(f"❌ METHOD 7 ERROR: {e}")
        return False, f"Error: {e}"


def test_all_methods(html_file, output_base="test_method"):
    """Test all methods and report results"""
    
    print("🚀 TESTING ALL SVG EXPORT METHODS")
    print("="*60)
    print(f"Input HTML: {html_file}")
    print(f"Testing {7} different methods...")
    
    methods = [
        ("Method 1: Improved Download", test_method_1_improved_download),
        ("Method 2: Bulletproof Download", test_method_2_bulletproof_download),
        ("Method 3: Simple Auto Download", test_method_3_simple_auto_download),
        ("Method 4: Robust Chrome Download", test_method_4_robust_chrome_download),
        ("Method 5: Puppeteer Export", test_method_5_puppeteer_export),
        ("Method 6: Isolated Export", test_method_6_isolated_export),
        ("Method 7: Copy Existing", test_method_7_copy_existing),
    ]
    
    results = []
    successful_methods = []
    
    for i, (name, test_func) in enumerate(methods, 1):
        output_svg = f"{output_base}_{i}.svg"
        
        print(f"\n⏳ Testing {name}...")
        success, message = test_func(html_file, output_svg)
        
        results.append({
            'method': name,
            'success': success,
            'message': message,
            'output_file': output_svg if success else None
        })
        
        if success:
            successful_methods.append((name, output_svg))
            # Check file size
            try:
                file_size = Path(output_svg).stat().st_size
                print(f"📁 Output file: {output_svg} ({file_size} bytes)")
            except:
                pass
        
        # Small delay between tests
        time.sleep(2)
    
    # Final summary
    print("\n" + "="*60)
    print("📊 FINAL RESULTS SUMMARY")
    print("="*60)
    
    for result in results:
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"{status}: {result['method']}")
        print(f"    {result['message']}")
        if result['output_file']:
            print(f"    File: {result['output_file']}")
        print()
    
    print(f"🎯 SUCCESSFUL METHODS: {len(successful_methods)}/{len(methods)}")
    
    if successful_methods:
        print("\n🏆 WORKING METHODS:")
        for name, output_file in successful_methods:
            print(f"  • {name} → {output_file}")
        
        print(f"\n💡 RECOMMENDATION: Use {successful_methods[0][0]} as primary method")
    else:
        print("\n😞 NO METHODS WORKED - Need to investigate further")
    
    return results, successful_methods


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_all_methods.py <html_file>")
        print("Example: python test_all_methods.py generated/batch_xxx/variant_2/infographic.html")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    if not Path(html_file).exists():
        print(f"Error: HTML file not found: {html_file}")
        sys.exit(1)
    
    results, successful_methods = test_all_methods(html_file)
    
    if successful_methods:
        print(f"\n🎉 SUCCESS! Found {len(successful_methods)} working method(s)")
        sys.exit(0)
    else:
        print(f"\n💥 FAILURE! No methods worked")
        sys.exit(1)
