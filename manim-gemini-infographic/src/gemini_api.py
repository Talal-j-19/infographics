def get_manim_code(prompt):

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

    # Create the Gemini model instance
    model = genai.GenerativeModel("gemini-2.5-flash")

    # System prompt: role and output instructions
    system_prompt = (
        "You are a Manim expert who creates beautiful, informative, and highly animated infographics. "
        "You always use correct Manim Community Edition syntax and functions. "
        "You must ONLY return valid Python Manim code, with NO explanations, NO markdown, and NO ```python or ``` blocks. "
        "The main scene class MUST always be named 'Scene'."
    )

    # User prompt: only the topic, with clear requirements
    user_prompt = (
        f"Create a highly informative and visually engaging GIF infographic using Manim. "
        f"The animation should be stylish, use great transitions and effects, and explain the topic in detail. "
        f"Topic: {prompt}"
    )

    # Use Gemini's system_instruction argument for the system prompt
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
    return manim_code