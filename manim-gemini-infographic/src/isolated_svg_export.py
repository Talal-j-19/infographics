#!/usr/bin/env python3
"""
Isolated SVG Export - Prevents cross-contamination between variants
Uses variant-specific temporary directories and unique identifiers
"""

import sys
import subprocess
import shutil
import tempfile
import uuid
from pathlib import Path
import time
import webbrowser


def create_isolated_download_html(html_file, variant_id):
    """Create HTML with variant-specific download functionality"""
    try:
        print(f"[Isolated] Creating variant-specific download for: {variant_id}")
        
        # Read original HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Create unique filename for this variant
        unique_filename = f"infographic_{variant_id}_{int(time.time())}.svg"
        
        # Enhanced download script with variant isolation
        download_script = f'''
        <script>
        const VARIANT_ID = "{variant_id}";
        const UNIQUE_FILENAME = "{unique_filename}";
        
        function downloadSVG() {{
            console.log('Starting SVG download for variant:', VARIANT_ID);
            
            const svg = document.querySelector('svg');
            if (!svg) {{
                console.error('No SVG found');
                alert('No SVG found for variant ' + VARIANT_ID);
                return;
            }}
            
            // Clone SVG to avoid modifying original
            const svgClone = svg.cloneNode(true);
            
            // Extract all CSS styles from style tags
            const styleElements = document.querySelectorAll('style');
            let allStyles = '';
            styleElements.forEach(style => {{
                allStyles += style.textContent + '\\n';
            }});
            
            // Get computed styles for key SVG elements
            const svgElements = svg.querySelectorAll('text, rect, line, path, circle');
            const computedStyles = new Set();
            
            for (let i = 0; i < Math.min(svgElements.length, 50); i++) {{
                const elem = svgElements[i];
                const computed = window.getComputedStyle(elem);
                const styles = [];
                
                // Extract essential visual styles
                if (computed.fill && computed.fill !== 'rgb(0, 0, 0)' && computed.fill !== 'none') {{
                    styles.push(`fill: ${{computed.fill}}`);
                }}
                if (computed.stroke && computed.stroke !== 'none') {{
                    styles.push(`stroke: ${{computed.stroke}}`);
                }}
                if (computed.strokeWidth && computed.strokeWidth !== '0px') {{
                    styles.push(`stroke-width: ${{computed.strokeWidth}}`);
                }}
                if (computed.fontSize) {{
                    styles.push(`font-size: ${{computed.fontSize}}`);
                }}
                if (computed.fontWeight && computed.fontWeight !== 'normal') {{
                    styles.push(`font-weight: ${{computed.fontWeight}}`);
                }}
                if (computed.fontFamily) {{
                    styles.push(`font-family: ${{computed.fontFamily}}`);
                }}
                if (computed.textAnchor && computed.textAnchor !== 'start') {{
                    styles.push(`text-anchor: ${{computed.textAnchor}}`);
                }}
                
                if (styles.length > 0) {{
                    const tagName = elem.tagName.toLowerCase();
                    if (elem.className && elem.className.baseVal) {{
                        computedStyles.add(`.${{elem.className.baseVal}} {{ ${{styles.join('; ')}}; }}`);
                    }} else if (elem.id) {{
                        computedStyles.add(`#${{elem.id}} {{ ${{styles.join('; ')}}; }}`);
                    }} else {{
                        computedStyles.add(`${{tagName}} {{ ${{styles.join('; ')}}; }}`);
                    }}
                }}
            }}
            
            // Combine all styles
            const finalStyles = allStyles + '\\n' + Array.from(computedStyles).join('\\n');
            
            // Create style element for SVG
            if (finalStyles.trim()) {{
                const styleElement = document.createElementNS('http://www.w3.org/2000/svg', 'style');
                styleElement.setAttribute('type', 'text/css');
                styleElement.textContent = finalStyles;
                svgClone.insertBefore(styleElement, svgClone.firstChild);
            }}
            
            // Add XML declaration and namespace
            let svgString = svgClone.outerHTML;
            if (!svgString.includes('xmlns="http://www.w3.org/2000/svg"')) {{
                svgString = svgString.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
            }}
            svgString = '<?xml version="1.0" encoding="UTF-8"?>\\n' + svgString;
            
            // Create and trigger download
            const blob = new Blob([svgString], {{type: 'image/svg+xml'}});
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = UNIQUE_FILENAME;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log('SVG download triggered for variant:', VARIANT_ID, 'filename:', UNIQUE_FILENAME);
            
            // Signal completion
            document.title = 'SVG_DOWNLOAD_COMPLETE_' + VARIANT_ID;
        }}
        
        // Auto-download after rendering
        setTimeout(() => {{
            if (typeof d3 !== 'undefined' && document.querySelector('svg')) {{
                console.log('Auto-triggering download for variant:', VARIANT_ID);
                downloadSVG();
            }} else {{
                console.error('D3 or SVG not ready for variant:', VARIANT_ID);
            }}
        }}, 3000);
        </script>
        <div style="position: fixed; top: 10px; right: 10px; z-index: 1000; background: rgba(0,123,255,0.9); color: white; padding: 10px; border-radius: 5px; font-family: Arial;">
            <div>Variant: {variant_id}</div>
            <button onclick="downloadSVG()" style="margin-top: 5px; padding: 5px 10px; background: white; color: #007bff; border: none; border-radius: 3px; cursor: pointer;">Download SVG</button>
        </div>
        '''
        
        # Insert download script before closing body tag
        modified_html = html_content.replace('</body>', download_script + '</body>')
        
        return modified_html, unique_filename
        
    except Exception as e:
        print(f"[Isolated] Error creating download HTML: {e}")
        return None, None


def isolated_svg_export(html_file, output_svg):
    """
    Export SVG with complete isolation between variants
    """
    try:
        html_path = Path(html_file)
        output_path = Path(output_svg)
        
        # Create unique variant ID from path
        variant_parts = html_path.parts
        variant_id = None
        for part in variant_parts:
            if 'variant_' in part:
                variant_id = part
                break
        
        if not variant_id:
            # Fallback: create ID from filename
            variant_id = f"var_{html_path.stem}_{int(time.time() % 10000)}"
        
        print(f"[Isolated] Starting isolated SVG export for {variant_id}")
        print(f"[Isolated] Input: {html_file}")
        print(f"[Isolated] Output: {output_svg}")
        
        # Create variant-specific HTML with download functionality
        modified_html, unique_filename = create_isolated_download_html(html_file, variant_id)
        if not modified_html:
            return False
        
        # Create temporary file in same directory as original
        temp_html = html_path.parent / f"temp_download_{variant_id}.html"
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(modified_html)
        
        print(f"[Isolated] Created temporary HTML: {temp_html}")
        
        # Clear Downloads folder of old infographic files for this variant
        downloads_folder = Path.home() / 'Downloads'
        old_files = list(downloads_folder.glob(f'infographic_{variant_id}*.svg'))
        for old_file in old_files:
            try:
                old_file.unlink()
                print(f"[Isolated] Cleaned up old file: {old_file.name}")
            except Exception as e:
                print(f"[Isolated] Could not clean {old_file.name}: {e}")
        
        # Open in browser
        print(f"[Isolated] Opening browser for {variant_id}...")
        webbrowser.open(f'file://{temp_html.absolute()}')
        
        # Wait for download with progress indication
        print(f"[Isolated] Waiting for download of {unique_filename}...")
        for i in range(30):
            time.sleep(1)
            
            # Check if file was downloaded
            expected_file = downloads_folder / unique_filename
            if expected_file.exists():
                print(f"[Isolated] Download detected after {i+1} seconds!")
                break
            
            # Progress indicator
            if (i + 1) % 5 == 0:
                print(f"[Isolated] Still waiting... ({i+1}/30 seconds)")
        
        # Check for downloaded file
        downloaded_file = downloads_folder / unique_filename
        if downloaded_file.exists():
            # Copy to final location
            shutil.copy2(downloaded_file, output_svg)
            print(f"[Isolated] Successfully copied: {downloaded_file} -> {output_svg}")
            
            # Clean up
            try:
                downloaded_file.unlink()
                temp_html.unlink()
                print(f"[Isolated] Cleaned up temporary files")
            except Exception as e:
                print(f"[Isolated] Cleanup warning: {e}")
            
            return True
        else:
            print(f"[Isolated] Download failed - file not found: {unique_filename}")
            
            # Clean up temp file
            try:
                temp_html.unlink()
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"[Isolated] Export failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python isolated_svg_export.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    
    success = isolated_svg_export(html_file, output_svg)
    
    if success:
        print(f"[Isolated] SUCCESS: {output_svg}")
        sys.exit(0)
    else:
        print(f"[Isolated] FAILED: Could not export {output_svg}")
        sys.exit(1)
