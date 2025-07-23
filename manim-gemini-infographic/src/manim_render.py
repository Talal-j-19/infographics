def render_manim_code(filename):
    import os
    import subprocess

    scene_name = "Scene"
    output_path = "output.gif"
    cmd = [
        "manim", "-pql", "--format=gif",
        f"--output_file={output_path}",
        filename, scene_name
    ]
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        stdout = result.stdout
        stderr = result.stderr
        return_code = result.returncode
    except Exception as e:
        stdout = ""
        stderr = str(e)
        return_code = 1

    # Check if the GIF was created
    if os.path.exists(output_path):
        print(f"GIF successfully created at {os.path.abspath(output_path)}")
        return True, stdout, stderr
    else:
        print("Failed to create GIF.")
        print(stderr)
        return False, stdout, stderr