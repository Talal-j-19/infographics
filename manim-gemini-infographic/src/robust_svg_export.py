#!/usr/bin/env python3
"""
Robust SVG Export - Handles D3.js loading failures and JavaScript execution issues
"""

import sys
import subprocess
import shutil
import tempfile
import uuid
from pathlib import Path
import time
import webbrowser
import requests


def download_d3js_locally():
    """Download D3.js library locally to avoid CDN issues"""
    try:
        d3_path = Path(__file__).parent / 'd3.v7.min.js'
        if d3_path.exists():
            return str(d3_path)
        
        print("[Robust] Downloading D3.js locally...")
        response = requests.get('https://d3js.org/d3.v7.min.js', timeout=10)
        response.raise_for_status()
        
        with open(d3_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"[Robust] D3.js downloaded: {d3_path}")
        return str(d3_path)
        
    except Exception as e:
        print(f"[Robust] Could not download D3.js: {e}")
        return None


def create_robust_download_html(html_file, variant_id):
    """Create HTML with robust download functionality and local D3.js"""
    try:
        print(f"[Robust] Creating robust download for: {variant_id}")
        
        # Read original HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Try to get D3.js locally
        d3_local_path = download_d3js_locally()
        
        # Create unique filename for this variant
        unique_filename = f"infographic_{variant_id}_{int(time.time())}.svg"
        
        # Replace CDN D3.js with local version if available
        if d3_local_path:
            # Read local D3.js content
            with open(d3_local_path, 'r', encoding='utf-8') as f:
                d3_content = f.read()
            
            # Replace CDN script with inline D3.js
            html_content = html_content.replace(
                '<script src="https://d3js.org/d3.v7.min.js"></script>',
                f'<script>\n{d3_content}\n</script>'
            )
            print("[Robust] Replaced CDN D3.js with local version")
        
        # Enhanced download script with better error handling
        download_script = f'''
        <script>
        const VARIANT_ID = "{variant_id}";
        const UNIQUE_FILENAME = "{unique_filename}";
        let downloadAttempted = false;
        
        // Error handling
        window.addEventListener('error', function(e) {{
            console.error('JavaScript error:', e.error);
            document.title = 'ERROR_' + VARIANT_ID + '_' + e.error.message;
        }});
        
        function checkD3AndSVG() {{
            console.log('Checking D3 and SVG availability...');
            
            if (typeof d3 === 'undefined') {{
                console.error('D3.js not loaded');
                document.title = 'ERROR_' + VARIANT_ID + '_D3_NOT_LOADED';
                return false;
            }}
            
            const svg = document.querySelector('svg');
            if (!svg) {{
                console.error('SVG not found');
                document.title = 'ERROR_' + VARIANT_ID + '_SVG_NOT_FOUND';
                return false;
            }}
            
            console.log('D3 and SVG are available');
            return true;
        }}
        
        function downloadSVG() {{
            if (downloadAttempted) {{
                console.log('Download already attempted');
                return;
            }}
            downloadAttempted = true;
            
            console.log('Starting SVG download for variant:', VARIANT_ID);
            
            if (!checkD3AndSVG()) {{
                return;
            }}
            
            try {{
                const svg = document.querySelector('svg');
                
                // Clone SVG to avoid modifying original
                const svgClone = svg.cloneNode(true);
                
                // Extract all CSS styles from style tags
                const styleElements = document.querySelectorAll('style');
                let allStyles = '';
                styleElements.forEach(style => {{
                    allStyles += style.textContent + '\\n';
                }});
                
                // Get computed styles for key SVG elements
                const svgElements = svg.querySelectorAll('text, rect, line, path, circle, g');
                const computedStyles = new Set();
                
                for (let i = 0; i < Math.min(svgElements.length, 100); i++) {{
                    const elem = svgElements[i];
                    try {{
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
                    }} catch (styleError) {{
                        console.warn('Error getting styles for element:', styleError);
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
                
            }} catch (error) {{
                console.error('Download error:', error);
                document.title = 'ERROR_' + VARIANT_ID + '_DOWNLOAD_FAILED_' + error.message;
            }}
        }}
        
        // Multiple trigger mechanisms
        function attemptDownload() {{
            if (checkD3AndSVG()) {{
                downloadSVG();
            }} else {{
                console.log('D3 or SVG not ready, will retry...');
            }}
        }}
        
        // Try multiple times with different delays
        setTimeout(attemptDownload, 1000);  // 1 second
        setTimeout(attemptDownload, 3000);  // 3 seconds
        setTimeout(attemptDownload, 5000);  // 5 seconds
        
        // Also try when DOM is fully loaded
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', function() {{
                setTimeout(attemptDownload, 1000);
            }});
        }}
        
        // Manual trigger button
        function createDownloadButton() {{
            const button = document.createElement('button');
            button.textContent = 'Download SVG';
            button.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                z-index: 1000;
                padding: 10px 15px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            `;
            button.onclick = downloadSVG;
            document.body.appendChild(button);
            
            // Add variant info
            const info = document.createElement('div');
            info.textContent = 'Variant: ' + VARIANT_ID;
            info.style.cssText = `
                position: fixed;
                top: 50px;
                right: 10px;
                z-index: 1000;
                padding: 5px 10px;
                background: rgba(0,123,255,0.9);
                color: white;
                border-radius: 3px;
                font-size: 12px;
            `;
            document.body.appendChild(info);
            
            console.log('Download button created for variant:', VARIANT_ID);
        }}
        
        // Create button immediately
        createDownloadButton();
        
        </script>
        '''
        
        # Insert download script before closing body tag
        modified_html = html_content.replace('</body>', download_script + '</body>')
        
        return modified_html, unique_filename
        
    except Exception as e:
        print(f"[Robust] Error creating download HTML: {e}")
        return None, None


def robust_svg_export(html_file, output_svg):
    """
    Export SVG with robust error handling and local D3.js
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
            variant_id = f"var_{html_path.stem}_{int(time.time() % 10000)}"
        
        print(f"[Robust] Starting robust SVG export for {variant_id}")
        
        # Create robust HTML with download functionality
        modified_html, unique_filename = create_robust_download_html(html_file, variant_id)
        if not modified_html:
            return False
        
        # Create temporary file
        temp_html = html_path.parent / f"temp_robust_{variant_id}.html"
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(modified_html)
        
        print(f"[Robust] Created temporary HTML: {temp_html}")
        
        # Clear Downloads folder of old files
        downloads_folder = Path.home() / 'Downloads'
        old_files = list(downloads_folder.glob(f'infographic_{variant_id}*.svg'))
        for old_file in old_files:
            try:
                old_file.unlink()
                print(f"[Robust] Cleaned up old file: {old_file.name}")
            except:
                pass
        
        # Open in browser
        print(f"[Robust] Opening browser for {variant_id}...")
        webbrowser.open(f'file://{temp_html.absolute()}')
        
        # Wait for download with detailed monitoring
        print(f"[Robust] Waiting for download of {unique_filename}...")
        for i in range(45):  # Extended wait time
            time.sleep(1)
            
            # Check if file was downloaded
            expected_file = downloads_folder / unique_filename
            if expected_file.exists():
                print(f"[Robust] Download detected after {i+1} seconds!")
                break
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"[Robust] Still waiting... ({i+1}/45 seconds)")
        
        # Check for downloaded file
        downloaded_file = downloads_folder / unique_filename
        if downloaded_file.exists():
            # Copy to final location
            shutil.copy2(downloaded_file, output_svg)
            print(f"[Robust] Successfully copied: {downloaded_file} -> {output_svg}")
            
            # Clean up
            try:
                downloaded_file.unlink()
                temp_html.unlink()
                print(f"[Robust] Cleaned up temporary files")
            except Exception as e:
                print(f"[Robust] Cleanup warning: {e}")
            
            return True
        else:
            print(f"[Robust] Download failed - file not found: {unique_filename}")
            
            # Clean up temp file
            try:
                temp_html.unlink()
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"[Robust] Export failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python robust_svg_export.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    
    success = robust_svg_export(html_file, output_svg)
    
    if success:
        print(f"[Robust] SUCCESS: {output_svg}")
        sys.exit(0)
    else:
        print(f"[Robust] FAILED: Could not export {output_svg}")
        sys.exit(1)
