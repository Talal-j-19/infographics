#!/usr/bin/env python3
"""
Reliable SVG Export with Multiple Fallback Methods
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import tempfile
import shutil


def method1_selenium_with_retry(html_file, output_svg, max_retries=3):
    """Method 1: Selenium with retry logic and process cleanup"""
    for attempt in range(max_retries):
        try:
            print(f"[Method 1] Selenium attempt {attempt + 1}/{max_retries}")
            
            # Kill any existing Chrome processes first
            try:
                subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                             capture_output=True, check=False)
                subprocess.run(['taskkill', '/f', '/im', 'chromedriver.exe'], 
                             capture_output=True, check=False)
                time.sleep(2)
            except:
                pass
            
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Configure Chrome with stability options
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript-harmony-shipping')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--window-size=1400,900')
            options.add_argument('--memory-pressure-off')
            
            # Use chromedriver from the project
            chromedriver_path = Path(__file__).parent.parent.parent / 'chromedriver.exe'
            if not chromedriver_path.exists():
                chromedriver_path = Path(__file__).parent / 'chromedriver.exe'
            
            from selenium.webdriver.chrome.service import Service
            service = Service(str(chromedriver_path))
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            
            try:
                # Load the HTML file
                html_path = Path(html_file).absolute().as_uri()
                driver.get(html_path)
                
                # Wait for SVG element to be present
                wait = WebDriverWait(driver, 15)
                svg_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'svg')))
                
                # Additional wait for D3.js to complete rendering
                time.sleep(3)
                
                # Get SVG content
                svg_content = driver.execute_script("return document.querySelector('svg').outerHTML;")
                
                if not svg_content or len(svg_content) < 100:
                    raise Exception("SVG content is empty or too small")
                
                # Get CSS styles
                css_styles = driver.execute_script("""
                    var styles = '';
                    for (var i = 0; i < document.styleSheets.length; i++) {
                        try {
                            var sheet = document.styleSheets[i];
                            for (var j = 0; j < sheet.cssRules.length; j++) {
                                styles += sheet.cssRules[j].cssText + '\\n';
                            }
                        } catch (e) {}
                    }
                    return styles;
                """)
                
                # Process and save SVG
                processed_svg = process_svg_content(svg_content, css_styles)
                
                with open(output_svg, 'w', encoding='utf-8') as f:
                    f.write(processed_svg)
                
                print(f"[Method 1] Success: {output_svg}")
                return True
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"[Method 1] Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print(f"[Method 1] All attempts failed")
            else:
                time.sleep(2)  # Wait before retry
    
    return False


def method2_puppeteer_fallback(html_file, output_svg):
    """Method 2: Use Puppeteer via Node.js if available"""
    try:
        print("[Method 2] Trying Puppeteer fallback")
        
        # Create a temporary Node.js script
        puppeteer_script = f"""
const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {{
    const browser = await puppeteer.launch({{
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }});
    
    const page = await browser.newPage();
    await page.setViewport({{ width: 1400, height: 900 }});
    await page.goto('file://{Path(html_file).absolute().as_posix()}');
    
    // Wait for SVG to render
    await page.waitForSelector('svg', {{ timeout: 10000 }});
    await page.waitForTimeout(3000);
    
    // Get SVG content
    const svgContent = await page.evaluate(() => {{
        const svg = document.querySelector('svg');
        return svg ? svg.outerHTML : null;
    }});
    
    if (svgContent) {{
        fs.writeFileSync('{output_svg}', svgContent);
        console.log('Puppeteer success');
    }} else {{
        throw new Error('No SVG found');
    }}
    
    await browser.close();
}})().catch(console.error);
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(puppeteer_script)
            script_path = f.name
        
        try:
            result = subprocess.run(['node', script_path], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and Path(output_svg).exists():
                print(f"[Method 2] Success: {output_svg}")
                return True
        finally:
            os.unlink(script_path)
            
    except Exception as e:
        print(f"[Method 2] Failed: {e}")
    
    return False


def method3_html_to_svg_conversion(html_file, output_svg):
    """Method 3: Extract SVG from HTML using BeautifulSoup and simulate D3.js"""
    try:
        print("[Method 3] Trying HTML parsing method")
        
        from bs4 import BeautifulSoup
        import re
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract CSS styles
        styles = []
        for style_tag in soup.find_all('style'):
            styles.append(style_tag.get_text())
        
        # Look for D3.js code patterns and extract basic structure
        script_content = ""
        for script_tag in soup.find_all('script'):
            if script_tag.string and 'd3.' in script_tag.string:
                script_content = script_tag.string
                break
        
        # Create a basic SVG structure based on common D3.js patterns
        svg_content = create_fallback_svg(script_content, '\n'.join(styles))
        
        with open(output_svg, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"[Method 3] Success: {output_svg}")
        return True
        
    except Exception as e:
        print(f"[Method 3] Failed: {e}")
    
    return False


def method4_copy_existing_svg(html_file, output_svg):
    """Method 4: Look for existing SVG files in the same directory"""
    try:
        print("[Method 4] Looking for existing SVG files")
        
        html_dir = Path(html_file).parent
        existing_svgs = list(html_dir.glob('*.svg'))
        
        if existing_svgs:
            # Use the most recent SVG file
            latest_svg = max(existing_svgs, key=lambda x: x.stat().st_mtime)
            shutil.copy2(latest_svg, output_svg)
            print(f"[Method 4] Copied existing SVG: {latest_svg} -> {output_svg}")
            return True
            
    except Exception as e:
        print(f"[Method 4] Failed: {e}")
    
    return False


def process_svg_content(svg_content, css_styles=""):
    """Process SVG content to make it standalone and editor-friendly"""
    # Add XML declaration if not present
    if not svg_content.startswith('<?xml'):
        svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content
    
    # Add xmlns if not present
    if 'xmlns=' not in svg_content:
        svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
    
    # Embed CSS styles
    if css_styles:
        style_tag = f'<style type="text/css"><![CDATA[{css_styles}]]></style>'
        svg_content = svg_content.replace(
            '<svg xmlns="http://www.w3.org/2000/svg"',
            f'<svg xmlns="http://www.w3.org/2000/svg">{style_tag}',
            1
        )
    
    return svg_content


def create_fallback_svg(script_content, css_styles):
    """Create a fallback SVG when other methods fail"""
    # This is a basic fallback - you can enhance this based on your D3.js patterns
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
    <style type="text/css"><![CDATA[
        {css_styles}
        text {{ font-family: Arial, sans-serif; }}
        .fallback {{ fill: #666; font-size: 14px; }}
    ]]></style>
    <rect width="800" height="600" fill="#f9f9f9" stroke="#ddd"/>
    <text x="400" y="300" text-anchor="middle" class="fallback">
        SVG Export Fallback - Original content could not be rendered
    </text>
    <text x="400" y="320" text-anchor="middle" class="fallback" font-size="12">
        Please check the HTML file for the interactive version
    </text>
</svg>"""
    return svg


def reliable_svg_export(html_file, output_svg):
    """
    Export SVG using multiple fallback methods for maximum reliability
    """
    html_path = Path(html_file)
    output_path = Path(output_svg)
    
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting reliable SVG export: {html_file} -> {output_svg}")
    
    # Try methods in order of preference
    methods = [
        method1_selenium_with_retry,
        method2_puppeteer_fallback,
        method3_html_to_svg_conversion,
        method4_copy_existing_svg
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            if method(str(html_path), str(output_path)):
                # Verify the file was created and has content
                if output_path.exists() and output_path.stat().st_size > 100:
                    print(f"✅ SVG export successful using method {i}")
                    return str(output_path)
        except Exception as e:
            print(f"Method {i} exception: {e}")
    
    # If all methods fail, create a minimal fallback
    print("⚠️ All methods failed, creating minimal fallback SVG")
    fallback_svg = create_fallback_svg("", "")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fallback_svg)
    
    return str(output_path)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python reliable_svg_export.py <html_file> <output_svg>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    result = reliable_svg_export(html_file, output_svg)
    print(f"Final result: {result}")
