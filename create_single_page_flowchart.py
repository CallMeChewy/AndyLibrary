#!/usr/bin/env python3
"""
Create Single-Page Flowchart HTML for Perfect PDF Export
- Forces everything onto one continuous page
- No page breaks - complete map view
- Optimized for PDF navigation like a map
"""

def create_single_page_html():
    """Create HTML optimized for single-page PDF export"""
    
    # Read the current Mermaid source
    with open('Docs/Flowchart/Mermaid/AndyLibrary_Fixed_Registration_Process.mmd', 'r') as f:
        mermaid_code = f.read()
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AndyLibrary Registration Process - Single Page Map</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        /* FORCE SINGLE PAGE LAYOUT - NO PAGE BREAKS */
        * {{
            page-break-inside: avoid !important;
            page-break-before: avoid !important;
            page-break-after: avoid !important;
            break-inside: avoid !important;
        }}
        
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: 'Arial', sans-serif;
            background: #ffffff;
        }}
        
        .page-container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: #ffffff;
            page-break-inside: avoid !important;
        }}
        
        .header {{
            flex-shrink: 0;
            text-align: center;
            padding: 10px;
            background: #ffffff;
            border-bottom: 2px solid #667eea;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 24px;
            margin: 0 0 5px 0;
            font-weight: 700;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 14px;
            margin: 0;
            font-weight: 600;
        }}
        
        .flowchart-container {{
            flex: 1;
            width: 100%;
            height: calc(100vh - 80px);
            background: #ffffff;
            overflow: visible;
            position: relative;
            page-break-inside: avoid !important;
        }}
        
        .mermaid {{
            width: 100%;
            height: 100%;
            background: #ffffff !important;
            font-family: 'Arial', sans-serif !important;
            page-break-inside: avoid !important;
        }}
        
        .mermaid svg {{
            width: 100% !important;
            height: 100% !important;
            max-width: none !important;
            max-height: none !important;
            background: #ffffff !important;
            font-family: 'Arial', sans-serif !important;
            font-weight: bold !important;
        }}
        
        /* Enhanced text visibility */
        .mermaid .node text,
        .mermaid .edgeLabel text,
        .mermaid tspan {{
            font-family: 'Arial', sans-serif !important;
            font-size: 11px !important;
            font-weight: 800 !important;
            fill: #000000 !important;
            stroke: none !important;
        }}
        
        .mermaid .edgeLabel rect {{
            fill: #ffffff !important;
            stroke: #333333 !important;
            stroke-width: 1px !important;
            opacity: 1.0 !important;
        }}
        
        /* PRINT STYLES - CRITICAL FOR PDF */
        @media print {{
            * {{
                page-break-inside: avoid !important;
                page-break-before: avoid !important;
                page-break-after: avoid !important;
                break-inside: avoid !important;
            }}
            
            html, body {{
                width: 100%;
                height: 100%;
                margin: 0;
                padding: 0;
                overflow: visible;
                background: #ffffff;
            }}
            
            .page-container {{
                width: 100%;
                height: 100%;
                page-break-inside: avoid !important;
                display: block;
            }}
            
            .header {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 60px;
                z-index: 1000;
                background: #ffffff;
            }}
            
            .flowchart-container {{
                margin-top: 60px;
                width: 100%;
                height: calc(100% - 60px);
                page-break-inside: avoid !important;
                overflow: visible;
            }}
            
            .mermaid {{
                width: 100%;
                height: 100%;
                page-break-inside: avoid !important;
                transform: scale(0.85);
                transform-origin: top left;
            }}
            
            .mermaid svg {{
                width: 100% !important;
                height: 100% !important;
                background: #ffffff !important;
            }}
            
            /* Hide any potential page break elements */
            .page-break, .page-separator, .break {{
                display: none !important;
            }}
        }}
        
        /* Additional single-page enforcement */
        .no-break {{
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }}
    </style>
</head>
<body class="no-break">
    <div class="page-container no-break">
        <div class="header">
            <h1>🏛️ AndyLibrary Registration Process Map</h1>
            <p>Complete Flow • Single-Page Navigation • PDF-Optimized</p>
        </div>
        
        <div class="flowchart-container no-break">
            <div class="mermaid no-break" id="mermaidDiagram">
{mermaid_code}
            </div>
        </div>
    </div>

    <script>
        // Initialize Mermaid for single-page rendering
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis',
                padding: 15
            }},
            themeVariables: {{
                primaryColor: '#f3e5f5',
                primaryTextColor: '#000000',
                primaryBorderColor: '#4a148c',
                lineColor: '#333333',
                sectionBkgColor: '#ffffff',
                altSectionBkgColor: '#f8f9fa',
                gridColor: '#e1e1e1',
                secondaryColor: '#fff3e0',
                tertiaryColor: '#e1f5fe',
                fontSize: '11px',
                fontFamily: 'Arial, sans-serif',
                background: '#ffffff'
            }}
        }});
        
        // Ensure single-page layout after rendering
        setTimeout(() => {{
            const mermaidDiv = document.getElementById('mermaidDiagram');
            const svg = mermaidDiv.querySelector('svg');
            if (svg) {{
                svg.style.background = '#ffffff';
                svg.style.width = '100%';
                svg.style.height = '100%';
                
                // Force single-page attributes
                svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
                
                // Ensure no page breaks
                mermaidDiv.style.pageBreakInside = 'avoid';
                mermaidDiv.style.breakInside = 'avoid';
            }}
        }}, 2000);
    </script>
</body>
</html>'''
    
    return html_content

def create_pdf_instructions():
    """Create updated instructions for single-page PDF creation"""
    
    instructions = '''# Single-Page PDF Creation - NO PAGE BREAKS

## CRITICAL: Special Print Settings for Map-Like Navigation

### Step 1: Open the Single-Page HTML
File: `Docs/Flowchart/HTML/AndyLibrary_Single_Page_Map.html`

### Step 2: Browser Print Settings (IMPORTANT)

#### Chrome/Chromium (Recommended):
1. Press Ctrl+P (Print)
2. Destination: "Save as PDF"
3. **Layout: "Landscape"** ← CRITICAL
4. **Paper size: "A3" or "Tabloid"** ← LARGER SIZE PREVENTS BREAKS
5. **Margins: "None" or "Minimum"** ← CRITICAL
6. **Scale: "Custom" → "Fit to page width"** ← CRITICAL
7. **More settings:**
   - ✅ **Background graphics: ENABLED**
   - ✅ **Headers/footers: DISABLED**
8. **Save as: "AndyLibrary_Single_Page_Map.pdf"**

#### Alternative - Custom Paper Size:
1. In Chrome print dialog
2. More settings → Paper size → "Custom"
3. Width: 17 inches, Height: 22 inches
4. This creates a large single-page canvas

### Step 3: Verify Single-Page Result
- ✅ Should be ONE continuous page
- ✅ No breaks in the flowchart
- ✅ Can zoom and pan like a map
- ✅ All connections visible

## Why This Works:
- **Larger paper size** prevents automatic page breaks
- **Landscape orientation** fits the wide flowchart
- **Scale to fit** ensures everything stays on one page
- **No margins** maximizes space usage

## Result:
Perfect single-page flowchart PDF that you can navigate like a map with:
- Zoom in/out for detail
- Pan around to see different sections
- No annoying page breaks interrupting the flow
- Professional presentation quality

## If Still Getting Page Breaks:
Try even larger custom paper size:
- Width: 24 inches
- Height: 36 inches
- This forces everything onto one canvas
'''
    
    return instructions

def main():
    print("🗺️ Creating Single-Page Flowchart Map...")
    print("=" * 50)
    
    # Create the single-page optimized HTML
    html_content = create_single_page_html()
    
    # Save to organized directory
    html_output = 'Docs/Flowchart/HTML/AndyLibrary_Single_Page_Map.html'
    with open(html_output, 'w') as f:
        f.write(html_content)
    
    # Create updated PDF instructions
    instructions = create_pdf_instructions()
    instructions_file = 'Docs/Flowchart/PDF/SINGLE_PAGE_PDF_INSTRUCTIONS.md'
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"✅ Single-page HTML created: {html_output}")
    print(f"📋 Instructions created: {instructions_file}")
    
    print(f"\n🗺️ SOLUTION FOR MAP-LIKE NAVIGATION:")
    print(f"1. Open: {html_output}")
    print(f"2. Print → Landscape → A3/Tabloid size → Scale to fit")
    print(f"3. Result: ONE continuous page - no breaks!")
    
    print(f"\n🎯 KEY SETTINGS:")
    print(f"   • Paper size: A3 or Tabloid (larger prevents breaks)")
    print(f"   • Layout: Landscape")
    print(f"   • Scale: Fit to page width")
    print(f"   • Margins: None/Minimum")
    
    print(f"\n✅ This gives you exactly what you want:")
    print(f"   • Single continuous flowchart page")
    print(f"   • Navigate like a map (zoom/pan)")
    print(f"   • No interrupting page breaks")
    print(f"   • Perfect for presentations")

if __name__ == "__main__":
    main()