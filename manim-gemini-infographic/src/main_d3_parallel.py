#!/usr/bin/env python3
"""
Main script for generating multiple parallel D3.js infographics using multithreading
Creates 3 unique variants of the same topic simultaneously
"""

import sys
import json
import traceback
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def generate_single_variant(topic, variant_id, variant_manager, style_variant=None):
    """
    Generate a single infographic variant
    
    Args:
        topic: The topic for the infographic
        variant_id: Unique identifier for this variant (0, 1, 2)
        variant_manager: Job manager instance for this variant
        style_variant: Optional style override
    
    Returns:
        dict: Result information for this variant
    """
    try:
        print(f"🎨 [Variant {variant_id+1}] Starting generation...")
        
        # Import here to avoid circular imports in threading
        from gemini_api_d3_single_frame import get_d3_code_single_frame
        from gemini_api_d3_parallel import get_d3_code_parallel_variant
        from add_responsive_scaling import add_responsive_scaling
        from save_infographic_as_png import save_infographic_as_png
        from save_infographic_as_svg import save_infographic_as_svg
        import json

        # Get file paths for this variant
        file_paths = variant_manager.get_file_paths()
        code_file = str(file_paths['html'])

        # Step 1: Get elements for each variant with simple variation instruction
        print(f"🔍 [Variant {variant_id+1}] Getting elements from Gemini API...")

        elements_prompt = {
            "topic": topic,
            "task": f"List the key visual/text elements needed to make a single-frame D3.js infographic for this topic. Create a unique and creative approach - make this infographic different from typical ones. Variant {variant_id+1} of 3 - be creative and original. Return as a JSON list of element descriptions. Do not include code or explanations."
        }
        elements_response = get_d3_code_single_frame(elements_prompt)
        try:
            elements_list = json.loads(elements_response)
            if not isinstance(elements_list, list):
                raise ValueError("LLM did not return a JSON list.")
            elements = elements_response  # Keep the raw response for the next step
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ [Variant {variant_id+1}] Could not parse elements as JSON: {e}")
            elements = elements_response  # Use raw response as fallback
        
        # Step 2: Generate D3.js code with simple variation instruction
        print(f"⚙️ [Variant {variant_id+1}] Generating D3.js code...")
        code_prompt_obj = {
            "task": f"Generate D3.js code for the given elements. Create a unique and creative infographic - make this different from typical approaches. This is variant {variant_id+1} of 3, so be original and creative.",
            "topic": topic,
            "elements": elements
        }
        d3_code = get_d3_code_parallel_variant(code_prompt_obj, variant_id, style_variant)
        
        # Step 3: Save HTML file
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(d3_code)
        print(f"💾 [Variant {variant_id+1}] Generated D3.js code saved to: {code_file}")
        
        # Step 4: Add responsive scaling
        try:
            add_responsive_scaling(code_file)
            print(f"📱 [Variant {variant_id+1}] Added responsive scaling")
        except Exception as e:
            print(f"⚠️ [Variant {variant_id+1}] Could not add responsive scaling: {e}")
        
        # Step 5: Export PNG
        try:
            print(f"🖼️ [Variant {variant_id+1}] Exporting PNG...")
            png_path = save_infographic_as_png(code_file, str(file_paths['png']))
            print(f"✅ [Variant {variant_id+1}] PNG saved to: {png_path}")
        except Exception as e:
            print(f"❌ [Variant {variant_id+1}] PNG export failed: {e}")
            png_path = None
        
        # Step 6: Export SVG
        try:
            print(f"🎨 [Variant {variant_id+1}] Exporting SVG...")
            svg_path = save_infographic_as_svg(code_file, str(file_paths['svg']))
            print(f"✅ [Variant {variant_id+1}] SVG saved to: {svg_path}")
        except Exception as e:
            print(f"❌ [Variant {variant_id+1}] SVG export failed: {e}")
            svg_path = None
        
        # Step 7: Save job info
        variant_manager.save_job_info(topic, len(elements.split('\n')) if elements else 0)
        
        print(f"🎉 [Variant {variant_id+1}] Generation completed successfully!")
        
        return {
            'variant_id': variant_id,
            'success': True,
            'html_path': code_file,
            'png_path': png_path,
            'svg_path': svg_path,
            'job_dir': variant_manager.current_job_dir
        }
        
    except Exception as e:
        print(f"💥 [Variant {variant_id+1}] Generation failed: {e}")
        traceback.print_exc()
        return {
            'variant_id': variant_id,
            'success': False,
            'error': str(e),
            'job_dir': variant_manager.current_job_dir if variant_manager else None
        }


def main():
    """Main function for parallel infographic generation"""
    try:
        # Get user input
        topic = input("Enter your topic for parallel D3.js infographics (3 variants): ")
        print("You can optionally enter advanced options as JSON (or just press Enter to skip):")
        options_input = input("Advanced options (JSON): ")
        options = {}
        if options_input.strip():
            try:
                options = json.loads(options_input)
            except Exception as e:
                print(f"[WARN] Could not parse JSON, ignoring advanced options: {e}")
                options = {}
        
        # Import job manager
        from job_manager_parallel import ParallelInfographicJobManager
        
        # Create batch job
        print(f"\n🚀 Starting parallel generation for topic: '{topic}'")
        job_manager = ParallelInfographicJobManager()
        batch_id, batch_dir, variant_managers = job_manager.create_batch_job(topic)
        
        # Define simple style variants - let LLM be creative
        style_variants = [
            "creative and unique design approach",
            "innovative visualization style",
            "original and distinctive layout"
        ]
        
        # Start parallel generation
        print(f"\n⚡ Generating {len(variant_managers)} variants in parallel...")
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel generation
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all variant generation tasks
            future_to_variant = {
                executor.submit(
                    generate_single_variant, 
                    topic, 
                    i, 
                    variant_managers[i], 
                    style_variants[i]
                ): i for i in range(len(variant_managers))
            }
            
            # Collect results as they complete
            results = []
            for future in as_completed(future_to_variant):
                variant_id = future_to_variant[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"💥 Variant {variant_id+1} failed with exception: {e}")
                    results.append({
                        'variant_id': variant_id,
                        'success': False,
                        'error': str(e)
                    })
        
        # Calculate total time
        total_time = time.time() - start_time
        
        # Display results
        print(f"\n🎯 Parallel Generation Complete!")
        print(f"⏱️ Total time: {total_time:.2f} seconds")
        print(f"📁 Batch directory: {batch_dir}")
        print("=" * 60)
        
        successful_variants = [r for r in results if r['success']]
        failed_variants = [r for r in results if not r['success']]
        
        print(f"✅ Successful variants: {len(successful_variants)}/{len(results)}")
        
        for result in successful_variants:
            variant_num = result['variant_id'] + 1
            print(f"   🎨 Variant {variant_num}: {result['job_dir']}")
        
        if failed_variants:
            print(f"❌ Failed variants: {len(failed_variants)}")
            for result in failed_variants:
                variant_num = result['variant_id'] + 1
                print(f"   💥 Variant {variant_num}: {result.get('error', 'Unknown error')}")
        
        # Open successful variants in browser
        if successful_variants:
            print(f"\n🌐 Opening successful variants in browser...")
            import webbrowser
            for result in successful_variants:
                if result.get('html_path'):
                    abs_path = Path(result['html_path']).absolute()
                    webbrowser.open(f"file://{abs_path}")
                    time.sleep(1)  # Small delay between browser opens
        
        print(f"\n🎉 Parallel infographic generation completed!")
        print(f"📊 Success rate: {len(successful_variants)}/{len(results)} variants")
        
    except KeyboardInterrupt:
        print("\n⚠️ Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error in main: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
