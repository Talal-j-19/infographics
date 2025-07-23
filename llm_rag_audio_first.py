"""
RAG-Enhanced LLM for Audio-First 3Blue1Brown Manim Code Generation
This module integrates the RAG system with the LLM to provide audio-first workflow:
1. Generate natural educational script
2. Create audio at natural speaking pace
3. Generate video code synchronized to audio timing
"""

import os
import json
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Tuple

try:
    from app.rag_system import ManimRAG
except ImportError:
    print("RAG system not available. Run setup_3b1b_rag.py first.")
    ManimRAG = None

try:
    from app.synchronized_tts import SynchronizedTTS
except ImportError:
    print("Synchronized TTS not available.")
    SynchronizedTTS = None

load_dotenv()

# API key management with automatic fallback
primary_key = os.getenv("GOOGLE_API_KEY2")
backup_key = os.getenv("GOOGLE_API_KEY")
current_api_key = primary_key

# Function to switch API keys when quota/rate limits are hit
def switch_api_key():
    """Switch between primary and backup API keys"""
    global current_api_key, primary_key, backup_key, model

    if current_api_key == primary_key and backup_key:
        print("🔄 Switching to backup API key due to rate/quota limits")
        current_api_key = backup_key
    elif current_api_key == backup_key and primary_key:
        print("🔄 Switching to primary API key due to rate/quota limits")
        current_api_key = primary_key
    else:
        print("⚠️ No alternative API key available")
        return False

    # Reconfigure with new key
    genai.configure(api_key=current_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    print(f"✅ API key switched successfully")
    return True

# Initial configuration
genai.configure(api_key=current_api_key)
model = genai.GenerativeModel("gemini-2.5-flash")


class AudioFirstRAGEnhancedManimLLM:
    """LLM enhanced with RAG for audio-first manim code generation"""
    
    def __init__(self):
        self.rag = None
        self.tts = None
        
        # Initialize RAG system
        if ManimRAG:
            try:
                self.rag = ManimRAG()
                self.rag.setup()
                print("✅ RAG system initialized")
            except Exception as e:
                print(f"⚠️ RAG system failed to initialize: {e}")
                self.rag = None
        else:
            print("⚠️ RAG system not available")
        
        # Initialize TTS system
        if SynchronizedTTS:
            try:
                self.tts = SynchronizedTTS()
                print("✅ Synchronized TTS initialized")
            except Exception as e:
                print(f"⚠️ TTS system failed to initialize: {e}")
                self.tts = None
        else:
            print("⚠️ TTS system not available")
    
    def get_relevant_examples(self, prompt: str) -> str:
        """Get relevant manim examples from RAG system"""
        if not self.rag:
            return ""
        
        try:
            # Extract key concepts from prompt for better search
            search_terms = self._extract_search_terms(prompt)
            examples = self.rag.get_relevant_examples(search_terms)
            return examples
        except Exception as e:
            print(f"Error getting examples: {e}")
            return ""
    
    def _extract_search_terms(self, prompt: str) -> str:
        """Extract key terms from prompt for RAG search"""
        # Simple keyword extraction - could be enhanced with NLP
        math_terms = [
            "vector", "matrix", "derivative", "integral", "function",
            "graph", "plot", "equation", "formula", "geometry",
            "calculus", "algebra", "trigonometry", "statistics",
            "probability", "complex", "number", "transformation"
        ]

        animation_terms = [
            "animation", "transform", "create", "write", "draw",
            "move", "rotate", "scale", "fade", "morph", "shift"
        ]

        found_terms = []
        prompt_lower = prompt.lower()

        for term in math_terms + animation_terms:
            if term in prompt_lower:
                found_terms.append(term)

        return " ".join(found_terms) if found_terms else prompt

    def _validate_manim_code(self, code: str) -> tuple[bool, str, str]:
        """Validate manim code for common syntax errors with aggressive auto-fixing"""
        errors = []

        # AGGRESSIVE AUTO-FIX: Fix common errors automatically
        original_code = code

        # Fix GRAY -> GREY
        code = code.replace("GRAY", "GREY")

        # Fix common Tex usage
        code = code.replace("Tex(", "Text(")
        code = code.replace("MathTex(", "Text(")
        code = code.replace("TexMobject(", "Text(")
        code = code.replace("TextMobject(", "Text(")

        # Fix common parameter errors by commenting them out
        code = code.replace("numbers_to_show=", "# numbers_to_show=")
        code = code.replace("include_numbers=", "# include_numbers=")
        code = code.replace("x_length=", "# x_length=")
        code = code.replace("y_length=", "# y_length=")
        code = code.replace("axis_config=", "# axis_config=")

        # Fix common method errors
        code = code.replace("add_coordinates()", "add_coordinate_labels()")
        code = code.replace(".add_coordinates(", ".add_coordinate_labels(")

        # Fix undefined variables by defining them
        if " dy" in code and "dy =" not in code:
            code = "        dy = 0.1  # Auto-defined\n" + code
        if " dx" in code and "dx =" not in code:
            code = "        dx = 0.1  # Auto-defined\n" + code
        if " dt" in code and "dt =" not in code:
            code = "        dt = 0.1  # Auto-defined\n" + code

        if code != original_code:
            print("🔧 Auto-fixed common errors in generated code")
            # Update the code for further validation
            pass

        # Check basic syntax
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")

        # Check for required imports
        if "from manimlib import *" not in code:
            errors.append("Missing required import: from manimlib import *")

        # Check for Scene class
        if "class " not in code or "(Scene)" not in code:
            errors.append("Missing Scene class definition")

        # Check for construct method
        if "def construct(self):" not in code:
            errors.append("Missing construct method")

        # Check for common 3b1b patterns
        if "FunctionGraph(" in code and "axes.get_graph(" not in code:
            errors.append("Use axes.get_graph() instead of FunctionGraph() for 3b1b manim")

        # Check for color naming issues
        if "GRAY" in code:
            errors.append("CRITICAL ERROR - Use GREY instead of GRAY in 3Blue1Brown manim")

        # Check for Tex usage (not supported in 3Blue1Brown manim) - ENHANCED
        if "Tex(" in code:
            errors.append("CRITICAL ERROR - Tex() not supported! ONLY use Text() for ALL text. Example: Text('dy/dx', font_size=72) NOT Tex('$\\\\frac{dy}{dx}$')")
        if "MathTex(" in code:
            errors.append("CRITICAL ERROR - MathTex() not supported! ONLY use Text() for ALL text. Example: Text('x² + 1', font_size=48) NOT MathTex('x^2 + 1')")
        if "TexMobject(" in code:
            errors.append("CRITICAL ERROR - TexMobject() not supported! ONLY use Text() for ALL text. Example: Text('formula', font_size=48) NOT TexMobject('formula')")
        if "TextMobject(" in code:
            errors.append("CRITICAL ERROR - TextMobject() not supported! ONLY use Text() for ALL text. Example: Text('hello', font_size=48) NOT TextMobject('hello')")

        # Check for undefined mathematical variables - NEW
        undefined_vars = ['dy', 'dx', 'dt', 'du', 'dv']
        for var in undefined_vars:
            if f" {var}" in code or f"({var}" in code or f"[{var}" in code:
                errors.append(f"CRITICAL ERROR - Variable '{var}' not defined! "
                            f"Define as: {var} = 0.1 or use Text('{var}') for display")

        # Check for unsupported parameters - NEW
        if "numbers_to_show" in code:
            errors.append("CRITICAL ERROR - 'numbers_to_show' parameter not supported! "
                        "Remove this parameter from Axes() or NumberLine()")
        if "include_numbers" in code:
            errors.append("CRITICAL ERROR - 'include_numbers' parameter not supported! "
                        "Remove this parameter from Axes() or NumberLine()")
        if "x_length" in code or "y_length" in code:
            errors.append("CRITICAL ERROR - 'x_length'/'y_length' parameters not supported! "
                        "Use width/height instead: Axes(x_range=(-3,3), y_range=(-2,2))")
        if "width=" in code and "Axes(" in code:
            errors.append("CRITICAL ERROR - 'width' parameter not supported in Axes()! "
                        "Use only x_range and y_range: Axes(x_range=(-3,3), y_range=(-2,2))")
        if "height=" in code and "Axes(" in code:
            errors.append("CRITICAL ERROR - 'height' parameter not supported in Axes()! "
                        "Use only x_range and y_range: Axes(x_range=(-3,3), y_range=(-2,2))")

        # Check for LaTeX/TeX expressions that slip through - ENHANCED
        if "\\underbrace" in code or "\\overbrace" in code:
            errors.append("CRITICAL ERROR - LaTeX braces not supported! Use Text() only")
        if "\\frac" in code or "\\sqrt" in code or "\\sum" in code:
            errors.append("CRITICAL ERROR - LaTeX math not supported! Use Text() with Unicode: Text('√x', font_size=48)")
        if "$" in code and ("Tex" in code or "Math" in code):
            errors.append("CRITICAL ERROR - LaTeX $ symbols not supported! Use Text() only")

        # Check for other unsupported Axes parameters
        if "axis_config" in code:
            errors.append("CRITICAL ERROR - 'axis_config' parameter not supported! Use simple Axes(x_range=(-3,3), y_range=(-2,2))")
        if "x_axis_config" in code or "y_axis_config" in code:
            errors.append("CRITICAL ERROR - 'x_axis_config'/'y_axis_config' not supported! Use simple Axes(x_range=(-3,3), y_range=(-2,2))")

        # Check for unsupported methods - NEW
        if "get_scene_time()" in code:
            errors.append("CRITICAL ERROR - 'get_scene_time()' method not supported! "
                        "Use self.wait() for timing instead")
        if "wait_until(" in code:
            errors.append("CRITICAL ERROR - 'wait_until()' function not supported! "
                        "Use self.wait() for timing instead")
        if "def wait_until(" in code:
            errors.append("CRITICAL ERROR - Don't define custom wait_until() function! "
                        "Use self.wait() for timing instead")
        if "add_coordinates()" in code:
            errors.append("CRITICAL ERROR - 'add_coordinates()' method not supported! "
                        "Use 'add_coordinate_labels()' instead")
        if ".add_coordinates(" in code:
            errors.append("CRITICAL ERROR - 'add_coordinates()' method not supported! "
                        "Use 'add_coordinate_labels()' instead")

        # Check for LaTeX mathematical expressions that should use Text()
        import re
        latex_patterns = [
            r'\\frac\{[^}]+\}\{[^}]+\}',  # \frac{a}{b}
            r'\$[^$]+\$',                 # $math$
            r'\\[a-zA-Z]+\{[^}]*\}',     # \command{...}
        ]

        for pattern in latex_patterns:
            if re.search(pattern, code):
                errors.append("CRITICAL ERROR - LaTeX math expressions not supported! Use simple Text() with Unicode symbols instead")

        # Check for balanced parentheses
        if code.count('(') != code.count(')'):
            errors.append("Unbalanced parentheses")

        if code.count('[') != code.count(']'):
            errors.append("Unbalanced square brackets")

        if code.count('{') != code.count('}'):
            errors.append("Unbalanced curly braces")

        # Check for common variable misuse patterns
        lines = code.split('\n')
        variables = {}  # Track variable assignments

        for i, line in enumerate(lines, 1):
            line = line.strip()

            # Track variable assignments
            if '=' in line and not line.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    assignment = parts[1].strip()

                    # Track what type of object this variable holds
                    if 'axes.i2gp(' in assignment:
                        variables[var_name] = 'point_coordinates'
                    elif 'Dot(' in assignment:
                        variables[var_name] = 'dot_object'
                    elif 'Text(' in assignment:
                        variables[var_name] = 'text_object'

            # Check for misuse in animations - CRITICAL ERROR PREVENTION
            import re

            # Check for direct coordinate animation (most common error)
            coord_animation_patterns = [
                r'FadeOut\s*\(\s*axes\.c2p\s*\(',
                r'FadeIn\s*\(\s*axes\.c2p\s*\(',
                r'ShowCreation\s*\(\s*axes\.c2p\s*\(',
                r'Write\s*\(\s*axes\.c2p\s*\('
            ]

            for pattern in coord_animation_patterns:
                if re.search(pattern, line):
                    errors.append(f"Line {i}: CRITICAL ERROR - Cannot animate coordinates directly! Use: dot = Dot(axes.c2p(x,y), color=RED); FadeOut(dot)")

            # Check for variable-based coordinate animation
            if 'FadeOut(' in line or 'FadeIn(' in line:
                fade_vars = re.findall(r'Fade(?:Out|In)\(([^,)]+)', line)
                for var in fade_vars:
                    var = var.strip()
                    if var in variables and variables[var] == 'point_coordinates':
                        errors.append(f"Line {i}: CRITICAL ERROR - Variable '{var}' contains coordinates. Create Dot object first: dot = Dot({var}, color=RED); FadeOut(dot)")

        # Check for animation density and quality (ENHANCED REQUIREMENTS)
        animation_count = 0
        animation_types = set()

        # Count different types of animations
        animation_patterns = {
            'ShowCreation': r'ShowCreation\(',
            'FadeIn': r'FadeIn\(',
            'FadeOut': r'FadeOut\(',
            'Write': r'Write\(',
            'Transform': r'Transform\(',
            'DrawBorderThenFill': r'DrawBorderThenFill\(',
            'GrowFromCenter': r'GrowFromCenter\(',
        }

        for anim_type, pattern in animation_patterns.items():
            matches = len(re.findall(pattern, code))
            if matches > 0:
                animation_count += matches
                animation_types.add(anim_type)

        # Check for mathematical visualizations
        math_viz_patterns = [
            r'axes\.get_graph\(',
            r'Dot\(',
            r'Line\(',
            r'Circle\(',
            r'Axes\(',
        ]

        math_viz_count = 0
        for pattern in math_viz_patterns:
            math_viz_count += len(re.findall(pattern, code))

        # Validation rules for animation quality
        if animation_count < 5:
            errors.append(f"ANIMATION QUALITY ERROR - Only {animation_count} animations found. Need at least 5 animations for rich mathematical content")

        if len(animation_types) < 3:
            errors.append(f"ANIMATION VARIETY ERROR - Only {len(animation_types)} animation types used. Need at least 3 different types (ShowCreation, FadeIn, Transform, etc.)")

        if math_viz_count < 3:
            errors.append(f"MATHEMATICAL VISUALIZATION ERROR - Only {math_viz_count} mathematical objects found. Need at least 3 (graphs, dots, lines, circles, axes)")

        # Check for external file dependencies (CRITICAL ERROR)
        external_file_patterns = [
            r'ImageMobject\s*\(',
            r'SVGMobject\s*\(',
            r'VideoMobject\s*\(',
            r'\.png["\']',
            r'\.jpg["\']',
            r'\.jpeg["\']',
            r'\.svg["\']',
            r'\.mp4["\']',
            r'\.avi["\']',
            r'\.gif["\']',
            r'open\s*\(',
            r'with\s+open\s*\(',
            r'imread\s*\(',
            r'load\s*\(',
        ]

        for pattern in external_file_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(f"CRITICAL ERROR - External file dependency detected! Code must be self-contained using only built-in manim objects. Pattern found: {pattern}")

        return len(errors) == 0, "; ".join(errors), code

    def _test_manim_compilation(self, code: str, script: str, total_duration: float) -> str:
        """Test manim code by importing and instantiating Scene class (NO rendering)"""
        print("🚨 DEBUG: _test_manim_compilation function called!")
        import tempfile
        import os
        import re
        import importlib.util

        try:
            # Extract scene name from code
            scene_match = re.search(r'class\s+(\w+)\s*\(Scene\)', code)
            if not scene_match:
                return "No Scene class found in code"
            scene_name = scene_match.group(1)

            # Create temporary file with the manim code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            try:
                # Mock sys.argv to prevent manimlib from parsing uvicorn arguments
                import sys
                original_argv = sys.argv.copy()
                # Use minimal valid manim arguments
                sys.argv = ['python', '-s']  # -s flag for skip_animations (no rendering)

                try:
                    # Load the generated code as a module
                    spec = importlib.util.spec_from_file_location("test_scene", temp_file_path)
                    test_module = importlib.util.module_from_spec(spec)

                    # Execute the module to define the Scene class
                    spec.loader.exec_module(test_module)
                finally:
                    # Restore original sys.argv
                    sys.argv = original_argv

                # Get the Scene class
                scene_class = getattr(test_module, scene_name)
                print(f"🔍 DEBUG: Found scene class: {scene_class}")

                # Try to instantiate the Scene class AND run construct method
                # This is where AttributeError, NameError, etc. will be caught
                print(f"🔍 DEBUG: Instantiating scene...")
                scene = scene_class()
                print(f"🔍 DEBUG: Scene instantiated successfully")

                # Actually test the construct method - this is where real errors occur
                print(f"🔍 DEBUG: Calling construct() method...")

                # In 3Blue1Brown manim, construct() just sets up the scene
                # We need to actually try to execute some of the problematic code
                scene.construct()

                # Try to force execution of any objects that were created
                # This should trigger errors like get_area(), get_riemann_rectangles(), etc.
                if hasattr(scene, 'mobjects') and scene.mobjects:
                    print(f"🔍 DEBUG: Found {len(scene.mobjects)} mobjects, testing them...")
                    for mobject in scene.mobjects:
                        # Try to access properties that might trigger errors
                        try:
                            _ = mobject.get_center()  # This should be safe
                        except:
                            pass  # Ignore safe property access errors

                print(f"🔍 DEBUG: construct() completed successfully")

                # Success - no errors during construction
                return None

            except SystemExit as e:
                # Handle SystemExit specifically (manimlib argument parsing issues)
                print(f"🔍 DEBUG: Caught SystemExit: {e}")
                return f"SystemExit: manimlib argument parsing failed - {e}"

            except Exception as e:
                # Capture the exact error that would occur during manim execution
                error_type = type(e).__name__
                error_msg = str(e)
                print(f"🔍 DEBUG: Caught {error_type}: {error_msg}")

                # Return the exact error message
                return f"{error_type}: {error_msg}"

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

        except Exception as e:
            return f"Compilation test failed: {str(e)}"

        except Exception as e:
            return f"Compilation test failed: {str(e)}"

    def _get_error_specific_rag_examples(self, errors: str) -> str:
        """Get RAG examples relevant to specific errors encountered"""
        if not self.rag:
            return ""

        # Map errors to relevant search terms with better coverage
        error_keywords = []

        # Axes-related errors (most common)
        if any(keyword in errors.lower() for keyword in ["axes", "axis", "coordinate", "x_axis", "y_axis", "numberplane"]):
            error_keywords.extend(["Axes", "NumberPlane", "coordinate system", "axes creation", "axis labels", "x_range", "y_range"])

        # Area/region errors
        if any(keyword in errors.lower() for keyword in ["get_area", "area", "region", "fill"]):
            error_keywords.extend(["area", "get_area", "region", "polygon area", "fill_opacity", "Rectangle"])

        # Riemann rectangles errors
        if any(keyword in errors.lower() for keyword in ["riemann", "rectangles", "get_riemann"]):
            error_keywords.extend(["get_riemann_rectangles", "riemann", "integration", "rectangles", "dx"])

        # Graph/function plotting errors
        if any(keyword in errors.lower() for keyword in ["graph", "plot", "function", "curve", "get_graph"]):
            error_keywords.extend(["get_graph", "ParametricFunction", "FunctionGraph", "plot", "function"])

        # Animation errors
        if any(keyword in errors.lower() for keyword in ["play", "animation", "transform", "fadein", "fadeout"]):
            error_keywords.extend(["self.play", "Transform", "FadeIn", "FadeOut", "ShowCreation", "animation"])

        # Text/label errors
        if any(keyword in errors.lower() for keyword in ["text", "label", "tex", "mathtex"]):
            error_keywords.extend(["Text", "Tex", "MathTex", "labels", "text rendering", "TextMobject"])

        # Variable/attribute errors
        if any(keyword in errors.lower() for keyword in ["nameerror", "attributeerror", "not defined", "has no attribute"]):
            error_keywords.extend(["variables", "attributes", "object properties", "manim objects", "mobject"])

        # Parameter/argument errors
        if any(keyword in errors.lower() for keyword in ["unexpected keyword", "got an unexpected", "parameter", "argument"]):
            error_keywords.extend(["parameters", "arguments", "function calls", "method signatures"])

        # Color errors
        if any(keyword in errors.lower() for keyword in ["color", "colour", "gray", "grey"]):
            error_keywords.extend(["color", "BLUE", "RED", "GREEN", "GREY", "color constants"])

        # VGroup errors
        if any(keyword in errors.lower() for keyword in ["vgroup", "group"]):
            error_keywords.extend(["VGroup", "group", "mobject group", "grouping"])

        # Get examples for the most relevant keywords
        if error_keywords:
            # Try multiple search strategies
            search_queries = [
                " ".join(error_keywords[:4]),  # Most specific
                " ".join(error_keywords[:2]),  # Broader
                error_keywords[0] if error_keywords else ""  # Fallback
            ]

            for query in search_queries:
                if not query:
                    continue
                try:
                    examples = self.get_relevant_examples(query)
                    if examples and len(examples.strip()) > 50:  # Ensure we got meaningful examples
                        return f"\n\nRELEVANT 3BLUE1BROWN EXAMPLES FOR FIXING THESE ERRORS:\n{examples}\n"
                except Exception as e:
                    print(f"⚠️ Could not fetch RAG examples for query '{query}': {e}")
                    continue

        return ""

    def _get_specific_error_fixes(self, errors: str) -> str:
        """Generate specific fix instructions for common errors"""
        fixes = []

        if "get_area" in errors.lower():
            fixes.append("• Replace get_area() with proper area calculation methods from examples")
            fixes.append("• Use Rectangle or Polygon objects for area visualization")

        if "get_riemann_rectangles" in errors.lower() and "color" in errors.lower():
            fixes.append("• Remove 'color=' parameter from get_riemann_rectangles()")
            fixes.append("• Set color using .set_color() method after creation")

        if "axes" in errors.lower() and ("x_axis" in errors.lower() or "y_axis" in errors.lower()):
            fixes.append("• Use axes.x_axis and axes.y_axis instead of axes.get_x_axis()")
            fixes.append("• Create Axes object first: axes = Axes(x_range=..., y_range=...)")

        if "attributeerror" in errors.lower() and "has no attribute" in errors.lower():
            fixes.append("• Check the 3Blue1Brown examples for correct method names")
            fixes.append("• Replace incorrect method calls with working examples from RAG")

        if "nameerror" in errors.lower():
            fixes.append("• Define all variables before using them")
            fixes.append("• Import required objects from manimlib")

        if "unexpected keyword" in errors.lower():
            fixes.append("• Remove invalid parameters from method calls")
            fixes.append("• Use only parameters shown in the 3Blue1Brown examples")

        if "indentationerror" in errors.lower():
            fixes.append("• Fix Python indentation - use 4 spaces consistently")
            fixes.append("• Ensure all code blocks are properly indented")

        if "gray" in errors.lower() or "grey" in errors.lower():
            fixes.append("• Use GREY instead of GRAY for color constants")

        if not fixes:
            fixes.append("• Follow the exact syntax patterns from the 3Blue1Brown examples above")
            fixes.append("• Replace any non-working code with working examples from RAG")

        return "\n".join(fixes)

    def generate_natural_script(self, prompt: str) -> str:
        """Generate natural educational script for the topic"""
        
        # Get relevant examples from RAG
        relevant_examples = self.get_relevant_examples(prompt)
        
        examples_section = ""
        if relevant_examples:
            examples_section = f"RELEVANT EXAMPLES FROM 3BLUE1BROWN:\n{relevant_examples}\n"

        script_prompt = f"""
You are an expert educational content creator in the style of 3Blue1Brown. Generate a natural, conversational script for explaining: {prompt}

{examples_section}

REQUIREMENTS:
- Write in a conversational, engaging tone like Grant Sanderson (3Blue1Brown)
- Use natural speech patterns with appropriate pauses
- Include mathematical concepts but explain them intuitively
- Structure content logically with smooth transitions
- Keep explanations clear and accessible
- Use analogies and visual descriptions where helpful
- Aim for 60-90 seconds of natural speaking time
- Write as if speaking directly to the viewer



OUTPUT: Return only the script text, no formatting or extra content.
"""

        # Add retry logic for script generation to handle RPM limits
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                print(f"📝 Script generation attempt {attempt + 1}/{max_attempts}")

                # Create proper system prompt structure for Gemini
                system_instructions = """You are an expert educational content creator specializing in mathematics and AI topics.
Generate clear, engaging educational scripts that explain complex concepts in an accessible way.
CRITICAL: Generate ONLY the script content without any markdown formatting, explanations, or meta-text."""

                # Configure model with system instructions
                model_with_system = genai.GenerativeModel(
                    "gemini-2.5-flash",
                    system_instruction=system_instructions
                )

                response = model_with_system.generate_content(script_prompt)
                script = response.text.strip()

                # Clean up any unwanted formatting
                script = script.replace("```", "").replace("**", "").strip()

                print(f"✅ Script generation successful on attempt {attempt + 1}")
                return script

            except Exception as e:
                error_str = str(e).lower()
                print(f"⚠️ Script generation attempt {attempt + 1} failed: {e}")

                # Check if it's a rate limit or quota error
                if "429" in error_str or "quota" in error_str or "rate" in error_str:
                    if attempt < max_attempts - 1:
                        # Try switching API key first
                        if switch_api_key():
                            print("🔄 Retrying with different API key...")
                            continue
                        else:
                            # If no API key switch possible, wait and retry
                            import time
                            wait_time = (attempt + 1) * 2  # Exponential backoff
                            print(f"🔄 Rate limit detected, waiting {wait_time}s...")
                            time.sleep(wait_time)
                            continue

                # If it's the last attempt or not a rate limit error, return fallback
                if attempt == max_attempts - 1:
                    print(f"❌ Script generation failed after {max_attempts} attempts")
                    return f"Let's explore {prompt} through visual mathematics and discover the beautiful patterns that emerge."

    def create_natural_audio(self, script: str, job_id: str) -> Tuple[str, Dict]:
        """Create audio at natural speaking pace and return timing info"""
        
        if not self.tts:
            print("⚠️ TTS system not available, skipping audio generation")
            return "", {"total_duration": 0, "segments": []}
        
        try:
            # Create audio without duration constraints for natural pacing
            audio_path = self.tts.generate_timed_audio(
                script=script,
                job_id=job_id,
                timing_info=None,
                target_duration=None  # No target - let it be natural
            )
            
            # Load timing information
            timing_file = Path(f"generated/{job_id}/audio_timing.json")
            timing_info = {"total_duration": 0, "segments": []}
            
            if timing_file.exists():
                with open(timing_file, 'r', encoding='utf-8') as f:
                    timing_info = json.load(f)
            
            return audio_path, timing_info
            
        except Exception as e:
            print(f"Error creating audio: {e}")
            return "", {"total_duration": 0, "segments": []}

    def generate_synchronized_manim_code(self, prompt: str, script: str, audio_timing: Dict) -> str:
        """Generate manim code synchronized to audio timing"""

        # Get relevant examples from RAG
        relevant_examples = self.get_relevant_examples(prompt)

        examples_section = ""
        if relevant_examples:
            examples_section = f"RELEVANT EXAMPLES FROM 3BLUE1BROWN CODEBASE:\n{relevant_examples}\n"

        # Extract timing information
        total_duration = audio_timing.get("total_duration", 60)
        segments = audio_timing.get("segments", [])

        # Create timing context for the prompt
        timing_context = f"AUDIO TIMING CONTEXT:\n"
        timing_context += f"- Total Duration: {total_duration:.2f} seconds\n"
        timing_context += f"- Number of Segments: {len(segments)}\n"

        if segments:
            timing_context += "- Segment Breakdown:\n"
            for i, segment in enumerate(segments[:5]):  # Show first 5 segments
                start_time = segment.get('start_time', 0)
                duration = segment.get('duration', 0)
                text = segment.get('text', '')[:50]
                timing_context += f"  {i+1}. {start_time:.1f}s-{start_time+duration:.1f}s: {text}...\n"

        code_prompt = f"""
🚨🚨🚨 CRITICAL: READ THESE RULES FIRST - IGNORE = CODE FAILURE 🚨🚨🚨

❌ ABSOLUTELY FORBIDDEN (WILL CAUSE ERRORS):
- Tex(), MathTex(), TexMobject(), TextMobject() → CAUSES ERRORS
- LaTeX: \\frac, \\sqrt, \\underbrace, $ symbols → CAUSES ERRORS
- Undefined: dy, dx, dt, du, dv → CAUSES "name 'dy' is not defined"
- Parameters: numbers_to_show, x_length, y_length, axis_config → CAUSES TypeError
- Methods: get_scene_time(), wait_until() → CAUSES AttributeError
- GRAY color → CAUSES NameError (use GREY)

✅ ONLY USE THESE (GUARANTEED TO WORK):
- Text("f(x) = x²", font_size=48) for ALL text
- Axes(x_range=(-3, 3, 1), y_range=(-2, 8, 1)) for graphs
- self.wait(2.5) for timing
- GREY, BLUE, RED, GREEN colors

🚨🚨🚨 FOLLOW THESE OR YOUR CODE WILL CRASH 🚨🚨🚨

You are a professional Manim animation expert using 3Blue1Brown's original manim library. Generate code synchronized to audio timing.

{timing_context}

CRITICAL SYNTAX RULES FOR 3BLUE1BROWN MANIM:

✅ DO:
   - Use Text() for ALL text display: Text("f(x) = x²", font_size=48)
   - Define variables before using: dy = 0.1, then use dy
   - Use self.wait() for timing: self.wait(2.5)
   - Use GREY (not GRAY) for colors
   - Use proper Axes syntax: Axes(x_range=(-3, 3, 1), y_range=(-2, 8, 1))
   - Use proper 3Blue1Brown objects: Arrow(), Circle(), Line(), Dot()
   - Keep all visual elements self-contained (no external files)

❌ DON'T:
   - DON'T use Tex(), MathTex(), TexMobject(), TextMobject()
   - DON'T use LaTeX expressions: \\frac, \\sqrt, \\underbrace, $ symbols
   - DON'T use undefined variables: dy, dx, dt, du, dv without defining them
   - DON'T use unsupported parameters: numbers_to_show, include_numbers, x_length, y_length, axis_config
   - DON'T use unsupported methods: get_scene_time(), wait_until(), add_coordinates()
   - DON'T use GRAY (use GREY instead)
   - DON'T use external files (SVG, images)

1. IMPORTS AND SCENE:
   - ALWAYS use: from manimlib import *
   - Scene class: class YourScene(Scene):
   - NO CONFIG dictionary needed

2. AXES AND GRAPHS:
   - Use: axes = Axes(x_range=(-3, 3, 1), y_range=(-2, 8, 1))
   - For graphs: graph = axes.get_graph(lambda x: x**2, color=BLUE)
   - NOT FunctionGraph directly
   - Use axes.i2gp(x_value, graph) for points on graph

3. COMMON OBJECTS:
   - Text: Text("Hello", font_size=36)
   - Dot: Dot(color=RED)
   - Line: Line(start=LEFT, end=RIGHT)
   - Circle: Circle(radius=1, color=BLUE)



4. ANIMATIONS:
   - ShowCreation (not Create)
   - Write (for text)
   - FadeIn, FadeOut
   - Transform (not ReplacementTransform)

4. RICH MATHEMATICAL ANIMATION REQUIREMENTS (CRITICAL):
   - MANDATORY: Include visual animation every 10-15 seconds
   - MANDATORY: Generate animations for EVERY mathematical concept mentioned in script
   - MANDATORY: Use at least 3 different animation types per major topic
   - MANDATORY: Create visual representations of all equations, functions, and formulas

   SPECIFIC ANIMATION TYPES REQUIRED:
   - Mathematical Visualizations: graphs, equations, geometric shapes
   - Dynamic Demonstrations: function plotting, transformations, calculations
   - Conceptual Illustrations: step-by-step mathematical processes
   - Visual Emphasis: highlighting key terms, zooming on important elements

   SCRIPT-SYNCHRONIZED ANIMATION RULES:
   - When script mentions "derivative" → show tangent lines, slopes, rate of change
   - When script mentions "function" → show graph plotting, domain/range
   - When script mentions "equation" → show algebraic steps, solving process
   - When script mentions "slope" → show rise/run, angle measurements
   - When script mentions "rate of change" → show dynamic changing values
   - When script mentions "graph" → show coordinate system, plotting points

5. TIMING SYNCHRONIZATION:
   - Use self.wait() to match audio timing precisely
   - Total animation time should be approximately {total_duration:.1f} seconds
   - Distribute animations throughout the ENTIRE script duration
   - NO static periods longer than 5 seconds without visual changes

{examples_section}

SCRIPT TO ANIMATE:
{script}

TASK: Generate manim code that creates rich mathematical animations synchronized to the audio timing above.

⚠️ CRITICAL DO's AND DON'Ts - FOLLOW EXACTLY ⚠️

✅ DO:
- Use Text() for ALL text: Text("f(x) = x²", font_size=48)
- Define variables before using: dy = 0.1, then use dy
- Use self.wait() for timing: self.wait(2.5)
- Use GREY (not GRAY) for colors
- Use proper objects: Axes(), Arrow(), Circle(), Line(), Dot()

❌ DON'T:
- DON'T use Tex(), MathTex(), TexMobject(), TextMobject()
- DON'T use LaTeX: \\frac, \\sqrt, \\underbrace, $ symbols
- DON'T use undefined variables: dy, dx, dt, du, dv
- DON'T use: numbers_to_show, include_numbers, x_length, y_length, axis_config parameters
- DON'T use: get_scene_time(), wait_until(), add_coordinates() methods
- DON'T use GRAY (use GREY)

ENHANCED ANIMATION REQUIREMENTS:
- Code MUST be syntactically correct for 3Blue1Brown's manim
- MANDATORY: Rich mathematical animations throughout {total_duration:.1f} seconds
- MANDATORY: Visual animation every 10-15 seconds (no long static periods)
- MANDATORY: Animate EVERY mathematical concept mentioned in the script
- MANDATORY: Use diverse animation types (graphs, transformations, highlights)

ANIMATION QUALITY STANDARDS:
- Generate proper mathematical visualizations, NOT just text displays
- Create dynamic demonstrations of mathematical concepts
- Show step-by-step mathematical processes visually
- Include smooth transitions between different concepts
- Use visual emphasis for key mathematical terms when spoken

SCRIPT SYNCHRONIZATION RULES:
- Parse script content for mathematical terms and concepts
- Generate appropriate animations for each mathematical concept
- Time animations to match when concepts are mentioned in audio
- Use appropriate wait() calls to maintain audio-visual synchronization
- Text should fade away after being spoken, not stay on screen
- Focus on visual mathematical concepts that support the narration

ANIMATION PLACEMENT STRATEGY:
- Analyze script segments for mathematical content
- Generate context-appropriate animations for each segment
- Ensure visual variety across the entire video duration
- Balance text explanations with rich mathematical visualizations

⚠️ FINAL REMINDER - CRITICAL RULES ⚠️
✅ DO: Text(), self.wait(), GREY, define variables, Axes(x_range=(-3,3), y_range=(-2,2))
❌ DON'T: Tex/MathTex, undefined dy/dx, numbers_to_show, x_length, get_scene_time()

Return ONLY the manim code without any markdown formatting or explanations.
"""

        # Try generation with validation and retry logic

        # Create CRITICAL system prompt for manim code generation
        system_instructions = """🚨 CRITICAL SYSTEM INSTRUCTIONS 🚨

You are a 3Blue1Brown manim code generator. Your code MUST work without errors.

❌ ABSOLUTELY FORBIDDEN (CAUSES ERRORS):
- Tex(), MathTex(), TexMobject(), TextMobject() → CAUSES ERRORS
- LaTeX: \\frac, \\sqrt, \\underbrace, $ symbols → CAUSES ERRORS
- Undefined: dy, dx, dt, du, dv → CAUSES "name 'dy' is not defined"
- Parameters: numbers_to_show, x_length, y_length, axis_config → CAUSES TypeError
- Methods: get_scene_time(), wait_until(), add_coordinates() → CAUSES AttributeError
- GRAY color → CAUSES NameError (use GREY)

✅ ONLY USE THESE (GUARANTEED TO WORK):
- Text("f(x) = x²", font_size=48) for ALL text
- Axes(x_range=(-3, 3, 1), y_range=(-2, 8, 1)) for graphs
- axes.add_coordinate_labels() for coordinate labels (NOT add_coordinates())
- self.wait(2.5) for timing
- GREY, BLUE, RED, GREEN colors

CRITICAL: Generate ONLY working Python code without markdown or explanations."""

        # Configure model with critical system instructions - MAINTAIN SAME CONTEXT
        model_with_system = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system_instructions
        )

        # Start chat session to maintain context
        chat_session = model_with_system.start_chat()

        # Collect ALL errors in one pass, with more attempts and RAG examples
        validation_attempts = 1
        compilation_attempts = 10  # Increased to 10 for better error fixing with RAG examples

        # Step 1: Generate initial code with minimal validation
        for attempt in range(validation_attempts):
            try:
                if attempt == 0:
                    print(f"📝 Initial code generation")
                    response = chat_session.send_message(code_prompt)
                else:
                    print(f"🔧 Code validation fix attempt {attempt + 1}")
                    fix_prompt = f"""Fix these validation errors in the code:
EXISTING CODE: {code}
ERRORS: {error_msg}
Return only the corrected code without explanations."""
                    response = chat_session.send_message(fix_prompt)

                code = response.text.strip()

                # Clean up markdown formatting
                if code.startswith("```python"):
                    code = code[9:]
                elif code.startswith("```"):
                    code = code[3:]
                if code.endswith("```"):
                    code = code[:-3]
                code = code.strip()

                # Basic validation (only critical errors)
                is_valid, error_msg, fixed_code = self._validate_manim_code(code)

                if is_valid:
                    print(f"✅ Basic validation passed")
                    code = fixed_code
                    break
                else:
                    print(f"⚠️ Basic validation failed: {error_msg}")
                    if attempt < validation_attempts - 1:
                        continue
                    else:
                        print("⚠️ Using code with validation warnings, will fix with manim errors")
                        code = fixed_code
                        break

            except Exception as e:
                print(f"❌ Error in validation attempt {attempt + 1}: {e}")
                if attempt == validation_attempts - 1:
                    print("⚠️ Validation had errors, proceeding to compilation testing")
                    code = "# Basic fallback code - will be tested with manim"
                    break

        # Step 2: Try manim compilation and fix real errors
        compilation_successful = False
        for compilation_attempt in range(compilation_attempts):
            try:
                print(f"🎬 Manim compilation attempt {compilation_attempt + 1}/{compilation_attempts}")

                # Test the code with actual manim compilation
                print(f"🔍 DEBUG: Starting compilation test for attempt {compilation_attempt + 1}")
                compilation_error = self._test_manim_compilation(code, script, total_duration)
                print(f"🔍 DEBUG: Compilation test returned: {compilation_error}")

                if compilation_error is None:
                    print(f"✅ Manim compilation successful on attempt {compilation_attempt + 1}")
                    compilation_successful = True
                    break
                else:
                    print(f"⚠️ Manim compilation failed: {compilation_error}")

                    if compilation_attempt < compilation_attempts - 1:
                        # Get relevant RAG examples for these specific errors
                        print(f"🔍 Fetching RAG examples for error fixing...")
                        error_examples = self._get_error_specific_rag_examples(compilation_error)
                        if error_examples:
                            print(f"✅ Found relevant 3Blue1Brown examples for error fixing")
                        else:
                            print(f"⚠️ No specific RAG examples found for these errors")

                        # Fix ALL manim errors at once with specific guidance
                        specific_fixes = self._get_specific_error_fixes(compilation_error)
                        fix_prompt = f"""
CRITICAL: Fix ALL these REAL manim compilation errors in the existing code.

EXISTING CODE:
```python
{code}
```

MANIM ERRORS TO FIX (Attempt {compilation_attempt + 1}/{compilation_attempts}):
{compilation_error}

{error_examples}

SPECIFIC FIXES REQUIRED:
{specific_fixes}

CRITICAL INSTRUCTIONS:
- Fix ALL the errors listed above using the exact syntax from examples
- Replace incorrect method calls with correct ones from 3Blue1Brown examples
- Use GREY instead of GRAY for colors
- Remove invalid parameters and use only those shown in examples
- Return the complete corrected code without explanations or markdown
- Address every single error mentioned above
"""
                        response = chat_session.send_message(fix_prompt)
                        code = response.text.strip()

                        # Clean up markdown formatting
                        if code.startswith("```python"):
                            code = code[9:]
                        elif code.startswith("```"):
                            code = code[3:]
                        if code.endswith("```"):
                            code = code[:-3]
                        code = code.strip()
                    else:
                        print("❌ Max compilation attempts reached, using last attempt")
                        break

            except Exception as e:
                print(f"❌ Error in compilation attempt {compilation_attempt + 1}: {e}")
                if compilation_attempt == compilation_attempts - 1:
                    break

        # Store compilation status for API server
        self._last_compilation_successful = compilation_successful

        if not compilation_successful:
            print("⚠️ Code compilation testing failed - video generation may fail")

        return code

    def _get_fallback_code(self, prompt: str) -> str:
        """Generate basic fallback manim code"""
        return f'''from manimlib import *

class AudioFirstScene(Scene):
    def construct(self):
        # Basic visualization for: {prompt}
        title = Text("{prompt}", font_size=48)
        title.to_edge(UP)

        self.play(Write(title))
        self.wait(2)

        # Simple mathematical visualization
        axes = Axes(
            x_range=(-3, 3, 1),
            y_range=(-2, 8, 1),
            height=6,
            width=8
        )

        self.play(ShowCreation(axes))
        self.wait(1)

        # Basic function
        graph = axes.get_graph(lambda x: x**2, color=BLUE)
        self.play(ShowCreation(graph))
        self.wait(2)

        self.play(FadeOut(title), FadeOut(axes), FadeOut(graph))
        self.wait(1)
'''

    def generate_audio_first_content(self, prompt: str, job_id: str) -> Dict:
        """
        Generate complete audio-first content:
        1. Natural educational script
        2. Audio at natural speaking pace
        3. Synchronized manim code
        """

        print("🎯 Audio-First Generation Pipeline")
        print("=" * 50)

        # Step 1: Generate natural educational script
        print("📝 Step 1: Generating natural educational script...")
        script = self.generate_natural_script(prompt)
        print(f"✅ Script generated ({len(script)} characters)")

        # Step 2: Create audio at natural pace
        print("🎵 Step 2: Creating audio at natural speaking pace...")
        audio_path, audio_timing = self.create_natural_audio(script, job_id)
        print(f"✅ Audio created: {audio_path}")

        natural_duration = audio_timing.get('total_duration', 0)
        segments_count = len(audio_timing.get('segments', []))
        print(f"📊 Natural duration: {natural_duration:.2f} seconds")
        print(f"📊 Audio segments: {segments_count}")

        # Step 3: Generate synchronized manim code
        print("🎬 Step 3: Generating synchronized manim code...")
        manim_code = self.generate_synchronized_manim_code(prompt, script, audio_timing)
        print(f"✅ Manim code generated ({len(manim_code)} characters)")

        # Save all outputs
        base_path = Path(f"generated/{job_id}")
        base_path.mkdir(parents=True, exist_ok=True)

        # Save script
        with open(base_path / "script.txt", "w", encoding="utf-8") as f:
            f.write(script)

        # Save manim code
        with open(base_path / "manim_code.py", "w", encoding="utf-8") as f:
            f.write(manim_code)

        # Save timing information
        with open(base_path / "generation_info.json", "w", encoding="utf-8") as f:
            json.dump({
                "prompt": prompt,
                "job_id": job_id,
                "natural_duration": natural_duration,
                "segments_count": segments_count,
                "audio_path": audio_path,
                "generation_method": "audio_first_rag_enhanced",
                "rag_enhanced": bool(self.rag),
                "tts_available": bool(self.tts)
            }, f, indent=2)

        print("💾 All files saved successfully")
        print(f"📁 Output directory: {base_path}")

        return {
            "script": script,
            "manim_code": manim_code,
            "audio_path": audio_path,
            "natural_duration": natural_duration,
            "segments": audio_timing.get('segments', []),
            "job_id": job_id,
            "rag_enhanced": bool(self.rag),
            "code_path": str(base_path / "manim_code.py"),
            "script_path": str(base_path / "script.txt"),
            "compilation_successful": getattr(self, '_last_compilation_successful', False)
        }


# Global instance to prevent multiple instance creation and RPM limit issues
_global_llm_instance = None

def _get_global_llm_instance() -> AudioFirstRAGEnhancedManimLLM:
    """Get or create the global LLM instance to prevent RPM limit issues"""
    global _global_llm_instance
    if _global_llm_instance is None:
        print("🔄 Creating global AudioFirstRAGEnhancedManimLLM instance...")
        _global_llm_instance = AudioFirstRAGEnhancedManimLLM()
        print("✅ Global instance created and ready")
    return _global_llm_instance

# Backward compatibility functions (FIXED - no longer creates multiple instances)
def generate_audio_first_content(prompt: str, job_id: str) -> Dict:
    """Backward compatible function for existing code - uses singleton instance"""
    llm = _get_global_llm_instance()
    return llm.generate_audio_first_content(prompt, job_id)


def generate_script_and_manim_code_audio_first(prompt: str, job_id: str) -> dict:
    """Alternative backward compatible function - uses singleton instance"""
    result = generate_audio_first_content(prompt, job_id)
    return {
        "script": result["script"],
        "manim_code": result["manim_code"],
        "job_id": result["job_id"],
        "audio_first": True,
        "natural_duration": result["natural_duration"]
    }


def main():
    """Test the Audio-First RAG-enhanced LLM"""
    llm = AudioFirstRAGEnhancedManimLLM()

    # Test with a simple prompt
    test_prompt = "quadratic functions and parabolas"
    test_job_id = "audio_first_test"

    print(f"Testing audio-first generation with prompt: {test_prompt}")

    try:
        result = llm.generate_audio_first_content(test_prompt, test_job_id)
        print("✅ Audio-first generation successful!")
        print(f"RAG Enhanced: {result.get('rag_enhanced', False)}")
        print(f"Natural Duration: {result['natural_duration']:.2f} seconds")
        print(f"Audio Segments: {len(result['segments'])}")
        print(f"Script length: {len(result['script'])} characters")
        print(f"Code length: {len(result['manim_code'])} characters")
        print(f"Audio path: {result['audio_path']}")
    except Exception as e:
        print(f"❌ Audio-first generation failed: {e}")


if __name__ == "__main__":
    main()
