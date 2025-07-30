

from gemini_api_single_frame import get_manim_code_single_frame
from manim_render import render_manim_code

def main():
    import json
    topic = input("Enter your topic for a single-frame Manim infographic: ")
    print("You can optionally enter advanced options as JSON (or just press Enter to skip):")
    options_input = input("Advanced options (JSON): ")
    options = {}
    if options_input.strip():
        try:
            options = json.loads(options_input)
        except Exception as e:
            print(f"[WARN] Could not parse JSON, ignoring advanced options: {e}")
            options = {}
    prompt_obj = {"topic": topic}
    prompt_obj.update(options)

    # Step 1: Ask LLM for a concise list of elements for the infographic
    from gemini_api_single_frame import get_manim_code_single_frame as llm_call
    print("Asking Gemini for a concise list of elements for the infographic...")
    elements_prompt = {
        "topic": topic,
        "task": "List the key visual/text elements needed to make a single-frame Manim infographic for this topic. Only include enough elements to fit one screen and be informative. Return as a JSON list of element descriptions. Do not include code or explanations."
    }
    elements_prompt.update(options)
    elements_response = llm_call(elements_prompt)
    try:
        import json
        elements_list = json.loads(elements_response)
        if not isinstance(elements_list, list):
            raise ValueError("LLM did not return a JSON list.")
    except Exception as e:
        print(f"[ERROR] Could not parse elements list from LLM: {e}\nRaw response: {elements_response}")
        return
    print("Elements to use in infographic:")
    for i, el in enumerate(elements_list, 1):
        print(f"  {i}. {el}")

    # Step 2: Ask LLM to generate Manim code for those elements
    print("Fetching Manim code from Gemini API...")
    code_prompt_obj = {
        "topic": topic,
        "elements": elements_list,
        "task": "Produce Manim Community Edition code for a single-frame infographic using ONLY the provided elements. The code must fit one screen, be informative, and follow all previous rules."
    }
    code_prompt_obj.update(options)
    max_attempts = 10
    attempt = 0
    code_file = "generated_manim_code_single_frame.py"
    manim_code = get_manim_code_single_frame(code_prompt_obj)

    while attempt < max_attempts:
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(manim_code)
        print(f"Generated Manim code saved to: {code_file}")

        print(f"Rendering the Manim code... (Attempt {attempt+1}/{max_attempts})")
        success, stdout, stderr = render_manim_code(code_file, still_image=True)
        if success:
            break
        else:
            print("Attempting to fix code using Gemini API...")
            from gemini_api_single_frame import get_manim_code_single_frame as fix_manim_code
            error_prompt_obj = {
                "topic": topic,
                "error_message": stderr,
                "previous_code": manim_code,
                "rules": [
                    "Only return valid, working Manim Community Edition code (v0.13.1).",
                    "The main scene class MUST be named 'Scene'.",
                    "The output must be a single static frame (no animation).",
                    "All information about the topic must be visible in that single frame.",
                    "Use only valid Manim Community Edition syntax and functions.",
                    "DO NOT use any markdown, explanations, or extra text.",
                    "DO NOT use '```' or 'python' code blocks.",
                    "If you are unsure, copy working patterns from the official Manim Community Edition documentation."
                ]
            }
            error_prompt_obj.update(options)
            manim_code = fix_manim_code(error_prompt_obj)
            attempt += 1
    else:
        print("Failed to render Manim code after 5 attempts.")

if __name__ == "__main__":
    main()
