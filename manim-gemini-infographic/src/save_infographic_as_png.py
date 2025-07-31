import subprocess
from pathlib import Path

import subprocess
from pathlib import Path

def save_infographic_as_png(html_path, output_png=None):
    """
    Given a path to a generated HTML infographic, export the SVG as a PNG using Selenium.
    If output_png is None, saves as <html_path>.png in the same folder.
    """
    html_path = Path(html_path)
    if output_png is None:
        output_png = html_path.with_suffix('.png')
    # Look for export_infographic_png.py in the project root
    # Look for export_infographic_png.py in the project root (d:/infographics)
    script_path = Path(__file__).parent.parent.parent / 'export_infographic_png.py'
    script_path = script_path.resolve()
    # Use the Python interpreter from the venv in d:/infographics/venv/Scripts/python.exe
    venv_python = Path(__file__).parent.parent.parent / 'venv' / 'Scripts' / 'python.exe'
    print(f"[DEBUG] Calling export_infographic_png.py with: {html_path} {output_png}")
    subprocess.run([
        str(venv_python), str(script_path), str(html_path), str(output_png)
    ], check=True)
    print(f"[DEBUG] Finished calling export_infographic_png.py")
    return output_png

if __name__ == '__main__':
    print('[DEBUG] save_infographic_as_png.py script started')
    import argparse
    parser = argparse.ArgumentParser(description='Save infographic as PNG')
    parser.add_argument('html_path', type=str, help='Path to HTML file')
    parser.add_argument('output_png', type=str, nargs='?', default=None, help='Output PNG path')
    args = parser.parse_args()
    save_infographic_as_png(args.html_path, args.output_png)
