#!/usr/bin/env python3
"""
Add Download Button - Adds auto-download functionality to existing HTML files
"""

import sys
import shutil
from pathlib import Path
import time
import webbrowser


def add_download_button_to_html(html_file, variant_id):
    """Add download button and auto-download to existing HTML file"""
    
    # Read original HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Create unique filename
    timestamp = int(time.time())
    unique_filename = f"infographic_{variant_id}_{timestamp}.svg"
    
    # Simple download script that works with existing HTML
    download_script = f'''
    
    <!-- Download Button and Auto-Download Script -->
    <script>
    function downloadSVG() {{
        console.log('Starting SVG download...');
        
        // Wait for SVG to be rendered
        const svg = document.querySelector('svg');
        if (!svg) {{
            console.log('SVG not found, retrying...');
            setTimeout(downloadSVG, 500);
            return;
        }}
        
        console.log('SVG found, preparing download...');
        
        // Get SVG content
        let svgContent = svg.outerHTML;
        
        // Add XML declaration if not present
        if (!svgContent.startsWith('<?xml')) {{
            svgContent = '<?xml version="1.0" encoding="UTF-8"?>\\n' + svgContent;
        }}
        
        // Ensure proper namespace
        if (!svgContent.includes('xmlns="http://www.w3.org/2000/svg"')) {{
            svgContent = svgContent.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
        }}
        
        // Create and trigger download
        const blob = new Blob([svgContent], {{type: 'image/svg+xml'}});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = '{unique_filename}';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('Download triggered: {unique_filename}');
        
        // Update button text to show success
        const button = document.getElementById('download-btn');
        if (button) {{
            button.textContent = '✓ Downloaded!';
            button.style.backgroundColor = '#28a745';
        }}
    }}
    
    // Auto-download when page is ready
    function autoDownload() {{
        // Wait for D3.js to render
        setTimeout(function() {{
            const svg = document.querySelector('svg');
            if (svg && svg.children.length > 0) {{
                console.log('Auto-downloading SVG...');
                downloadSVG();
            }} else {{
                console.log('SVG not ready, retrying...');
                setTimeout(autoDownload, 1000);
            }}
        }}, 2000);
    }}
    
    // Start auto-download process
    setTimeout(autoDownload, 1000);
    </script>
    
    <!-- Download Button -->
    <button id="download-btn" onclick="downloadSVG()" style="
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        padding: 12px 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    " onmouseover="this.style.backgroundColor='#0056b3'" onmouseout="this.style.backgroundColor='#007bff'">
        📥 Download SVG
    </button>
    
    <!-- Variant Info -->
    <div style="
        position: fixed;
        top: 70px;
        right: 20px;
        z-index: 1000;
        padding: 8px 12px;
        background: rgba(0,123,255,0.9);
        color: white;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    ">
        {variant_id}
    </div>
    
    '''
    
    # Add download script before closing body tag
    modified_html = html_content.replace('</body>', download_script + '</body>')
    
    return modified_html, unique_filename


def add_download_and_open(html_file, output_svg):
    """Add download button to HTML file and open in browser"""
    
    html_path = Path(html_file)
    
    # Get variant ID from path
    variant_id = "unknown"
    for part in html_path.parts:
        if 'variant_' in part:
            variant_id = part
            break
    
    print(f"[Download] Adding download button to {variant_id}")
    print(f"[Download] Input: {html_file}")
    print(f"[Download] Output: {output_svg}")
    
    # Add download functionality to HTML
    modified_html, unique_filename = add_download_button_to_html(html_file, variant_id)
    
    # Save temporary HTML file with download button
    temp_html = html_path.parent / f"temp_download_{variant_id}.html"
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(modified_html)
    
    print(f"[Download] Created HTML with download button: {temp_html}")
    
    # Clear old downloads for this variant
    downloads_folder = Path.home() / 'Downloads'
    old_files = list(downloads_folder.glob(f'infographic_{variant_id}_*.svg'))
    for old_file in old_files:
        try:
            old_file.unlink()
            print(f"[Download] Cleaned up old file: {old_file.name}")
        except:
            pass
    
    # Open in browser
    print(f"[Download] Opening browser for {variant_id}...")
    webbrowser.open(f'file://{temp_html.absolute()}')
    
    # Wait for download
    print(f"[Download] Waiting for download of {unique_filename}...")
    
    for i in range(35):
        time.sleep(1)
        
        # Check if file was downloaded
        downloaded_file = downloads_folder / unique_filename
        if downloaded_file.exists():
            print(f"[Download] Download detected after {i+1} seconds!")
            
            # Copy to final location
            shutil.copy2(downloaded_file, output_svg)
            print(f"[Download] Copied to: {output_svg}")
            
            # Clean up
            try:
                downloaded_file.unlink()
                temp_html.unlink()
                print(f"[Download] Cleaned up temporary files")
            except Exception as e:
                print(f"[Download] Cleanup warning: {e}")
            
            return True
        
        # Progress indicator
        if (i + 1) % 5 == 0:
            print(f"[Download] Still waiting... {i+1}/35 seconds")
    
    print(f"[Download] Download failed - file not found: {unique_filename}")
    
    # Clean up temp file
    try:
        temp_html.unlink()
    except:
        pass
    
    return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_download_button.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    
    success = add_download_and_open(html_file, output_svg)
    
    if success:
        print(f"[Download] SUCCESS: {output_svg}")
        sys.exit(0)
    else:
        print(f"[Download] FAILED: {output_svg}")
        sys.exit(1)
