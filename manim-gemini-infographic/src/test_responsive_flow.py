#!/usr/bin/env python3
"""
Test the complete flow with responsive scaling
"""

from job_manager import InfographicJobManager
from add_responsive_scaling import add_responsive_scaling
import shutil

def test_responsive_flow():
    """Test that responsive scaling works in the complete flow"""
    
    # Create a test job
    job_manager = InfographicJobManager()
    job_id, job_dir = job_manager.create_new_job("test_responsive_flow")
    file_paths = job_manager.get_file_paths()
    
    print(f"Created test job: {job_id}")
    
    # Copy an existing HTML file for testing
    existing_html = "generated/1754314349_2b35919e_test_svg_export/infographic.html"
    test_html = str(file_paths['html'])
    
    try:
        shutil.copy(existing_html, test_html)
        print(f"Copied HTML to: {test_html}")
        
        # Test responsive scaling
        result = add_responsive_scaling(test_html)
        if result:
            print("✅ Responsive scaling added successfully")
            
            # Check if the file contains responsive elements
            with open(test_html, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = [
                ('viewport meta tag', 'viewport' in content),
                ('responsive CSS', 'max-width: 100%' in content),
                ('responsive JS', 'ensureResponsiveDisplay' in content),
                ('preserveAspectRatio', 'preserveAspectRatio' in content)
            ]
            
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"{status} {check_name}: {'PASS' if passed else 'FAIL'}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print("🎉 All responsive features are working!")
                
                # Open in browser for visual verification
                import webbrowser
                webbrowser.open(f'file://{file_paths["html"].absolute()}')
                print(f"🌐 Opened in browser: {file_paths['html']}")
                
                return True
            else:
                print("❌ Some responsive features are missing")
                return False
        else:
            print("❌ Failed to add responsive scaling")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_responsive_flow()
    if success:
        print("\n✅ Responsive flow test PASSED")
    else:
        print("\n❌ Responsive flow test FAILED")
        exit(1)
