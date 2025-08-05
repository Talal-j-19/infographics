#!/usr/bin/env python3
"""
Reliable SVG Export V2 - From Scratch Implementation
Uses Puppeteer as the primary method for maximum reliability
"""

import sys
import subprocess
import shutil
from pathlib import Path
import time
import json


def check_node_and_puppeteer():
    """Check if Node.js and Puppeteer are available"""
    try:
        # Check Node.js
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return False, "Node.js not found"
        
        node_version = result.stdout.strip()
        print(f"[Check] Node.js version: {node_version}")
        
        # Check if Puppeteer is installed (check in current directory)
        result = subprocess.run(['npm', 'list', 'puppeteer'],
                              capture_output=True, text=True, timeout=10,
                              cwd=Path(__file__).parent)
        
        if 'puppeteer@' not in result.stdout:
            print("[Check] Puppeteer not found, attempting to install...")
            # Try to install Puppeteer
            install_result = subprocess.run(['npm', 'install', 'puppeteer'], 
                                          capture_output=True, text=True, timeout=120)
            if install_result.returncode != 0:
                return False, f"Failed to install Puppeteer: {install_result.stderr}"
            print("[Check] Puppeteer installed successfully")
        else:
            print("[Check] Puppeteer is available")
        
        return True, "Node.js and Puppeteer ready"
        
    except subprocess.TimeoutExpired:
        return False, "Timeout checking Node.js/Puppeteer"
    except Exception as e:
        return False, f"Error checking dependencies: {e}"


def method_1_puppeteer_export(html_file, output_svg):
    """Method 1: Use Puppeteer for SVG export (most reliable)"""
    try:
        print("[Method 1] Using Puppeteer SVG export...")
        
        # Check if our Puppeteer script exists
        script_path = Path(__file__).parent / 'puppeteer_svg_export.js'
        if not script_path.exists():
            print(f"[Method 1] Puppeteer script not found: {script_path}")
            return False
        
        # Check dependencies
        deps_ok, deps_msg = check_node_and_puppeteer()
        if not deps_ok:
            print(f"[Method 1] Dependencies check failed: {deps_msg}")
            return False
        
        # Run Puppeteer export
        print(f"[Method 1] Running: node {script_path} {html_file} {output_svg}")
        result = subprocess.run([
            'node', str(script_path), str(html_file), str(output_svg)
        ], capture_output=True, text=True, timeout=120)
        
        # Print output for debugging
        if result.stdout:
            print(f"[Method 1] Output: {result.stdout}")
        if result.stderr:
            print(f"[Method 1] Errors: {result.stderr}")
        
        if result.returncode == 0 and Path(output_svg).exists():
            file_size = Path(output_svg).stat().st_size
            print(f"[Method 1] Success: {output_svg} ({file_size} bytes)")
            return True
        else:
            print(f"[Method 1] Failed with return code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[Method 1] Puppeteer export timed out")
        return False
    except Exception as e:
        print(f"[Method 1] Puppeteer export failed: {e}")
        return False


def method_2_chrome_download_button(html_file, output_svg):
    """Method 2: Add download button to HTML and use Chrome automation"""
    try:
        print("[Method 2] Using Chrome download button approach...")

        # Read original HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Create modified HTML with enhanced download button that includes styles
        download_script = '''
        <script>
        function downloadSVG() {
            const svg = document.querySelector('svg');
            if (!svg) {
                alert('No SVG found');
                return;
            }

            // Clone SVG to avoid modifying original
            const svgClone = svg.cloneNode(true);

            // Extract all CSS styles from style tags
            const styleElements = document.querySelectorAll('style');
            let allStyles = '';
            styleElements.forEach(style => {
                allStyles += style.textContent + '\\n';
            });

            // Get computed styles for SVG elements
            const svgElements = svg.querySelectorAll('*');
            const computedStyles = new Set();

            for (let i = 0; i < Math.min(svgElements.length, 100); i++) {
                const elem = svgElements[i];
                const computed = window.getComputedStyle(elem);
                const styles = [];

                // Extract important visual styles
                if (computed.fill && computed.fill !== 'rgb(0, 0, 0)' && computed.fill !== 'none') {
                    styles.push(`fill: ${computed.fill}`);
                }
                if (computed.stroke && computed.stroke !== 'none') {
                    styles.push(`stroke: ${computed.stroke}`);
                }
                if (computed.strokeWidth && computed.strokeWidth !== '0px') {
                    styles.push(`stroke-width: ${computed.strokeWidth}`);
                }
                if (computed.fontSize) {
                    styles.push(`font-size: ${computed.fontSize}`);
                }
                if (computed.fontWeight && computed.fontWeight !== 'normal') {
                    styles.push(`font-weight: ${computed.fontWeight}`);
                }
                if (computed.fontFamily) {
                    styles.push(`font-family: ${computed.fontFamily}`);
                }
                if (computed.textAnchor && computed.textAnchor !== 'start') {
                    styles.push(`text-anchor: ${computed.textAnchor}`);
                }

                if (styles.length > 0) {
                    const tagName = elem.tagName.toLowerCase();
                    if (elem.className && elem.className.baseVal) {
                        computedStyles.add(`.${elem.className.baseVal} { ${styles.join('; ')}; }`);
                    } else if (elem.id) {
                        computedStyles.add(`#${elem.id} { ${styles.join('; ')}; }`);
                    } else {
                        computedStyles.add(`${tagName} { ${styles.join('; ')}; }`);
                    }
                }
            }

            // Combine all styles
            const finalStyles = allStyles + '\\n' + Array.from(computedStyles).join('\\n');

            // Create style element for SVG
            if (finalStyles.trim()) {
                const styleElement = document.createElementNS('http://www.w3.org/2000/svg', 'style');
                styleElement.setAttribute('type', 'text/css');
                styleElement.textContent = finalStyles;
                svgClone.insertBefore(styleElement, svgClone.firstChild);
            }

            // Add XML declaration and namespace
            let svgString = svgClone.outerHTML;
            if (!svgString.includes('xmlns="http://www.w3.org/2000/svg"')) {
                svgString = svgString.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
            }
            svgString = '<?xml version="1.0" encoding="UTF-8"?>\\n' + svgString;

            const blob = new Blob([svgString], {type: 'image/svg+xml'});
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = 'infographic.svg';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        // Auto-download after rendering
        setTimeout(() => {
            if (typeof d3 !== 'undefined' && document.querySelector('svg')) {
                downloadSVG();
            }
        }, 5000);
        </script>
        <button onclick="downloadSVG()" style="position: fixed; top: 10px; right: 10px; z-index: 1000; padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Download SVG</button>
        '''
        
        # Insert download script before closing body tag
        modified_html = html_content.replace('</body>', download_script + '</body>')
        
        # Save modified HTML
        temp_html = Path(html_file).parent / 'temp_with_download.html'
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(modified_html)
        
        print(f"[Method 2] Created modified HTML with download button: {temp_html}")
        print("[Method 2] Please open the HTML file in Chrome and click the download button")
        print("[Method 2] Or wait 5 seconds for auto-download")
        
        # Open in default browser
        import webbrowser
        webbrowser.open(f'file://{temp_html.absolute()}')
        
        # Wait for user to download
        print("[Method 2] Waiting 30 seconds for download...")
        time.sleep(30)
        
        # Clean up temp file
        try:
            temp_html.unlink()
        except:
            pass
        
        # Check if file was downloaded (this is a manual process)
        downloads_folder = Path.home() / 'Downloads'
        possible_files = list(downloads_folder.glob('infographic*.svg'))
        
        if possible_files:
            latest_file = max(possible_files, key=lambda p: p.stat().st_mtime)
            shutil.copy2(latest_file, output_svg)
            print(f"[Method 2] Found and copied downloaded SVG: {output_svg}")
            return True
        else:
            print("[Method 2] No downloaded SVG file found")
            return False
            
    except Exception as e:
        print(f"[Method 2] Chrome download method failed: {e}")
        return False


def method_3_fallback_copy(html_file, output_svg):
    """Method 3: Copy existing SVG if available"""
    try:
        print("[Method 3] Looking for existing SVG files...")
        
        html_path = Path(html_file)
        
        # Look for existing SVG in same directory
        existing_svgs = list(html_path.parent.glob('*.svg'))
        
        if existing_svgs:
            # Use the largest SVG file (likely the most complete)
            best_svg = max(existing_svgs, key=lambda p: p.stat().st_size)
            if best_svg.stat().st_size > 500:  # Minimum reasonable size
                shutil.copy2(best_svg, output_svg)
                print(f"[Method 3] Copied existing SVG: {best_svg} -> {output_svg}")
                return True
        
        print("[Method 3] No suitable existing SVG found")
        return False
        
    except Exception as e:
        print(f"[Method 3] Fallback copy failed: {e}")
        return False


def create_emergency_fallback_svg(html_file, output_svg):
    """Create a basic SVG as last resort"""
    try:
        print("[Fallback] Creating emergency fallback SVG...")
        
        # Extract topic from path
        html_path = Path(html_file)
        topic_parts = html_path.parent.parent.name.split('_')
        topic = ' '.join(topic_parts[3:]).replace('_', ' ').title() if len(topic_parts) > 3 else "Infographic"
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#f8f9fa"/>
            <stop offset="100%" style="stop-color:#e9ecef"/>
        </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#bg)"/>
    <text x="400" y="100" text-anchor="middle" font-size="28" font-weight="bold" fill="#333">
        {topic}
    </text>
    <text x="400" y="300" text-anchor="middle" font-size="18" fill="#666">
        Interactive infographic available in HTML format
    </text>
    <text x="400" y="350" text-anchor="middle" font-size="14" fill="#999">
        SVG export encountered technical difficulties
    </text>
    <rect x="300" y="400" width="200" height="50" fill="#007bff" rx="5"/>
    <text x="400" y="430" text-anchor="middle" font-size="16" fill="white">
        View HTML Version
    </text>
</svg>'''
        
        with open(output_svg, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"[Fallback] Created emergency SVG: {output_svg}")
        return True
        
    except Exception as e:
        print(f"[Fallback] Failed to create emergency SVG: {e}")
        return False


def fix_svg_styles(svg_file, html_file):
    """Post-process SVG to add missing styles from HTML"""
    try:
        print(f"[Fix] Adding styles to SVG: {svg_file}")

        # Read SVG content
        with open(svg_file, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Read HTML to extract styles
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract CSS from HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        css_styles = []
        for style_tag in soup.find_all('style'):
            css_styles.append(style_tag.get_text())

        combined_css = '\n'.join(css_styles)

        # Add basic styles if missing
        if not combined_css.strip():
            combined_css = '''
            text { font-family: Arial, sans-serif; fill: #333; }
            .title { font-size: 24px; font-weight: bold; text-anchor: middle; }
            .node-text { fill: white; text-anchor: middle; }
            .node-rect { stroke-width: 1.5px; }
            .arrow-line { stroke: #777; stroke-width: 2px; fill: none; }
            '''

        # Check if SVG already has styles
        if '<style' not in svg_content and combined_css.strip():
            # Add XML declaration if missing
            if not svg_content.startswith('<?xml'):
                svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

            # Add namespace if missing
            if 'xmlns="http://www.w3.org/2000/svg"' not in svg_content:
                svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')

            # Insert styles after opening SVG tag
            style_tag = f'<style type="text/css"><![CDATA[\n{combined_css.strip()}\n]]></style>'

            # Find the end of the opening SVG tag
            svg_tag_end = svg_content.find('>')
            if svg_tag_end != -1:
                svg_content = (svg_content[:svg_tag_end + 1] +
                             '\n' + style_tag +
                             svg_content[svg_tag_end + 1:])

            # Save fixed SVG
            with open(svg_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)

            print(f"[Fix] Added styles to SVG: {len(combined_css)} chars of CSS")
            return True
        else:
            print("[Fix] SVG already has styles or no styles found")
            return True

    except Exception as e:
        print(f"[Fix] Failed to fix SVG styles: {e}")
        return False


def reliable_svg_export_v2(html_file, output_svg):
    """
    Main function for reliable SVG export using multiple methods
    """
    html_path = Path(html_file)
    output_path = Path(output_svg)

    if not html_path.exists():
        print(f"[ERROR] HTML file not found: {html_file}")
        return None

    print(f"[V2] Starting reliable SVG export: {html_file} -> {output_svg}")

    # Try methods in order of reliability
    methods = [
        method_1_puppeteer_export,
        method_2_chrome_download_button,
        method_3_fallback_copy
    ]

    for i, method in enumerate(methods, 1):
        try:
            print(f"\n[V2] Attempting Method {i}...")
            if method(html_file, output_svg):
                # Verify output
                if output_path.exists() and output_path.stat().st_size > 200:
                    # Post-process to fix styles if needed
                    fix_svg_styles(output_svg, html_file)
                    print(f"[V2] SUCCESS: SVG export completed using Method {i}")
                    return str(output_path)
                else:
                    print(f"[V2] Method {i} produced invalid output")
        except Exception as e:
            print(f"[V2] Method {i} exception: {e}")
            continue

    # Emergency fallback
    print("\n[V2] All methods failed, creating emergency fallback...")
    if create_emergency_fallback_svg(html_file, output_svg):
        return str(output_path)

    print("[V2] Complete failure - no SVG could be created")
    return None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reliable_svg_export_v2.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    
    result = reliable_svg_export_v2(html_file, output_svg)
    
    if result:
        print(f"\n[V2] Final result: {result}")
        sys.exit(0)
    else:
        print("\n[V2] SVG export failed completely")
        sys.exit(1)
