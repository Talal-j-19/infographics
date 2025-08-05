#!/usr/bin/env python3
"""
Bulletproof Download - Always shows download button, works even if D3.js fails
"""

import sys
import shutil
from pathlib import Path
import time
import webbrowser


def create_bulletproof_download_html(html_file, variant_id):
    """Create HTML that ALWAYS shows download button, even if D3.js fails"""
    
    # Read original HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Create unique filename
    timestamp = int(time.time())
    unique_filename = f"infographic_{variant_id}_{timestamp}.svg"
    
    # Bulletproof download script - shows button immediately, no dependencies
    bulletproof_script = f'''
    
    <!-- BULLETPROOF DOWNLOAD BUTTON - Always appears -->
    <div id="download-controls" style="
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 9999;
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 2px solid #007bff;
    ">
        <div style="font-weight: bold; margin-bottom: 10px; color: #333;">
            {variant_id}
        </div>
        
        <button id="download-btn" onclick="downloadSVG()" style="
            width: 100%;
            padding: 12px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 8px;
        ">
            📥 Download SVG
        </button>
        
        <div id="status" style="font-size: 12px; color: #666; text-align: center;">
            Ready to download
        </div>
    </div>
    
    <script>
    // Bulletproof download function - works regardless of D3.js status
    function downloadSVG() {{
        const statusDiv = document.getElementById('status');
        const button = document.getElementById('download-btn');
        
        try {{
            statusDiv.textContent = 'Looking for SVG...';
            button.style.backgroundColor = '#ffc107';
            
            // Try to find SVG element
            const svg = document.querySelector('svg');
            
            if (!svg) {{
                statusDiv.textContent = 'No SVG found - check console';
                button.style.backgroundColor = '#dc3545';
                console.error('No SVG element found on page');
                
                // Create a fallback SVG
                const fallbackSVG = createFallbackSVG();
                downloadContent(fallbackSVG, '{unique_filename}');
                return;
            }}
            
            statusDiv.textContent = 'Preparing download...';
            
            // Get SVG content
            let svgContent = svg.outerHTML;
            
            // Add XML declaration
            if (!svgContent.startsWith('<?xml')) {{
                svgContent = '<?xml version="1.0" encoding="UTF-8"?>\\n' + svgContent;
            }}
            
            // Ensure namespace
            if (!svgContent.includes('xmlns="http://www.w3.org/2000/svg"')) {{
                svgContent = svgContent.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
            }}
            
            // Download the SVG
            downloadContent(svgContent, '{unique_filename}');
            
            statusDiv.textContent = '✓ Downloaded!';
            button.style.backgroundColor = '#28a745';
            button.textContent = '✓ Downloaded!';
            
        }} catch (error) {{
            console.error('Download error:', error);
            statusDiv.textContent = 'Error: ' + error.message;
            button.style.backgroundColor = '#dc3545';
            
            // Try fallback download
            const fallbackSVG = createFallbackSVG();
            downloadContent(fallbackSVG, '{unique_filename}');
        }}
    }}
    
    function downloadContent(content, filename) {{
        const blob = new Blob([content], {{type: 'image/svg+xml'}});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('Download triggered:', filename);
    }}
    
    function createFallbackSVG() {{
        return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
    <rect width="800" height="600" fill="#f8f9fa"/>
    <text x="400" y="100" text-anchor="middle" font-size="24" font-weight="bold" fill="#333">
        {variant_id} Infographic
    </text>
    <text x="400" y="300" text-anchor="middle" font-size="16" fill="#666">
        SVG could not be extracted from D3.js
    </text>
    <text x="400" y="350" text-anchor="middle" font-size="14" fill="#999">
        Please check the HTML file for the interactive version
    </text>
</svg>`;
    }}
    
    // Auto-download after a delay (optional)
    setTimeout(function() {{
        const statusDiv = document.getElementById('status');
        if (statusDiv && statusDiv.textContent === 'Ready to download') {{
            statusDiv.textContent = 'Auto-downloading in 3 seconds...';
            setTimeout(function() {{
                if (statusDiv.textContent.includes('Auto-downloading')) {{
                    downloadSVG();
                }}
            }}, 3000);
        }}
    }}, 2000);
    
    // Show that the script loaded
    console.log('Bulletproof download script loaded for {variant_id}');
    </script>
    
    '''
    
    # Handle different HTML structures
    if '</body>' in html_content:
        # Normal HTML structure
        modified_html = html_content.replace('</body>', bulletproof_script + '</body>')
    elif '</script>' in html_content:
        # HTML with script but no body tag - add after last script
        last_script_pos = html_content.rfind('</script>')
        if last_script_pos != -1:
            insert_pos = last_script_pos + len('</script>')
            modified_html = html_content[:insert_pos] + bulletproof_script + html_content[insert_pos:]
        else:
            modified_html = html_content + bulletproof_script
    else:
        # Just append at the end
        modified_html = html_content + bulletproof_script

    return modified_html, unique_filename


def bulletproof_download_svg(html_file, output_svg):
    """Bulletproof approach: always shows download button"""
    
    html_path = Path(html_file)
    
    # Get variant ID from path
    variant_id = "unknown"
    for part in html_path.parts:
        if 'variant_' in part:
            variant_id = part
            break
    
    print(f"[Bulletproof] Creating bulletproof download for {variant_id}")
    print(f"[Bulletproof] Input: {html_file}")
    print(f"[Bulletproof] Output: {output_svg}")
    
    # Create bulletproof HTML
    modified_html, unique_filename = create_bulletproof_download_html(html_file, variant_id)
    
    # Save temporary HTML file
    temp_html = html_path.parent / f"temp_bulletproof_{variant_id}.html"
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(modified_html)
    
    print(f"[Bulletproof] Created: {temp_html}")
    
    # Clear old downloads
    downloads_folder = Path.home() / 'Downloads'
    old_files = list(downloads_folder.glob(f'infographic_{variant_id}_*.svg'))
    for old_file in old_files:
        try:
            old_file.unlink()
        except:
            pass
    
    # Open in browser
    print(f"[Bulletproof] Opening browser...")
    print(f"[Bulletproof] You should see a download button in the top-right corner")
    print(f"[Bulletproof] The button will auto-download after 5 seconds")
    webbrowser.open(f'file://{temp_html.absolute()}')
    
    # Wait for download
    print(f"[Bulletproof] Waiting for download...")
    
    for i in range(40):
        time.sleep(1)
        
        # Check if file was downloaded
        downloaded_file = downloads_folder / unique_filename
        if downloaded_file.exists():
            print(f"[Bulletproof] Download found after {i+1} seconds!")
            
            # Copy to final location
            shutil.copy2(downloaded_file, output_svg)
            print(f"[Bulletproof] Success: {output_svg}")
            
            # Clean up
            try:
                downloaded_file.unlink()
                temp_html.unlink()
            except:
                pass
            
            return True
        
        # Progress
        if (i + 1) % 10 == 0:
            print(f"[Bulletproof] Still waiting... {i+1}/40 seconds")
    
    print(f"[Bulletproof] Download timeout - check if button appeared")
    
    # Don't clean up temp file so user can try manually
    print(f"[Bulletproof] Temp file kept for manual download: {temp_html}")
    
    return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bulletproof_download.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    
    success = bulletproof_download_svg(html_file, output_svg)
    
    if success:
        print(f"[Bulletproof] SUCCESS: {output_svg}")
        sys.exit(0)
    else:
        print(f"[Bulletproof] TIMEOUT: Check browser for download button")
        sys.exit(1)
