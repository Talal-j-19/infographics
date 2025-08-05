#!/usr/bin/env python3
"""
Add responsive scaling to D3.js infographics to prevent viewport issues
Simple, focused solution that doesn't interfere with the main flow
"""

import re
from pathlib import Path


def add_responsive_scaling(html_file_path):
    """
    Add responsive scaling to ensure infographic fits on screen.
    Only adds viewport meta tag and responsive CSS - no complex scripts.
    """
    html_path = Path(html_file_path)
    
    if not html_path.exists():
        print(f"❌ HTML file {html_path} not found")
        return False
    
    try:
        # Read the HTML content
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already responsive
        if 'viewport' in content and 'max-width: 100%' in content:
            print("✅ Infographic is already responsive")
            return True
        
        # Add viewport meta tag if not present
        if 'viewport' not in content:
            if '<head>' in content:
                content = content.replace(
                    '<head>',
                    '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
                )
            elif '<meta charset=' in content:
                # Insert after charset meta tag
                content = re.sub(
                    r'(<meta charset="[^"]*">)',
                    r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
                    content
                )
        
        # Add responsive CSS styles - smart scaling with full content visibility
        responsive_css = """
        /* Smart responsive infographic styles */
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            box-sizing: border-box !important;
            background-color: #f5f5f5 !important;
            overflow: auto !important;
            height: auto !important;
            min-height: 100vh !important;
            max-height: none !important;
        }
        .infographic-wrapper {
            width: 100%;
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }
        svg {
            max-width: calc(100vw - 40px) !important;
            width: auto !important;
            height: auto !important;
            max-height: none !important;
            display: block !important;
            background-color: white !important;
            border: 1px solid #ddd !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        }
        /* FORCE all containers to show full content */
        *, *::before, *::after {
            max-height: none !important;
        }
        #d3-container, .infographic-container, div {
            width: 100% !important;
            height: auto !important;
            max-height: none !important;
            overflow: visible !important;
        }"""
        
        # Add the CSS to existing style section or create new one
        if '</style>' in content:
            content = content.replace('</style>', responsive_css + '\n    </style>')
        elif '<head>' in content:
            # Add new style section
            style_section = f'    <style>{responsive_css}\n    </style>\n'
            content = content.replace('</head>', style_section + '</head>')
        else:
            # Fallback: add style section before body
            style_section = f'<style>{responsive_css}\n</style>\n'
            content = style_section + content
        
        # Add simple JavaScript to ensure proper scaling after D3 renders
        responsive_js = """
        // Simple responsive scaling for D3.js infographics
        function ensureResponsiveDisplay() {
            const svg = document.querySelector('svg');
            if (!svg) return;

            // Get original dimensions
            const width = svg.getAttribute('width') || svg.viewBox?.baseVal?.width || 800;
            const height = svg.getAttribute('height') || svg.viewBox?.baseVal?.height || 600;

            // Set viewBox if not already set to ensure full content is visible
            if (!svg.getAttribute('viewBox')) {
                svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
            }

            // Ensure preserveAspectRatio for proper scaling without cutting content
            svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

            // Remove fixed width/height to allow CSS to control sizing
            svg.removeAttribute('width');
            svg.removeAttribute('height');

            // Wrap SVG in responsive container if not already wrapped
            const container = svg.parentElement;
            if (!container.classList.contains('infographic-wrapper')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'infographic-wrapper';
                svg.parentNode.insertBefore(wrapper, svg);
                wrapper.appendChild(svg);
            }

            // AGGRESSIVELY remove ALL height constraints
            document.body.style.height = 'auto';
            document.body.style.minHeight = '100vh';
            document.body.style.maxHeight = 'none';
            document.body.style.overflow = 'auto';
            document.documentElement.style.height = 'auto';
            document.documentElement.style.maxHeight = 'none';

            // Remove height constraints from ALL elements except wrapper
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                if (el.tagName !== 'SVG' && !el.classList.contains('infographic-wrapper')) {
                    el.style.maxHeight = 'none';
                    el.style.height = 'auto';
                    el.style.overflow = 'visible';
                }
            });

            console.log('✅ Smart responsive scaling applied - full content visible with proper wrapper');
        }
        
        // Apply responsive scaling after DOM loads and D3 renders
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(ensureResponsiveDisplay, 500);
            });
        } else {
            setTimeout(ensureResponsiveDisplay, 500);
        }"""
        
        # Add the JavaScript before closing body tag
        if '</body>' in content:
            script_section = f'    <script>\n        {responsive_js}\n    </script>\n'
            content = content.replace('</body>', script_section + '</body>')
        elif '</html>' in content:
            # Fallback: add before closing html tag
            script_section = f'<script>\n{responsive_js}\n</script>\n'
            content = content.replace('</html>', script_section + '</html>')
        
        # Write the updated content
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Added responsive scaling to {html_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding responsive scaling: {e}")
        return False


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add responsive scaling to D3.js infographic')
    parser.add_argument('html_file', help='Path to HTML file')
    
    args = parser.parse_args()
    
    success = add_responsive_scaling(args.html_file)
    if not success:
        exit(1)


if __name__ == '__main__':
    main()
