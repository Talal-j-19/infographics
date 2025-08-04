import sys
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Usage: python export_infographic_png.py <html_file> <output_png>
# Usage: python export_infographic_png.py <html_file> <output_svg> --svg

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


def export_infographic_to_svg(html_file, output_svg, wait_time=2):
    """
    Export the SVG content from an HTML file to a standalone SVG file.
    """
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
        time.sleep(5)  # Wait for D3 to render
        try:
            svg_elem = driver.find_element(By.TAG_NAME, 'svg')
        except Exception as svg_exc:
            print('[ERROR] Could not find <svg> element after waiting.')
            print(driver.page_source)
            raise svg_exc

        # Get the SVG content as HTML (which includes the SVG markup)
        svg_content = svg_elem.get_attribute('outerHTML')

        # Extract CSS styles from the page
        try:
            style_elements = driver.find_elements(By.TAG_NAME, 'style')
            css_styles = ""
            for style_elem in style_elements:
                css_content = style_elem.get_attribute('innerHTML')
                if css_content:
                    css_styles += css_content + "\n"
        except Exception:
            css_styles = ""

        # Ensure the SVG has proper XML declaration and namespace
        if not svg_content.startswith('<?xml'):
            svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

        # Make sure the SVG has the proper xmlns attribute
        if 'xmlns=' not in svg_content:
            svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')

        # Inject CSS styles into the SVG
        if css_styles:
            # Create a <style> element with CDATA section for the CSS
            style_tag = f'<style type="text/css"><![CDATA[{css_styles}]]></style>'
            # Insert the style tag right after the opening <svg> tag
            svg_content = svg_content.replace(
                '<svg xmlns="http://www.w3.org/2000/svg"',
                f'<svg xmlns="http://www.w3.org/2000/svg">{style_tag}',
                1
            )

        # Write the SVG content to file
        with open(output_svg, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"Saved SVG: {output_svg}")

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python export_infographic_png.py <html_file> <output_file> [--svg]")
        sys.exit(1)

    html_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check if SVG export is requested
    if len(sys.argv) > 3 and sys.argv[3] == '--svg':
        export_infographic_to_svg(html_file, output_file)
    else:
        export_infographic_to_png(html_file, output_file)
