#!/usr/bin/env python3
"""
Create Visual PDF with Actual Flowchart Graph
- Use browser's print-to-PDF to capture the visual flowchart
- Much simpler than trying to convert programmatically
"""

import os
import subprocess
import shutil

def create_visual_pdf_with_browser():
    """Create PDF using browser's print functionality"""
    
    print("🎯 Creating PDF with actual visual flowchart...")
    print("\n💡 BEST APPROACH: Use browser's Print to PDF")
    print("   This captures the full visual flowchart perfectly!")
    
    html_file = os.path.abspath('Docs/Flowchart/HTML/AndyLibrary_Fixed_Registration_Process.html')
    pdf_output = os.path.abspath('Docs/Flowchart/PDF/AndyLibrary_Visual_Flowchart.pdf')
    
    print(f"\n📄 HTML Source: {html_file}")
    print(f"📁 PDF Output: {pdf_output}")
    
    # Try different browser commands
    browsers = [
        ['google-chrome', '--headless', '--disable-gpu', '--no-sandbox', '--print-to-pdf-no-header', '--print-to-pdf', '--virtual-time-budget=30000'],
        ['chromium-browser', '--headless', '--disable-gpu', '--no-sandbox', '--print-to-pdf-no-header', '--print-to-pdf', '--virtual-time-budget=30000'],
        ['firefox', '--headless', '--print-to-pdf']
    ]
    
    for browser_cmd in browsers:
        browser_name = browser_cmd[0]
        if shutil.which(browser_name):
            print(f"\n🌐 Found {browser_name}, attempting PDF generation...")
            try:
                cmd = browser_cmd + [f'file://{html_file}']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                # Chrome creates output.pdf in current directory
                if os.path.exists('output.pdf'):
                    os.rename('output.pdf', pdf_output)
                    print(f"✅ Visual PDF created: {pdf_output}")
                    return pdf_output
                elif result.returncode == 0:
                    print(f"✅ {browser_name} completed successfully")
                    return "browser_success"
                else:
                    print(f"❌ {browser_name} failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                print(f"⏰ {browser_name} timed out")
            except Exception as e:
                print(f"❌ {browser_name} error: {e}")
        else:
            print(f"❌ {browser_name} not found")
    
    return None

def create_manual_instructions():
    """Create instructions for manual PDF creation"""
    
    instructions = '''
# Manual PDF Creation Instructions

Since automated browser PDF generation may not work on all systems, 
here's how to create the visual flowchart PDF manually:

## Method 1: Chrome/Chromium (Recommended)
1. Open Chrome or Chromium browser
2. Navigate to: file:///home/herb/Desktop/AndyLibrary/Docs/Flowchart/HTML/AndyLibrary_Fixed_Registration_Process.html
3. Wait for the flowchart to fully render (2-3 seconds)
4. Press Ctrl+P (Print)
5. Choose "Save as PDF" as destination
6. Set layout to "Landscape" for better fit
7. Click "More settings"
8. Enable "Background graphics" 
9. Set margins to "Minimum"
10. Save as: AndyLibrary_Visual_Flowchart.pdf

## Method 2: Firefox
1. Open Firefox browser
2. Navigate to the same HTML file
3. Press Ctrl+P (Print)
4. Choose "Save to PDF"
5. Set orientation to "Landscape"
6. Save the PDF

## Method 3: Edge/Safari
Similar process - Print > Save as PDF with landscape orientation

## Why This Works Better:
- ✅ Captures the actual visual flowchart with all colors and shapes
- ✅ Includes all interactive elements as they appear
- ✅ Perfect text rendering with no visibility issues
- ✅ Proper layout and scaling
- ✅ All browsers handle Mermaid rendering correctly

The resulting PDF will have:
- Full visual flowchart with proper shapes and colors
- All text clearly visible
- Professional layout suitable for presentations
- Built-in PDF viewer zoom/navigation capabilities
'''
    
    instructions_file = 'Docs/Flowchart/PDF/MANUAL_PDF_CREATION.md'
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"📋 Manual instructions created: {instructions_file}")
    return instructions_file

def main():
    print("🎯 Creating Visual PDF with Actual Flowchart")
    print("=" * 50)
    
    # Ensure PDF directory exists
    os.makedirs('Docs/Flowchart/PDF', exist_ok=True)
    
    # Try automated PDF creation
    result = create_visual_pdf_with_browser()
    
    if result and os.path.exists(result):
        print(f"\n✅ SUCCESS! Visual PDF created: {result}")
        print("🎉 The PDF contains the actual flowchart graph!")
    else:
        print("\n⚠️ Automated PDF creation didn't work on this system")
        print("📋 Creating manual instructions instead...")
        
        instructions_file = create_manual_instructions()
        
        print(f"\n📄 Instructions created: {instructions_file}")
        print("\n🎯 RECOMMENDED ACTION:")
        print("1. Open your browser")
        print("2. Load: Docs/Flowchart/HTML/AndyLibrary_Fixed_Registration_Process.html")
        print("3. Press Ctrl+P → Save as PDF → Set to Landscape")
        print("4. This gives you the ACTUAL visual flowchart in PDF format!")
        
        print("\n💡 Why manual is better:")
        print("   • ✅ Perfect visual rendering of the flowchart")
        print("   • ✅ All colors, shapes, and connections visible") 
        print("   • ✅ No compatibility issues")
        print("   • ✅ Works with any browser")
        print("   • ✅ Professional presentation quality")

if __name__ == "__main__":
    main()