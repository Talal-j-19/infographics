#!/usr/bin/env python3
"""
Headless SVG Export - Uses headless browser automation for reliable SVG extraction
"""

import sys
import subprocess
import shutil
from pathlib import Path
import time
import json


def check_playwright_installation():
    """Check if Playwright is installed and browsers are available"""
    try:
        # Check if playwright is installed
        result = subprocess.run([sys.executable, '-c', 'import playwright'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return False, "Playwright not installed"

        # Try to find playwright executable in venv
        venv_playwright = Path(sys.executable).parent / 'playwright.exe'
        if venv_playwright.exists():
            # Check if browsers are installed
            result = subprocess.run([str(venv_playwright), 'install', '--dry-run'],
                                  capture_output=True, text=True, timeout=10)
        else:
            # Playwright module is installed, assume browsers are available
            pass

        return True, "Playwright available"

    except Exception as e:
        return False, f"Playwright check failed: {e}"


def install_playwright():
    """Install Playwright and browsers"""
    print("[Headless] Installing Playwright...")

    try:
        # Install playwright
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'playwright'],
                              capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"[Headless] Failed to install Playwright: {result.stderr}")
            return False

        # Install browsers using venv playwright
        venv_playwright = Path(sys.executable).parent / 'playwright.exe'
        if venv_playwright.exists():
            result = subprocess.run([str(venv_playwright), 'install', 'chromium'],
                                  capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"[Headless] Failed to install browsers: {result.stderr}")
                return False
        else:
            print("[Headless] Playwright executable not found, but module is installed")

        print("[Headless] Playwright installed successfully")
        return True

    except Exception as e:
        print(f"[Headless] Installation failed: {e}")
        return False


def create_headless_script(html_file, output_svg, variant_id):
    """Create a Playwright script for headless SVG extraction"""

    script_content = '''
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def extract_svg():
    """Extract SVG using headless Playwright"""

    html_file = r"''' + html_file + '''"
    output_svg = r"''' + output_svg + '''"
    variant_id = "''' + variant_id + '''"
    
    print(f"[Headless] Starting extraction for {variant_id}")
    print(f"[Headless] Input: {html_file}")
    print(f"[Headless] Output: {output_svg}")
    
    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-extensions'
            ]
        )
        
        try:
            # Create new page
            page = await browser.new_page()
            
            # Set viewport
            await page.set_viewport_size({"width": 1200, "height": 800})
            
            # Navigate to HTML file
            file_url = f"file://{Path(html_file).absolute()}"
            print(f"[Headless] Loading: {file_url}")
            
            await page.goto(file_url, wait_until='networkidle', timeout=30000)
            
            # Wait for D3.js to load and render
            print("[Headless] Waiting for D3.js to load...")
            
            # Check if D3.js is available
            d3_available = await page.evaluate("typeof d3 !== 'undefined'")
            if not d3_available:
                print("[Headless] D3.js not loaded, waiting longer...")
                await page.wait_for_timeout(5000)
                d3_available = await page.evaluate("typeof d3 !== 'undefined'")
            
            if not d3_available:
                print("[Headless] ERROR: D3.js failed to load")
                return False
            
            print("[Headless] D3.js loaded successfully")
            
            # Wait for SVG to be created and populated
            print("[Headless] Waiting for SVG rendering...")
            
            # Wait for SVG element
            await page.wait_for_selector('svg', timeout=15000)
            
            # Wait a bit more for content to render
            await page.wait_for_timeout(3000)
            
            # Validate SVG content
            svg_validation = await page.evaluate("""
                () => {
                    const svg = document.querySelector('svg');
                    if (!svg) return { valid: false, reason: 'No SVG element' };

                    const children = svg.children.length;
                    if (children === 0) return { valid: false, reason: 'SVG has no children' };

                    const textElements = svg.querySelectorAll('text').length;
                    if (textElements === 0) return { valid: false, reason: 'No text elements' };

                    const rect = svg.getBoundingClientRect();
                    if (rect.width < 100 || rect.height < 100) {
                        return { valid: false, reason: 'SVG too small' };
                    }

                    return {
                        valid: true,
                        children: children,
                        textElements: textElements,
                        width: rect.width,
                        height: rect.height
                    };
                }
            """)
            
            if not svg_validation['valid']:
                print(f"[Headless] SVG validation failed: {svg_validation['reason']}")
                return False

            print(f"[Headless] SVG validation passed:")
            print(f"[Headless]   Children: {svg_validation['children']}")
            print(f"[Headless]   Text elements: {svg_validation['textElements']}")
            print(f"[Headless]   Dimensions: {svg_validation['width']}x{svg_validation['height']}")
            
            # Extract SVG content
            svg_content = await page.evaluate("""
                () => {
                    const svg = document.querySelector('svg');
                    if (!svg) return null;

                    let content = svg.outerHTML;

                    // Add XML declaration if missing
                    if (!content.startsWith('<?xml')) {
                        content = '<?xml version="1.0" encoding="UTF-8"?>\\n' + content;
                    }

                    // Ensure namespace
                    if (!content.includes('xmlns="http://www.w3.org/2000/svg"')) {
                        content = content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
                    }

                    return content;
                }
            """)
            
            if not svg_content:
                print("[Headless] Failed to extract SVG content")
                return False
            
            # Validate extracted content
            if len(svg_content) < 500:
                print(f"[Headless] SVG content too small: {len(svg_content)} chars")
                return False

            # Save SVG file
            with open(output_svg, 'w', encoding='utf-8') as f:
                f.write(svg_content)

            file_size = Path(output_svg).stat().st_size
            print(f"[Headless] SVG saved: {output_svg} ({file_size} bytes)")

            return True

        except Exception as e:
            print(f"[Headless] Error during extraction: {e}")
            return False
            
        finally:
            await browser.close()

# Run the extraction
if __name__ == "__main__":
    success = asyncio.run(extract_svg())
    sys.exit(0 if success else 1)
'''
    
    return script_content


def headless_svg_export(html_file, output_svg):
    """Main headless SVG export function"""
    
    html_path = Path(html_file)
    
    # Get variant ID from path
    variant_id = "unknown"
    for part in html_path.parts:
        if 'variant_' in part:
            variant_id = part
            break
    
    print(f"[Headless] Starting headless SVG export for {variant_id}")
    print(f"[Headless] Input: {html_file}")
    print(f"[Headless] Output: {output_svg}")
    
    # Check if Playwright is available
    available, message = check_playwright_installation()
    if not available:
        print(f"[Headless] {message}")
        print("[Headless] Attempting to install Playwright...")
        
        if not install_playwright():
            print("[Headless] Failed to install Playwright")
            return False
    else:
        print(f"[Headless] {message}")
    
    # Create temporary script
    script_content = create_headless_script(html_file, output_svg, variant_id)
    temp_script = html_path.parent / f"temp_headless_{variant_id}.py"
    
    try:
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"[Headless] Created temporary script: {temp_script}")
        
        # Run the headless script
        print("[Headless] Running headless extraction...")
        result = subprocess.run([sys.executable, str(temp_script)], 
                              capture_output=True, text=True, timeout=120)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"[Headless] Stderr: {result.stderr}")
        
        # Check if successful
        if result.returncode == 0 and Path(output_svg).exists():
            file_size = Path(output_svg).stat().st_size
            print(f"[Headless] SUCCESS: {output_svg} ({file_size} bytes)")
            
            # Clean up
            try:
                temp_script.unlink()
            except:
                pass
            
            return True
        else:
            print(f"[Headless] FAILED: Return code {result.returncode}")
            return False
    
    except subprocess.TimeoutExpired:
        print("[Headless] TIMEOUT: Script took too long")
        return False
    except Exception as e:
        print(f"[Headless] ERROR: {e}")
        return False
    finally:
        # Clean up temp script
        try:
            if temp_script.exists():
                temp_script.unlink()
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python headless_svg_export.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    
    success = headless_svg_export(html_file, output_svg)
    
    if success:
        print(f"[Headless] SUCCESS: {output_svg}")
        sys.exit(0)
    else:
        print(f"[Headless] FAILED: {output_svg}")
        sys.exit(1)
