#!/usr/bin/env python3
"""
Improved Download - Waits for D3.js to fully render before auto-download
"""

import sys
import shutil
from pathlib import Path
import time
import webbrowser


def create_improved_download_html(html_file, variant_id):
    """Create HTML with improved timing and validation for auto-download"""
    
    # Read original HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Create unique filename
    timestamp = int(time.time())
    unique_filename = f"infographic_{variant_id}_{timestamp}.svg"
    
    # Improved download script with better timing and validation
    improved_script = f'''
    
    <!-- IMPROVED DOWNLOAD with D3.js render detection -->
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
        min-width: 200px;
    ">
        <div style="font-weight: bold; margin-bottom: 10px; color: #333; text-align: center;">
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
        
        <div id="status" style="font-size: 12px; color: #666; text-align: center; line-height: 1.3;">
            Waiting for D3.js...
        </div>
        
        <div id="countdown" style="font-size: 11px; color: #999; text-align: center; margin-top: 5px;">
            
        </div>
    </div>
    
    <script>
    let renderCheckInterval;
    let countdownInterval;
    let autoDownloadTimeout;
    let downloadAttempted = false;
    
    // Improved SVG validation
    function validateSVG(svg) {{
        if (!svg) return false;
        
        // Check if SVG has actual content (not just empty)
        const children = svg.children;
        if (children.length === 0) return false;
        
        // Check for text elements (most infographics have text)
        const textElements = svg.querySelectorAll('text');
        if (textElements.length === 0) return false;
        
        // Check for meaningful content (not just default/empty text)
        let hasContent = false;
        for (let text of textElements) {{
            if (text.textContent && text.textContent.trim().length > 2) {{
                hasContent = true;
                break;
            }}
        }}
        
        return hasContent;
    }}
    
    // Check if D3.js rendering is complete
    function isRenderingComplete() {{
        // Check if D3.js is loaded
        if (typeof d3 === 'undefined') {{
            return {{ complete: false, reason: 'D3.js not loaded' }};
        }}
        
        // Check if SVG exists
        const svg = document.querySelector('svg');
        if (!svg) {{
            return {{ complete: false, reason: 'No SVG element' }};
        }}
        
        // Validate SVG content
        if (!validateSVG(svg)) {{
            return {{ complete: false, reason: 'SVG has no content' }};
        }}
        
        // Check if SVG has reasonable dimensions
        const rect = svg.getBoundingClientRect();
        if (rect.width < 100 || rect.height < 100) {{
            return {{ complete: false, reason: 'SVG too small' }};
        }}
        
        return {{ complete: true, reason: 'Ready for download' }};
    }}
    
    // Download function with validation
    function downloadSVG() {{
        if (downloadAttempted) {{
            console.log('Download already attempted');
            return;
        }}
        
        const statusDiv = document.getElementById('status');
        const button = document.getElementById('download-btn');
        const countdownDiv = document.getElementById('countdown');
        
        // Clear any running intervals
        if (renderCheckInterval) clearInterval(renderCheckInterval);
        if (countdownInterval) clearInterval(countdownInterval);
        if (autoDownloadTimeout) clearTimeout(autoDownloadTimeout);
        
        downloadAttempted = true;
        
        try {{
            statusDiv.textContent = 'Checking SVG...';
            button.style.backgroundColor = '#ffc107';
            countdownDiv.textContent = '';
            
            const renderStatus = isRenderingComplete();
            
            if (!renderStatus.complete) {{
                statusDiv.textContent = 'Error: ' + renderStatus.reason;
                button.style.backgroundColor = '#dc3545';
                button.textContent = '❌ SVG Not Ready';
                
                console.error('SVG not ready:', renderStatus.reason);
                
                // Reset for retry
                setTimeout(() => {{
                    downloadAttempted = false;
                    button.textContent = '📥 Download SVG';
                    button.style.backgroundColor = '#28a745';
                    statusDiv.textContent = 'Click to retry';
                }}, 3000);
                
                return;
            }}
            
            statusDiv.textContent = 'Extracting SVG...';
            
            const svg = document.querySelector('svg');
            let svgContent = svg.outerHTML;
            
            // Add XML declaration
            if (!svgContent.startsWith('<?xml')) {{
                svgContent = '<?xml version="1.0" encoding="UTF-8"?>\\n' + svgContent;
            }}
            
            // Ensure namespace
            if (!svgContent.includes('xmlns="http://www.w3.org/2000/svg"')) {{
                svgContent = svgContent.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
            }}
            
            // Validate extracted content
            if (svgContent.length < 500) {{
                throw new Error('SVG content too small (' + svgContent.length + ' chars)');
            }}
            
            // Download the SVG
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
            
            statusDiv.textContent = '✓ Downloaded!';
            button.style.backgroundColor = '#28a745';
            button.textContent = '✓ Downloaded!';
            countdownDiv.textContent = 'File: {unique_filename}';
            
            console.log('Download successful:', '{unique_filename}', svgContent.length, 'chars');
            
        }} catch (error) {{
            console.error('Download error:', error);
            statusDiv.textContent = 'Error: ' + error.message;
            button.style.backgroundColor = '#dc3545';
            button.textContent = '❌ Download Failed';
            
            // Reset for retry
            setTimeout(() => {{
                downloadAttempted = false;
                button.textContent = '📥 Download SVG';
                button.style.backgroundColor = '#28a745';
                statusDiv.textContent = 'Click to retry';
            }}, 3000);
        }}
    }}
    
    // Start monitoring for render completion
    function startRenderMonitoring() {{
        const statusDiv = document.getElementById('status');
        const countdownDiv = document.getElementById('countdown');
        let checkCount = 0;
        const maxChecks = 60; // 30 seconds max wait
        
        renderCheckInterval = setInterval(() => {{
            checkCount++;
            const renderStatus = isRenderingComplete();
            
            statusDiv.textContent = renderStatus.reason + ' (' + checkCount + '/' + maxChecks + ')';
            
            if (renderStatus.complete) {{
                // Rendering is complete, start countdown for auto-download
                clearInterval(renderCheckInterval);
                statusDiv.textContent = 'Ready! Auto-downloading in...';
                
                let countdown = 10; // 10 second countdown
                countdownDiv.textContent = countdown + ' seconds';
                
                countdownInterval = setInterval(() => {{
                    countdown--;
                    countdownDiv.textContent = countdown + ' seconds';
                    
                    if (countdown <= 0) {{
                        clearInterval(countdownInterval);
                        if (!downloadAttempted) {{
                            downloadSVG();
                        }}
                    }}
                }}, 1000);
                
            }} else if (checkCount >= maxChecks) {{
                // Timeout - stop checking
                clearInterval(renderCheckInterval);
                statusDiv.textContent = 'Timeout - click to download anyway';
                countdownDiv.textContent = 'Manual download required';
            }}
        }}, 500); // Check every 500ms
    }}
    
    // Start monitoring when page loads
    setTimeout(startRenderMonitoring, 1000);
    
    console.log('Improved download script loaded for {variant_id}');
    </script>
    
    '''
    
    # Handle different HTML structures
    if '</body>' in html_content:
        modified_html = html_content.replace('</body>', improved_script + '</body>')
    elif '</script>' in html_content:
        last_script_pos = html_content.rfind('</script>')
        if last_script_pos != -1:
            insert_pos = last_script_pos + len('</script>')
            modified_html = html_content[:insert_pos] + improved_script + html_content[insert_pos:]
        else:
            modified_html = html_content + improved_script
    else:
        modified_html = html_content + improved_script
    
    return modified_html, unique_filename


def improved_download_svg(html_file, output_svg):
    """Improved approach with better timing and validation"""
    
    html_path = Path(html_file)
    
    # Get variant ID from path
    variant_id = "unknown"
    for part in html_path.parts:
        if 'variant_' in part:
            variant_id = part
            break
    
    print(f"[Improved] Creating improved download for {variant_id}")
    print(f"[Improved] Input: {html_file}")
    print(f"[Improved] Output: {output_svg}")
    
    # Create improved HTML
    modified_html, unique_filename = create_improved_download_html(html_file, variant_id)
    
    # Save temporary HTML file
    temp_html = html_path.parent / f"temp_improved_{variant_id}.html"
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(modified_html)
    
    print(f"[Improved] Created: {temp_html}")
    
    # Clear old downloads
    downloads_folder = Path.home() / 'Downloads'
    old_files = list(downloads_folder.glob(f'infographic_{variant_id}_*.svg'))
    for old_file in old_files:
        try:
            old_file.unlink()
        except:
            pass
    
    # Open in browser
    print(f"[Improved] Opening browser...")
    print(f"[Improved] Watch the status in the download panel")
    print(f"[Improved] Auto-download will start when D3.js rendering is complete")
    webbrowser.open(f'file://{temp_html.absolute()}')
    
    # Wait for download with extended timeout
    print(f"[Improved] Waiting for download (up to 60 seconds)...")
    
    for i in range(60):
        time.sleep(1)
        
        # Check if file was downloaded
        downloaded_file = downloads_folder / unique_filename
        if downloaded_file.exists():
            print(f"[Improved] Download found after {i+1} seconds!")
            
            # Validate downloaded file
            file_size = downloaded_file.stat().st_size
            if file_size < 500:
                print(f"[Improved] Warning: Downloaded file is very small ({file_size} bytes)")
            
            # Copy to final location
            shutil.copy2(downloaded_file, output_svg)
            print(f"[Improved] Success: {output_svg} ({file_size} bytes)")
            
            # Clean up
            try:
                downloaded_file.unlink()
                temp_html.unlink()
            except:
                pass
            
            return True
        
        # Progress
        if (i + 1) % 15 == 0:
            print(f"[Improved] Still waiting... {i+1}/60 seconds")
    
    print(f"[Improved] Download timeout - check browser for status")
    print(f"[Improved] Temp file kept: {temp_html}")
    
    return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python improved_download.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    
    success = improved_download_svg(html_file, output_svg)
    
    if success:
        print(f"[Improved] SUCCESS: {output_svg}")
        sys.exit(0)
    else:
        print(f"[Improved] TIMEOUT: Check browser panel")
        sys.exit(1)
