#!/usr/bin/env python3
"""
Test Headless Only - Test just the new headless Playwright method
"""

import sys
from pathlib import Path


def test_headless_method(html_file, output_svg="test_headless.svg"):
    """Test only the headless Playwright method"""
    
    print("🚀 TESTING HEADLESS PLAYWRIGHT METHOD")
    print("="*50)
    print(f"Input HTML: {html_file}")
    print(f"Output SVG: {output_svg}")
    print()
    
    try:
        from headless_svg_export import headless_svg_export
        
        print("🔧 Starting headless SVG export...")
        result = headless_svg_export(html_file, output_svg)
        
        if result:
            print("\n✅ HEADLESS METHOD SUCCESS!")
            
            # Check file quality
            if Path(output_svg).exists():
                file_size = Path(output_svg).stat().st_size
                print(f"📁 File: {output_svg} ({file_size} bytes)")
                
                # Quick quality check
                with open(output_svg, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                text_count = content.count('<text')
                shape_count = sum(content.count(f'<{shape}') for shape in ['circle', 'rect', 'path', 'line'])
                
                print(f"🎨 Content: {text_count} text elements, {shape_count} shapes")
                
                if file_size > 5000 and text_count > 5:
                    print("🏆 HIGH QUALITY SVG!")
                elif file_size > 1000 and text_count > 0:
                    print("👍 GOOD QUALITY SVG!")
                else:
                    print("⚠️  Basic SVG (may need improvement)")
            
            return True
        else:
            print("\n❌ HEADLESS METHOD FAILED!")
            return False
            
    except Exception as e:
        print(f"\n❌ HEADLESS METHOD ERROR: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_headless_only.py <html_file> [output_svg]")
        print("Example: python test_headless_only.py generated/batch_xxx/variant_2/infographic.html")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2] if len(sys.argv) > 2 else "test_headless.svg"
    
    if not Path(html_file).exists():
        print(f"Error: HTML file not found: {html_file}")
        sys.exit(1)
    
    success = test_headless_method(html_file, output_svg)
    
    if success:
        print(f"\n🎉 SUCCESS! Headless method worked")
        print(f"📄 Check the output: {output_svg}")
        sys.exit(0)
    else:
        print(f"\n💥 FAILURE! Headless method failed")
        sys.exit(1)
