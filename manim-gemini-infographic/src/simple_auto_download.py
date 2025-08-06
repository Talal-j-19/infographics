#!/usr/bin/env python3
"""
Simple Auto Download - Just opens HTML in browser and auto-downloads SVG when rendered
No complex error handling, just works
"""

import sys
import shutil
from pathlib import Path
import time
import webbrowser


def create_simple_auto_download_html(html_file, variant_id):
    """Create HTML that auto-downloads SVG when fully rendered - SIMPLE approach"""
    
    # Read original HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Create unique filename
    timestamp = int(time.time())
    unique_filename = f"infographic_{variant_id}_{timestamp}.svg"
    
    # Simple auto-download script - just waits for SVG and downloads
    auto_download_script = f'''
    <script>
    // Simple auto-download when SVG is ready
    function autoDownloadSVG() {{
        // Wait for SVG to exist
        const svg = document.querySelector('svg');
        if (!svg) {{
            setTimeout(autoDownloadSVG, 500);
            return;
        }}
        
        // Wait a bit more for rendering to complete
        setTimeout(function() {{
            // Get SVG content
            const svgContent = svg.outerHTML;
            
            // Add XML declaration
            const fullSVG = '<?xml version="1.0" encoding="UTF-8"?>\\n' + svgContent;
            
            // Create download
            const blob = new Blob([fullSVG], {{type: 'image/svg+xml'}});
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = '{unique_filename}';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log('Auto-downloaded: {unique_filename}');
        }}, 2000);
    }}
    
    // Start auto-download process
    setTimeout(autoDownloadSVG, 1000);
    </script>
    
    <!-- Simple download button as backup -->
    <button onclick="autoDownloadSVG()" style="position: fixed; top: 10px; right: 10px; z-index: 1000; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">
        Download SVG
    </button>
    
    <div style="position: fixed; top: 50px; right: 10px; z-index: 1000; padding: 5px; background: rgba(40,167,69,0.9); color: white; border-radius: 3px; font-size: 12px;">
        {variant_id}
    </div>
    '''
    
    # Add script before closing body tag
    modified_html = html_content.replace('</body>', auto_download_script + '</body>')
    
    return modified_html, unique_filename


def simple_auto_download_svg(html_file, output_svg):
    """Simple approach: open HTML in browser, auto-download SVG"""
    
    html_path = Path(html_file)
    
    # Get variant ID from path
    variant_id = "unknown"
    for part in html_path.parts:
        if 'variant_' in part:
            variant_id = part
            break
    
    print(f"[Simple] Auto-download SVG for {variant_id}")
    print(f"[Simple] Input: {html_file}")
    print(f"[Simple] Output: {output_svg}")
    
    # Create auto-download HTML
    modified_html, unique_filename = create_simple_auto_download_html(html_file, variant_id)
    
    # Save temporary HTML file
    temp_html = html_path.parent / f"temp_auto_{variant_id}.html"
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(modified_html)
    
    print(f"[Simple] Created: {temp_html}")
    
    # Clear old downloads for this variant
    downloads_folder = Path.home() / 'Downloads'
    old_files = list(downloads_folder.glob(f'infographic_{variant_id}_*.svg'))
    for old_file in old_files:
        try:
            old_file.unlink()
        except:
            pass
    
    # Open in browser
    print(f"[Simple] Opening browser...")
    webbrowser.open(f'file://{temp_html.absolute()}')
    
    # Wait for download
    print(f"[Simple] Waiting for auto-download...")
    
    for i in range(30):
        time.sleep(1)
        
        # Check if file was downloaded
        downloaded_file = downloads_folder / unique_filename
        if downloaded_file.exists():
            print(f"[Simple] Download found after {i+1} seconds!")
            
            # Copy to final location
            shutil.copy2(downloaded_file, output_svg)
            print(f"[Simple] Copied to: {output_svg}")
            
            # Clean up
            try:
                downloaded_file.unlink()
                temp_html.unlink()
            except:
                pass
            
            return True
        
        # Progress dots
        if (i + 1) % 5 == 0:
            print(f"[Simple] Still waiting... {i+1}/30")
    
    print(f"[Simple] Auto-download failed - file not found")
    
    # Clean up temp file
    try:
        temp_html.unlink()
    except:
        pass
    
    return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python simple_auto_download.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    
    success = simple_auto_download_svg(html_file, output_svg)
    
    if success:
        print(f"[Simple] SUCCESS: {output_svg}")
        sys.exit(0)
    else:
        print(f"[Simple] FAILED: {output_svg}")
        sys.exit(1)
