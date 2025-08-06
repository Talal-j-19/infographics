#!/usr/bin/env python3
"""
Test All Methods Plus Headless - Try all implemented SVG export methods including new headless
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


def test_method_3_robust_chrome_download(html_file, output_svg):
    """Test Method 3: Robust Chrome Download"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 3: Robust Chrome Download")
    print("="*60)
    print("Description: Enhanced Chrome download with local D3.js")
    print("Features: Local D3.js, robust timing, enhanced validation")
    
    try:
        from robust_svg_export import robust_svg_export
        result = robust_svg_export(html_file, output_svg)
        
        if result:
            print("✅ METHOD 3 SUCCESS!")
            return True, "Robust Chrome download worked"
        else:
            print("❌ METHOD 3 FAILED!")
            return False, "Robust Chrome download failed"
            
    except Exception as e:
        print(f"❌ METHOD 3 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_4_headless_playwright(html_file, output_svg):
    """Test Method 4: NEW Headless Playwright Export"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 4: 🆕 HEADLESS PLAYWRIGHT")
    print("="*60)
    print("Description: Headless browser automation with Playwright")
    print("Features: No GUI, programmatic control, reliable rendering")
    print("Advantages: No user interaction, works in server environments")
    
    try:
        from headless_svg_export import headless_svg_export
        result = headless_svg_export(html_file, output_svg)
        
        if result:
            print("✅ METHOD 4 SUCCESS!")
            return True, "Headless Playwright export worked"
        else:
            print("❌ METHOD 4 FAILED!")
            return False, "Headless Playwright export failed"
            
    except Exception as e:
        print(f"❌ METHOD 4 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_5_isolated_export(html_file, output_svg):
    """Test Method 5: Isolated SVG Export"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 5: Isolated SVG Export")
    print("="*60)
    print("Description: Isolated browser instance to prevent conflicts")
    print("Features: Clean environment, conflict prevention")
    
    try:
        from isolated_svg_export import isolated_svg_export
        result = isolated_svg_export(html_file, output_svg)
        
        if result:
            print("✅ METHOD 5 SUCCESS!")
            return True, "Isolated export worked"
        else:
            print("❌ METHOD 5 FAILED!")
            return False, "Isolated export failed"
            
    except Exception as e:
        print(f"❌ METHOD 5 ERROR: {e}")
        return False, f"Error: {e}"


def test_method_6_copy_existing(html_file, output_svg):
    """Test Method 6: Copy Existing SVG"""
    print("\n" + "="*60)
    print("🔧 TESTING METHOD 6: Copy Existing SVG")
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
            print("✅ METHOD 6 SUCCESS!")
            return True, "Copied existing SVG file"
        else:
            print("❌ METHOD 6 FAILED!")
            return False, "No existing SVG file found"
            
    except Exception as e:
        print(f"❌ METHOD 6 ERROR: {e}")
        return False, f"Error: {e}"


def analyze_svg_quality(svg_file):
    """Analyze the quality of an SVG file"""
    try:
        if not Path(svg_file).exists():
            return "File not found"
        
        file_size = Path(svg_file).stat().st_size
        
        with open(svg_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic quality checks
        has_xml_declaration = content.startswith('<?xml')
        has_namespace = 'xmlns="http://www.w3.org/2000/svg"' in content
        has_text_elements = '<text' in content
        has_shapes = any(shape in content for shape in ['<circle', '<rect', '<path', '<line'])
        
        text_count = content.count('<text')
        shape_count = sum(content.count(f'<{shape}') for shape in ['circle', 'rect', 'path', 'line', 'g'])
        
        quality_score = 0
        if has_xml_declaration: quality_score += 1
        if has_namespace: quality_score += 1
        if has_text_elements: quality_score += 2
        if has_shapes: quality_score += 2
        if text_count > 5: quality_score += 1
        if shape_count > 10: quality_score += 1
        if file_size > 1000: quality_score += 1
        if file_size > 5000: quality_score += 1
        
        quality_level = "Poor"
        if quality_score >= 8: quality_level = "Excellent"
        elif quality_score >= 6: quality_level = "Good"
        elif quality_score >= 4: quality_level = "Fair"
        
        return f"{quality_level} ({quality_score}/10) - {file_size} bytes, {text_count} text, {shape_count} shapes"
        
    except Exception as e:
        return f"Analysis failed: {e}"


def test_all_methods_plus_headless(html_file, output_base="test_method"):
    """Test all methods including the new headless approach"""
    
    print("🚀 TESTING ALL SVG EXPORT METHODS + NEW HEADLESS")
    print("="*60)
    print(f"Input HTML: {html_file}")
    print(f"Testing {6} different methods...")
    
    methods = [
        ("Method 1: Improved Download", test_method_1_improved_download),
        ("Method 2: Bulletproof Download", test_method_2_bulletproof_download),
        ("Method 3: Robust Chrome Download", test_method_3_robust_chrome_download),
        ("Method 4: 🆕 Headless Playwright", test_method_4_headless_playwright),
        ("Method 5: Isolated Export", test_method_5_isolated_export),
        ("Method 6: Copy Existing", test_method_6_copy_existing),
    ]
    
    results = []
    successful_methods = []
    
    for i, (name, test_func) in enumerate(methods, 1):
        output_svg = f"{output_base}_{i}.svg"
        
        print(f"\n⏳ Testing {name}...")
        success, message = test_func(html_file, output_svg)
        
        # Analyze quality if successful
        quality = ""
        if success and Path(output_svg).exists():
            quality = analyze_svg_quality(output_svg)
        
        results.append({
            'method': name,
            'success': success,
            'message': message,
            'output_file': output_svg if success else None,
            'quality': quality
        })
        
        if success:
            successful_methods.append((name, output_svg, quality))
            print(f"📁 Output: {output_svg}")
            print(f"🎨 Quality: {quality}")
        
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
            print(f"    Quality: {result['quality']}")
        print()
    
    print(f"🎯 SUCCESSFUL METHODS: {len(successful_methods)}/{len(methods)}")
    
    if successful_methods:
        print("\n🏆 WORKING METHODS (by quality):")
        # Sort by quality score
        sorted_methods = sorted(successful_methods, 
                              key=lambda x: int(x[2].split('(')[1].split('/')[0]) if '(' in x[2] else 0, 
                              reverse=True)
        
        for name, output_file, quality in sorted_methods:
            print(f"  • {name}")
            print(f"    Quality: {quality}")
            print(f"    File: {output_file}")
            print()
        
        best_method = sorted_methods[0]
        print(f"🥇 BEST METHOD: {best_method[0]}")
        print(f"   Quality: {best_method[2]}")
        
        if "Headless Playwright" in best_method[0]:
            print("\n🎉 NEW HEADLESS METHOD IS THE WINNER!")
            print("   Advantages: No GUI, server-friendly, reliable")
    else:
        print("\n😞 NO METHODS WORKED - Need to investigate further")
    
    return results, successful_methods


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_all_methods_plus_headless.py <html_file>")
        print("Example: python test_all_methods_plus_headless.py generated/batch_xxx/variant_2/infographic.html")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    if not Path(html_file).exists():
        print(f"Error: HTML file not found: {html_file}")
        sys.exit(1)
    
    results, successful_methods = test_all_methods_plus_headless(html_file)
    
    if successful_methods:
        print(f"\n🎉 SUCCESS! Found {len(successful_methods)} working method(s)")
        sys.exit(0)
    else:
        print(f"\n💥 FAILURE! No methods worked")
        sys.exit(1)
