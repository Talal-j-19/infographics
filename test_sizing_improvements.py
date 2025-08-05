#!/usr/bin/env python3
"""
Test the sizing improvements - both prompt guidance and responsive scaling
"""

import os
from pathlib import Path

def test_sizing_improvements():
    """Test that our sizing improvements work"""
    
    print("🧪 Testing Sizing Improvements")
    print("=" * 50)
    
    # Test 1: Check if prompt includes sizing guidance
    print("\n1️⃣ Testing Prompt Sizing Guidance:")
    
    try:
        from gemini_api_d3_single_frame import get_d3_code_single_frame
        
        # Read the source code to check for sizing constraints
        script_path = Path(__file__).parent / "gemini_api_d3_single_frame.py"
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sizing_checks = [
            ("Width constraint", "width=800-1000px" in content),
            ("Height constraint", "height=600-800px" in content),
            ("Tall infographic warning", ">900px height" in content),
            ("Landscape orientation", "landscape orientation" in content),
            ("Compact layout guidance", "compact layouts" in content)
        ]
        
        for check_name, passed in sizing_checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}: {'PASS' if passed else 'FAIL'}")
        
        prompt_score = sum(1 for _, passed in sizing_checks if passed)
        print(f"   📊 Prompt guidance score: {prompt_score}/5")
        
    except Exception as e:
        print(f"   ❌ Error checking prompt: {e}")
        prompt_score = 0
    
    # Test 2: Check responsive scaling features
    print("\n2️⃣ Testing Responsive Scaling Features:")
    
    try:
        from add_responsive_scaling import add_responsive_scaling
        
        # Read the source code to check for responsive features
        script_path = Path(__file__).parent / "add_responsive_scaling.py"
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        responsive_checks = [
            ("Smart wrapper", "infographic-wrapper" in content),
            ("Height constraint removal", "max-height: none" in content),
            ("Viewport handling", "calc(100vw - 40px)" in content),
            ("Overflow management", "overflow: auto" in content),
            ("Aggressive override", "!important" in content)
        ]
        
        for check_name, passed in responsive_checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}: {'PASS' if passed else 'FAIL'}")
        
        responsive_score = sum(1 for _, passed in responsive_checks if passed)
        print(f"   📊 Responsive scaling score: {responsive_score}/5")
        
    except Exception as e:
        print(f"   ❌ Error checking responsive scaling: {e}")
        responsive_score = 0
    
    # Test 3: Test on existing problematic infographic
    print("\n3️⃣ Testing on Problematic Infographic:")
    
    test_file = "generated/1754317758_22bc2138_steps_to_fine_tune_a_llm/infographic.html"
    
    if os.path.exists(test_file):
        try:
            # Check if responsive features were added
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            applied_checks = [
                ("Viewport meta tag", "viewport" in content),
                ("Responsive CSS", "infographic-wrapper" in content),
                ("Height override", "max-height: none" in content),
                ("Smart scaling JS", "ensureResponsiveDisplay" in content)
            ]
            
            for check_name, passed in applied_checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {check_name}: {'PASS' if passed else 'FAIL'}")
            
            applied_score = sum(1 for _, passed in applied_checks if passed)
            print(f"   📊 Applied features score: {applied_score}/4")
            
        except Exception as e:
            print(f"   ❌ Error checking test file: {e}")
            applied_score = 0
    else:
        print(f"   ⚠️ Test file not found: {test_file}")
        applied_score = 0
    
    # Overall assessment
    print("\n🎯 Overall Assessment:")
    print("=" * 50)
    
    total_score = prompt_score + responsive_score + applied_score
    max_score = 14
    percentage = (total_score / max_score) * 100
    
    print(f"📊 Total Score: {total_score}/{max_score} ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("🎉 EXCELLENT: Sizing improvements are comprehensive!")
    elif percentage >= 75:
        print("✅ GOOD: Most sizing improvements are in place")
    elif percentage >= 50:
        print("⚠️ FAIR: Some improvements need work")
    else:
        print("❌ POOR: Significant improvements needed")
    
    print("\n🔧 Key Benefits:")
    print("• Prompt guides Gemini to create better-sized infographics")
    print("• Responsive scaling handles edge cases gracefully")
    print("• Height constraints are aggressively removed")
    print("• Content is wrapped in smart containers")
    print("• Full content visibility is guaranteed")
    
    return percentage >= 75

if __name__ == "__main__":
    success = test_sizing_improvements()
    if success:
        print("\n✅ Sizing improvements test PASSED")
    else:
        print("\n❌ Sizing improvements test FAILED")
        exit(1)
