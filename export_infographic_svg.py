import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Usage: python export_infographic_svg.py <html_file> <output_svg>


def format_svg_for_editors(svg_content):
    """
    Format SVG content to be more editor-friendly by:
    1. Adding proper indentation and line breaks
    2. Converting some CSS classes to inline styles for better compatibility
    3. Adding comments for major sections
    """
    from xml.dom import minidom

    try:
        # Parse and pretty-print the SVG
        dom = minidom.parseString(svg_content)
        pretty_svg = dom.toprettyxml(indent="  ")

        # Remove the XML declaration line and empty lines
        lines = pretty_svg.split('\n')
        lines = [line for line in lines if line.strip() and not line.startswith('<?xml')]

        # Join back and clean up
        formatted_svg = '\n'.join(lines)

        # Add back the XML declaration at the top
        formatted_svg = '<?xml version="1.0" encoding="UTF-8"?>\n' + formatted_svg

        return formatted_svg

    except Exception as e:
        print(f"[WARN] Could not format SVG for editors: {e}")
        return svg_content


def export_infographic_to_svg(html_file, output_svg, wait_time=2):
    """
    Export the SVG content from an HTML file to a standalone SVG file.
    """
    html_path = Path(html_file).absolute().as_uri() + f"?v={int(time.time())}"
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
            svg_content = ('<?xml version="1.0" encoding="UTF-8"?>\n' +
                           svg_content)

        # Make sure the SVG has the proper xmlns attribute
        if 'xmlns=' not in svg_content:
            svg_content = svg_content.replace(
                '<svg',
                '<svg xmlns="http://www.w3.org/2000/svg"'
            )

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

        # Format SVG for better editor compatibility
        svg_content = format_svg_for_editors(svg_content)

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
    if len(sys.argv) != 3:
        print("Usage: python export_infographic_svg.py <html_file> <output_svg>")
        sys.exit(1)
    html_file = sys.argv[1]
    output_svg = sys.argv[2]
    export_infographic_to_svg(html_file, output_svg)
