import subprocess
from pathlib import Path


def save_infographic_as_svg(html_path, output_svg=None):
    """
    Given a path to a generated HTML infographic, export the SVG content as a standalone SVG file.
    If output_svg is None, saves as <html_path>.svg in the same folder.
    Uses reliable export with multiple fallback methods.
    """
    html_path = Path(html_path)
    if output_svg is None:
        output_svg = html_path.with_suffix('.svg')

    # Convert to absolute paths to avoid working directory issues
    html_path_abs = html_path.resolve()
    output_svg_abs = Path(output_svg).resolve()

    print(f"[DEBUG] Starting reliable SVG export: {html_path_abs} -> {output_svg_abs}")

    try:
        # Use the reliable SVG export method
        from reliable_svg_export import reliable_svg_export
        result_path = reliable_svg_export(str(html_path_abs), str(output_svg_abs))
        print(f"[DEBUG] Reliable SVG export completed: {result_path}")
        return result_path
    except Exception as e:
        print(f"[ERROR] Reliable SVG export failed: {e}")
        # Fallback to original method as last resort
        try:
            script_path = Path(__file__).parent.parent.parent / 'export_infographic_svg.py'
            script_path = script_path.resolve()
            venv_python = Path(__file__).parent.parent.parent / 'venv' / 'Scripts' / 'python.exe'
            subprocess.run([
                str(venv_python), str(script_path), str(html_path_abs), str(output_svg_abs)
            ], check=True)
            return str(output_svg_abs)
        except Exception as e2:
            print(f"[ERROR] Fallback SVG export also failed: {e2}")
            raise e


if __name__ == '__main__':
    print('[DEBUG] save_infographic_as_svg.py script started')
    import argparse
    parser = argparse.ArgumentParser(description='Save infographic as SVG')
    parser.add_argument('html_path', type=str, help='Path to HTML file')
    parser.add_argument('output_svg', type=str, nargs='?', default=None, help='Output SVG path')
    args = parser.parse_args()
    save_infographic_as_svg(args.html_path, args.output_svg)
