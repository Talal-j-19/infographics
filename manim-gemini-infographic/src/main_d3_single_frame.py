from gemini_api_d3_single_frame import get_d3_code_single_frame

def main():
    import json
    topic = input("Enter your topic for a single-frame D3.js infographic: ")
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
    from gemini_api_d3_single_frame import get_d3_code_single_frame as llm_call
    print("Asking Gemini for a concise list of elements for the infographic...")
    elements_prompt = {
        "topic": topic,
        "task": "List the key visual/text elements needed to make a single-frame D3.js infographic for this topic. Only include enough elements to fit one screen and be informative. Return as a JSON list of element descriptions. Do not include code or explanations."
    }
    elements_prompt.update(options)
    elements_response = llm_call(elements_prompt)
    try:
        elements_list = json.loads(elements_response)
        if not isinstance(elements_list, list):
            raise ValueError("LLM did not return a JSON list.")
    except Exception as e:
        print(f"[ERROR] Could not parse elements list from LLM: {e}\nRaw response: {elements_response}")
        return
    print("Elements to use in infographic:")
    for i, el in enumerate(elements_list, 1):
        print(f"  {i}. {el}")

    # Step 2: Ask LLM to generate D3.js code for those elements
    print("Fetching D3.js code from Gemini API...")
    code_prompt_obj = {
        "topic": topic,
        "elements": elements_list,
        "task": "Produce D3.js (HTML+JS) code for a single-frame infographic using ONLY the provided elements. The code must fit one screen, be informative, and follow all previous rules."
    }
    code_prompt_obj.update(options)
    max_attempts = 10
    attempt = 0
    code_file = "generated_d3_code_single_frame.html"
    d3_code = get_d3_code_single_frame(code_prompt_obj)

    while attempt < max_attempts:
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(d3_code)
        print(f"Generated D3.js code saved to: {code_file}")

        # Try to open the HTML file in the default browser for preview
        import webbrowser
        import os
        abs_path = os.path.abspath(code_file)
        print(f"Opening {abs_path} in your default browser...")
        webbrowser.open(f"file://{abs_path}")

        # Ask user if the output looks correct
        user_feedback = input("Does the output look correct? (y/n): ").strip().lower()
        if user_feedback == 'y':
            # Export PNG automatically using the helper
            try:
                from save_infographic_as_png import save_infographic_as_png
                print("Exporting infographic as PNG...")
                png_path = save_infographic_as_png(code_file)
                print(f"PNG saved to: {png_path}")
            except Exception as e:
                print(f"[WARN] Could not export PNG automatically: {e}")
            break
        else:
            print("Attempting to fix code using Gemini API...")
            from gemini_api_d3_single_frame import get_d3_code_single_frame as fix_d3_code
            error_prompt_obj = {
                "topic": topic,
                "error_message": "User feedback: output is not correct.",
                "previous_code": d3_code,
                "rules": [
                    "Only return valid, working D3.js (v7+) and SVG code.",
                    "The output must be a single static frame (no animation unless requested).",
                    "All information about the topic must be visible in that single frame.",
                    "Use only valid D3.js and SVG syntax and functions.",
                    "DO NOT use any markdown, explanations, or extra text.",
                    "DO NOT use '```' or 'html' code blocks.",
                    "If you are unsure, copy working patterns from the official D3.js documentation."
                ]
            }
            error_prompt_obj.update(options)
            d3_code = fix_d3_code(error_prompt_obj)
            attempt += 1
    else:
        print("Failed to generate correct D3.js code after 5 attempts.")

if __name__ == "__main__":
    main()
