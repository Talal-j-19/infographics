import os
from gemini_api import get_manim_code
from manim_render import render_manim_code

def main():
    prompt = input("Enter your prompt for the Gemini API to generate Manim code: ")
    print("Fetching Manim code from Gemini API...")
    
    max_attempts = 10
    attempt = 0
    code_file = "generated_manim_code.py"
    manim_code = get_manim_code(prompt)

    while attempt < max_attempts:
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(manim_code)
        print(f"Generated Manim code saved to: {code_file}")

        print(f"Rendering the Manim code... (Attempt {attempt+1}/{max_attempts})")
        success, stdout, stderr = render_manim_code(code_file)
        if success:
            break
        else:
            print("Attempting to fix code using Gemini API...")
            from gemini_api import get_manim_code as fix_manim_code
            error_prompt = (
                "The following Manim code did not render successfully. "
                "You are a Manim Community Edition (v0.13.1) expert. "
                "Your task is to fix ALL errors based on the error message below. "
                "STRICT RULES:\n"
                "- Only return valid, working Manim Community Edition code (v0.13.1).\n"
                "- The main scene class MUST be named 'Scene'.\n"
                "- Use only valid Manim Community Edition syntax and functions.\n"
                "- DO NOT use any markdown, explanations, or extra text.\n"
                "- DO NOT use '```' or 'python' code blocks.\n"
                "- If you are unsure, copy working patterns from the official Manim Community Edition documentation.\n"
                "CODE:\n"
                f"{manim_code}\n\n"
                "ERROR MESSAGE:\n"
                f"{stderr}\n"
                "Return ONLY the corrected Manim code."
            )
            manim_code = fix_manim_code(error_prompt)
            attempt += 1
    else:
        print("Failed to render Manim code after 10 attempts.")

if __name__ == "__main__":
    main()