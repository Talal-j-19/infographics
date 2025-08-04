import subprocess
from pathlib import Path


def save_infographic_as_svg(html_path, output_svg=None):
    """
    Given a path to a generated HTML infographic, export the SVG content as a standalone SVG file.
    If output_svg is None, saves as <html_path>.svg in the same folder.
    """
    html_path = Path(html_path)
    if output_svg is None:
        output_svg = html_path.with_suffix('.svg')

    # Convert paths to absolute paths to avoid working directory issues
    html_path_abs = html_path.resolve()
    output_svg_abs = Path(output_svg).resolve()

    # Use the standalone SVG export script (which we know works)
    script_path = Path(__file__).parent.parent.parent / 'export_infographic_svg.py'
    script_path = script_path.resolve()

    # Use the Python interpreter from the venv
    venv_python = Path(__file__).parent.parent.parent / 'venv' / 'Scripts' / 'python.exe'

    print(f"[DEBUG] Calling export_infographic_svg.py: {html_path_abs} -> {output_svg_abs}")
    subprocess.run([
        str(venv_python), str(script_path), str(html_path_abs), str(output_svg_abs)
    ], check=True)
    print(f"[DEBUG] Finished calling export_infographic_svg.py for SVG export")
    return str(output_svg_abs)


if __name__ == '__main__':
    print('[DEBUG] save_infographic_as_svg.py script started')
    import argparse
    parser = argparse.ArgumentParser(description='Save infographic as SVG')
    parser.add_argument('html_path', type=str, help='Path to HTML file')
    parser.add_argument('output_svg', type=str, nargs='?', default=None, help='Output SVG path')
    args = parser.parse_args()
    save_infographic_as_svg(args.html_path, args.output_svg)
