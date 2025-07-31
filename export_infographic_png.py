import sys
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Usage: python export_infographic_png.py <html_file> <output_png>

def export_infographic_to_png(html_file, output_png, wait_time=2):
    html_path = Path(html_file).absolute().as_uri()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1400,900')
    from selenium.webdriver.chrome.service import Service
    service = Service(r'D:\infographics\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(html_path)
        time.sleep(5)  # Wait longer for D3 to render
        try:
            svg_elem = driver.find_element(By.TAG_NAME, 'svg')
        except Exception as svg_exc:
            print('[ERROR] Could not find <svg> element after waiting. Dumping page source:')
            print(driver.page_source)
            raise svg_exc
        width = svg_elem.get_attribute('width')
        height = svg_elem.get_attribute('height')
        print(f"SVG width attribute: {width}, height attribute: {height}")
        # If width/height are missing or zero, set them via JavaScript
        if not width or not height or int(width) == 0 or int(height) == 0:
            bbox = driver.execute_script('var svg=arguments[0]; var bb=svg.getBBox(); svg.setAttribute(\"width\", bb.width); svg.setAttribute(\"height\", bb.height); return [bb.width, bb.height];', svg_elem)
            width, height = bbox
            print(f"Set SVG width/height to bounding box: width={width}, height={height}")
        else:
            width = int(width)
            height = int(height)
        # Screenshot the SVG element only
        png = svg_elem.screenshot_as_png
        with open(output_png, 'wb') as f:
            f.write(png)
        print(f"Saved PNG: {output_png}")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}", file=sys.stderr)
        import traceback; traceback.print_exc()
    finally:
        driver.quit()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python export_infographic_png.py <html_file> <output_png>")
        sys.exit(1)
    html_file = sys.argv[1]
    output_png = sys.argv[2]
    export_infographic_to_png(html_file, output_png)
