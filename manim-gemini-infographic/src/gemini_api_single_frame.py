def get_manim_code_single_frame(prompt):
    import os
    from dotenv import load_dotenv
    import google.generativeai as genai

    # Load .env file so environment variables are available
    load_dotenv()

    # Load API key from environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)

    # If prompt is a dict and has a 'task', branch logic
    if isinstance(prompt, dict) and 'task' in prompt:
        task = prompt['task'].lower()
        if 'list' in task and 'element' in task:
            # Step 1: List elements for the infographic
            system_prompt = (
                "You are a Manim infographic designer. "
                "Given a topic, return a JSON list of the key Manim elements (e.g., Text, VGroup, Rectangle, Arrow, etc.) needed to make a single-frame Manim infographic. "
                "Choose only valid Manim Community Edition elements. "
                "The elements should be chosen to make the infographic as informative as possible, but must not crowd the screen and must not overlap. "
                "Only include enough elements to fit one screen and be visually clear. "
                "Return ONLY a JSON list of element descriptions, no code, no explanations, no markdown."
            )
            user_prompt = (
                f"Topic: {prompt.get('topic', '')}\n"
                f"{prompt.get('task', '')}"
            )
            model = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=system_prompt
            )
            response = model.generate_content(user_prompt)
            elements = response.text.strip()
            # Remove accidental code blocks
            if elements.startswith("```json"):
                elements = elements[7:]
            if elements.startswith("```"):
                elements = elements[3:]
            if elements.endswith("```"):
                elements = elements[:-3]
            elements = elements.strip()
            return elements
        elif 'code' in task:
            # Step 2: Generate code for the given elements
            system_prompt = (
                "You are a Manim expert who creates beautiful, informative, and highly readable single-frame infographics. "
                "You must ONLY use valid Manim Community Edition (v0.13.1) syntax and functions—do not use any syntax, classes, or methods that are not part of the official Manim Community Edition. "
                "You must ONLY return valid Python Manim code, with NO explanations, NO markdown, and NO ```python or ``` blocks. "
                "The main scene class MUST always be named 'Scene'. "
                "The output must be a single static frame (no animation). "
                "All information about the topic must be visible in that single frame. "
                "Text and labels must be well-placed, non-overlapping, and clearly readable. "
                "Include key concepts and explanations with clear, non-crowded diagrams. "
                "Do NOT use any custom or undefined classes, functions, or imports. "
                "Do NOT try to explain in so much detail that the frame becomes crowded or unreadable. "
                "Use ONLY the provided elements."
            )
            user_prompt = (
                f"Topic: {prompt.get('topic', '')}\n"
                f"Elements: {prompt.get('elements', '')}\n"
                f"{prompt.get('task', '')}"
            )
            model_with_system = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=system_prompt
            )
            response = model_with_system.generate_content(user_prompt)
            manim_code = response.text.strip()
            # Remove accidental markdown code blocks if present
            if manim_code.startswith("```python"):
                manim_code = manim_code[9:]
            if manim_code.startswith("```"):
                manim_code = manim_code[3:]
            if manim_code.endswith("```"):
                manim_code = manim_code[:-3]
            manim_code = manim_code.strip()
            # Post-process: Ask Gemini to check for overlapping elements and fix them
            post_system_instruction = (
                "You are a Manim expert and code reviewer. "
                "Given a Manim Scene code for a single-frame infographic, "
                "analyze the code for any overlapping or crowded text or elements "
                "(e.g., using coordinates in Text, Tex, or Mobject placements). "
                "If you find overlapping or crowded elements, fix the code by repositioning, resizing, "
                "or removing some information as needed, but ensure the infographic remains clear, readable, "
                "and still makes sense. "
                "If you remove information, prioritize keeping the most important key concepts. "
                "Return ONLY the fixed Python Manim code, with no explanations or markdown. "
                "The main scene class MUST always be named 'Scene'."
            )
            post_user_prompt = (
                "Here is the Manim code for a single-frame infographic. "
                "Check for overlapping or crowded elements and fix them as needed. "
                "If you must remove information, keep the most important key concepts. "
                "Return only the fixed code.\n\n" + manim_code
            )
            post_model_with_system = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=post_system_instruction
            )
            post_response = post_model_with_system.generate_content(post_user_prompt)
            fixed_code = post_response.text.strip()
            # Remove accidental markdown code blocks if present
            if fixed_code.startswith("```python"):
                fixed_code = fixed_code[9:]
            if fixed_code.startswith("```"):
                fixed_code = fixed_code[3:]
            if fixed_code.endswith("```"):
                fixed_code = fixed_code[:-3]
            fixed_code = fixed_code.strip()

            # Second post-process: Ask Gemini to check and fix Manim syntax errors
            syntax_system_instruction = (
                "You are a Manim expert and code reviewer. "
                "Given a Manim Scene code, check for any Manim syntax errors or issues. "
                "Fix all syntax errors and return ONLY the corrected Python Manim code, with no explanations or markdown. "
                "The main scene class MUST always be named 'Scene'."
            )
            syntax_user_prompt = (
                "Here is the Manim code. Check for any syntax errors and fix them. "
                "Return only the corrected code.\n\n" + fixed_code
            )
            syntax_model_with_system = genai.GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=syntax_system_instruction
            )
            syntax_response = syntax_model_with_system.generate_content(syntax_user_prompt)
            syntax_fixed_code = syntax_response.text.strip()
            # Remove accidental markdown code blocks if present
            if syntax_fixed_code.startswith("```python"):
                syntax_fixed_code = syntax_fixed_code[9:]
            if syntax_fixed_code.startswith("```"):
                syntax_fixed_code = syntax_fixed_code[3:]
            if syntax_fixed_code.endswith("```"):
                syntax_fixed_code = syntax_fixed_code[:-3]
            syntax_fixed_code = syntax_fixed_code.strip()
            return syntax_fixed_code
    # Fallback: legacy string prompt flow
    # ...existing code for legacy string prompt...
    system_prompt = (
        "You are a Manim expert who creates beautiful, informative, and highly readable single-frame infographics. "
        "You always use correct Manim Community Edition syntax and functions. "
        "You must ONLY return valid Python Manim code, with NO explanations, NO markdown, and NO ```python or ``` blocks. "
        "The main scene class MUST always be named 'Scene'. "
        "The output must be a single static frame (no animation). "
        "All information about the topic must be visible in that single frame. "
        "Text and labels must be well-placed, non-overlapping, and clearly readable. "
        "Include key concepts and explanations with clear, non-crowded diagrams. "
        "Do NOT try to explain in so much detail that the frame becomes crowded or unreadable."
    )
    user_prompt = (
        f"Create a highly informative and visually engaging single-frame infographic using Manim. "
        f"The output must be a single static frame (no animation) and all information about the topic must be visible in that frame. "
        f"Text and labels must be well-placed, non-overlapping, and clearly readable. "
        f"Include key concepts and explanations with clear, non-crowded diagrams. "
        f"Do NOT try to explain in so much detail that the frame becomes crowded or unreadable. "
        f"Topic: {prompt}"
    )
    model_with_system = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=system_prompt
    )
    response = model_with_system.generate_content(user_prompt)
    manim_code = response.text.strip()
    # Remove accidental markdown code blocks if present
    if manim_code.startswith("```python"):
        manim_code = manim_code[9:]
    if manim_code.startswith("```"):
        manim_code = manim_code[3:]
    if manim_code.endswith("```"):
        manim_code = manim_code[:-3]
    manim_code = manim_code.strip()
    # Post-process: Ask Gemini to check for overlapping elements and fix them
    post_system_instruction = (
        "You are a Manim expert and code reviewer. "
        "Given a Manim Scene code for a single-frame infographic, "
        "analyze the code for any overlapping or crowded text or elements "
        "(e.g., using coordinates in Text, Tex, or Mobject placements). "
        "If you find overlapping or crowded elements, fix the code by repositioning, resizing, "
        "or removing some information as needed, but ensure the infographic remains clear, readable, "
        "and still makes sense. "
        "If you remove information, prioritize keeping the most important key concepts. "
        "Return ONLY the fixed Python Manim code, with no explanations or markdown. "
        "The main scene class MUST always be named 'Scene'."
    )
    post_user_prompt = (
        "Here is the Manim code for a single-frame infographic. "
        "Check for overlapping or crowded elements and fix them as needed. "
        "If you must remove information, keep the most important key concepts. "
        "Return only the fixed code.\n\n" + manim_code
    )
    post_model_with_system = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=post_system_instruction
    )
    post_response = post_model_with_system.generate_content(post_user_prompt)
    fixed_code = post_response.text.strip()
    # Remove accidental markdown code blocks if present
    if fixed_code.startswith("```python"):
        fixed_code = fixed_code[9:]
    if fixed_code.startswith("```"):
        fixed_code = fixed_code[3:]
    if fixed_code.endswith("```"):
        fixed_code = fixed_code[:-3]
    fixed_code = fixed_code.strip()

    # Second post-process: Ask Gemini to check and fix Manim syntax errors
    syntax_system_instruction = (
        "You are a Manim expert and code reviewer. "
        "Given a Manim Scene code, check for any Manim syntax errors or issues. "
        "Fix all syntax errors and return ONLY the corrected Python Manim code, with no explanations or markdown. "
        "The main scene class MUST always be named 'Scene'."
    )
    syntax_user_prompt = (
        "Here is the Manim code. Check for any syntax errors and fix them. "
        "Return only the corrected code.\n\n" + fixed_code
    )
    syntax_model_with_system = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=syntax_system_instruction
    )
    syntax_response = syntax_model_with_system.generate_content(syntax_user_prompt)
    syntax_fixed_code = syntax_response.text.strip()
    # Remove accidental markdown code blocks if present
    if syntax_fixed_code.startswith("```python"):
        syntax_fixed_code = syntax_fixed_code[9:]
    if syntax_fixed_code.startswith("```"):
        syntax_fixed_code = syntax_fixed_code[3:]
    if syntax_fixed_code.endswith("```"):
        syntax_fixed_code = syntax_fixed_code[:-3]
    syntax_fixed_code = syntax_fixed_code.strip()
    return syntax_fixed_code
