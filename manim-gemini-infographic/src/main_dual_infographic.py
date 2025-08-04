import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
from pathlib import Path
from typing import List, Tuple

def run_manim_single_frame(topic: str, output_dir: Path) -> Path:
    """Run the Manim single-frame flow for a topic and return the image path."""
    script = Path(__file__).parent / 'main_single_frame.py'
    output_path = output_dir / f"{topic}_manim.png"
    subprocess.run([
        sys.executable, str(script), topic, str(output_path)
    ], check=True)
    return output_path

def run_d3_single_frame(topic: str, output_dir: Path) -> Path:
    """Run the D3.js single-frame flow for a topic and return the image path."""
    script = Path(__file__).parent / 'main_d3_single_frame.py'
    output_path = output_dir / f"{topic}_d3.png"
    subprocess.run([
        sys.executable, str(script), topic, str(output_path)
    ], check=True)
    return output_path

def generate_infographics_for_topics(topics: List[str], output_dir: Path) -> List[Tuple[str, Path, Path]]:
    """For each topic, run both flows in parallel and return the image paths."""
    results = []
    for topic in topics:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(run_manim_single_frame, topic, output_dir): 'manim',
                executor.submit(run_d3_single_frame, topic, output_dir): 'd3',
            }
            done, _ = next(as_completed(futures), None), None
            # Accept whichever D3.js finishes first, but always wait for Manim
            manim_path = None
            d3_path = None
            for future in as_completed(futures):
                flow = futures[future]
                try:
                    img_path = future.result()
                    if flow == 'manim':
                        manim_path = img_path
                    else:
                        d3_path = img_path
                        break  # Accept first D3.js result
                except Exception as e:
                    print(f"Error in {flow} flow for topic '{topic}': {e}")
            # Wait for Manim if not done
            if manim_path is None:
                manim_path = [f.result() for f, flow in futures.items() if flow == 'manim'][0]
            results.append((topic, manim_path, d3_path))
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate Manim and D3.js infographics for topics.')
    parser.add_argument('topics', nargs='+', help='List of topics')
    parser.add_argument('--output_dir', default='generated_infographics', help='Output directory')
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    results = generate_infographics_for_topics(args.topics, output_dir)
    for topic, manim_img, d3_img in results:
        print(f"Topic: {topic}\n  Manim: {manim_img}\n  D3.js: {d3_img}")

if __name__ == '__main__':
    main()
