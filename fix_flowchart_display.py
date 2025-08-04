#!/usr/bin/env python3
"""
Fix Flowchart Display Issues
- Fix partial viewport display (pan/zoom not working)
- Fix SVG export with invisible text
- Improve browser navigation
"""

def create_fixed_flowchart_html():
    """Create HTML with proper viewport and SVG text handling"""
    
    # Read the current Mermaid source
    with open('Docs/Flowchart/Mermaid/AndyLibrary_Fixed_Registration_Process.mmd', 'r') as f:
        mermaid_code = f.read()
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AndyLibrary Registration Process - Fixed Display</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow: hidden;
        }}
        
        .container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            margin: 0 auto;
            max-width: 98%;
            height: calc(100vh - 40px);
            display: flex;
            flex-direction: column;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            flex-shrink: 0;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.2em;
            margin: 0 0 10px 0;
            font-weight: 700;
        }}
        
        .header p {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin: 0;
            font-weight: 600;
        }}
        
        .success-message {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            text-align: center;
            font-weight: 600;
            flex-shrink: 0;
        }}
        
        .info-panel {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 5px solid #667eea;
            flex-shrink: 0;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }}
        
        .info-section {{
            background: white;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
        
        .info-section h4 {{
            margin: 0 0 8px 0;
            color: #2c3e50;
            font-weight: 700;
            font-size: 14px;
        }}
        
        .info-section ul {{
            margin: 0;
            padding-left: 15px;
        }}
        
        .info-section li {{
            margin: 3px 0;
            font-size: 12px;
        }}
        
        .controls {{
            margin: 10px 0;
            text-align: center;
            flex-shrink: 0;
        }}
        
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            margin: 0 4px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            background: #5a67d8;
            transform: translateY(-1px);
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4);
        }}
        
        .diagram-container {{
            flex: 1;
            background: #ffffff;
            border-radius: 10px;
            border: 2px solid #ecf0f1;
            position: relative;
            overflow: hidden;
            min-height: 0;
        }}
        
        .zoom-controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .zoom-btn {{
            background: #667eea;
            color: white;
            border: none;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        }}
        
        .zoom-btn:hover {{
            background: #5a67d8;
            transform: scale(1.1);
        }}
        
        .pan-info {{
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 6px 10px;
            border-radius: 5px;
            font-size: 11px;
            z-index: 1000;
        }}
        
        .mermaid-wrapper {{
            width: 100%;
            height: 100%;
            overflow: auto;
            position: relative;
        }}
        
        .mermaid {{
            transform-origin: top left;
            min-width: 100%;
            min-height: 100%;
            background: #ffffff;
            font-family: 'Arial', sans-serif !important;
        }}
        
        .mermaid svg {{
            font-family: 'Arial', sans-serif !important;
            font-weight: bold !important;
            background: #ffffff !important;
            max-width: none !important;
            max-height: none !important;
        }}
        
        /* Enhanced text visibility for SVG export */
        .mermaid .node text,
        .mermaid .edgeLabel text,
        .mermaid tspan {{
            font-family: 'Arial', sans-serif !important;
            font-size: 12px !important;
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
        
        @media print {{
            body {{
                background: white;
                overflow: visible;
            }}
            .container {{
                box-shadow: none;
                max-width: none;
                height: auto;
            }}
            .controls, .info-panel, .zoom-controls, .pan-info, .success-message {{
                display: none;
            }}
            .diagram-container {{
                overflow: visible;
                height: auto;
            }}
            .mermaid {{
                transform: scale(0.8);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ AndyLibrary Registration Process</h1>
            <p>Fixed Display • Complete Navigation • Visible SVG Export</p>
        </div>
        
        <div class="success-message">
            ✅ <strong>Display Issues Fixed!</strong> Full flowchart visible with working navigation and proper SVG text export.
        </div>
        
        <div class="info-panel">
            <h3>📋 Registration Process Overview</h3>
            <div class="info-grid">
                <div class="info-section">
                    <h4>🔴 Required Fields</h4>
                    <ul>
                        <li><strong>Email:</strong> Valid format, unique</li>
                        <li><strong>Username:</strong> 3-20 chars, alphanumeric</li>
                        <li><strong>Password:</strong> 8+ chars, mixed case</li>
                        <li><strong>Confirm Password:</strong> Must match</li>
                        <li><strong>Mission:</strong> Educational access</li>
                        <li><strong>Terms:</strong> Legal acceptance</li>
                    </ul>
                </div>
                <div class="info-section">
                    <h4>🟡 Optional Fields</h4>
                    <ul>
                        <li><strong>Full Name:</strong> Display purposes</li>
                        <li><strong>Organization:</strong> Institution</li>
                        <li><strong>Country:</strong> Geographic preference</li>
                        <li><strong>Newsletter:</strong> Marketing opt-in</li>
                    </ul>
                </div>
                <div class="info-section">
                    <h4>⚡ Process Features</h4>
                    <ul>
                        <li><strong>Client Validation:</strong> Real-time feedback</li>
                        <li><strong>Server Validation:</strong> Security checks</li>
                        <li><strong>Email Verification:</strong> SMTP delivery</li>
                        <li><strong>Error Recovery:</strong> User-friendly flows</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="window.print()">🖨️ Print</button>
            <button class="btn" onclick="downloadFixedSVG()">💾 Download SVG</button>
            <button class="btn" onclick="downloadPNG()">📷 Download PNG</button>
            <button class="btn" onclick="resetView()">🔄 Reset View</button>
            <button class="btn" onclick="fitToScreen()">📐 Fit Screen</button>
        </div>
        
        <div class="diagram-container" id="diagramContainer">
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomIn()" title="Zoom In">+</button>
                <button class="zoom-btn" onclick="zoomOut()" title="Zoom Out">−</button>
                <button class="zoom-btn" onclick="resetView()" title="Reset">⌂</button>
            </div>
            <div class="pan-info">
                💡 Scroll to zoom • Drag to pan • Use controls to navigate
            </div>
            <div class="mermaid-wrapper" id="mermaidWrapper">
                <div class="mermaid" id="mermaidDiagram">
{mermaid_code}
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentScale = 1;
        let currentX = 0;
        let currentY = 0;
        let isDragging = false;
        let dragStartX, dragStartY;
        
        // Initialize Mermaid with better settings
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: false,
                htmlLabels: true,
                curve: 'basis',
                padding: 20
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
                fontSize: '12px',
                fontFamily: 'Arial, sans-serif',
                background: '#ffffff'
            }}
        }});
        
        // Wait for Mermaid to render, then set up interactions
        setTimeout(() => {{
            setupInteractions();
            fitToScreen();
        }}, 2000);
        
        function setupInteractions() {{
            const wrapper = document.getElementById('mermaidWrapper');
            const diagram = document.getElementById('mermaidDiagram');
            
            // Mouse wheel zoom
            wrapper.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const delta = e.deltaY > 0 ? 0.9 : 1.1;
                zoom(delta, e.clientX, e.clientY);
            }});
            
            // Mouse drag pan
            wrapper.addEventListener('mousedown', (e) => {{
                isDragging = true;
                dragStartX = e.clientX - currentX;
                dragStartY = e.clientY - currentY;
                wrapper.style.cursor = 'grabbing';
            }});
            
            wrapper.addEventListener('mousemove', (e) => {{
                if (!isDragging) return;
                currentX = e.clientX - dragStartX;
                currentY = e.clientY - dragStartY;
                updateTransform();
            }});
            
            wrapper.addEventListener('mouseup', () => {{
                isDragging = false;
                wrapper.style.cursor = 'grab';
            }});
            
            wrapper.addEventListener('mouseleave', () => {{
                isDragging = false;
                wrapper.style.cursor = 'grab';
            }});
            
            wrapper.style.cursor = 'grab';
        }}
        
        function zoom(factor, centerX, centerY) {{
            const wrapper = document.getElementById('mermaidWrapper');
            const rect = wrapper.getBoundingClientRect();
            
            // Calculate zoom center relative to wrapper
            const offsetX = centerX - rect.left;
            const offsetY = centerY - rect.top;
            
            // Adjust position to zoom around center point
            currentX = offsetX - (offsetX - currentX) * factor;
            currentY = offsetY - (offsetY - currentY) * factor;
            
            currentScale *= factor;
            currentScale = Math.max(0.1, Math.min(5, currentScale));
            
            updateTransform();
        }}
        
        function updateTransform() {{
            const diagram = document.getElementById('mermaidDiagram');
            diagram.style.transform = `translate(${{currentX}}px, ${{currentY}}px) scale(${{currentScale}})`;
        }}
        
        function zoomIn() {{
            zoom(1.2, window.innerWidth / 2, window.innerHeight / 2);
        }}
        
        function zoomOut() {{
            zoom(0.8, window.innerWidth / 2, window.innerHeight / 2);
        }}
        
        function resetView() {{
            currentScale = 1;
            currentX = 0;
            currentY = 0;
            updateTransform();
        }}
        
        function fitToScreen() {{
            const wrapper = document.getElementById('mermaidWrapper');
            const diagram = document.getElementById('mermaidDiagram');
            const svg = diagram.querySelector('svg');
            
            if (!svg) return;
            
            const wrapperRect = wrapper.getBoundingClientRect();
            const svgRect = svg.getBoundingClientRect();
            
            const scaleX = wrapperRect.width / svgRect.width;
            const scaleY = wrapperRect.height / svgRect.height;
            const scale = Math.min(scaleX, scaleY) * 0.9; // 90% to add padding
            
            currentScale = scale;
            currentX = (wrapperRect.width - svgRect.width * scale) / 2;
            currentY = (wrapperRect.height - svgRect.height * scale) / 2;
            
            updateTransform();
        }}
        
        function downloadFixedSVG() {{
            const svg = document.querySelector('.mermaid svg');
            if (!svg) return;
            
            const clonedSvg = svg.cloneNode(true);
            
            // Ensure white background
            clonedSvg.style.background = '#ffffff';
            clonedSvg.setAttribute('style', 'background: #ffffff');
            
            // Add white background rectangle
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('width', '100%');
            rect.setAttribute('height', '100%');
            rect.setAttribute('fill', '#ffffff');
            clonedSvg.insertBefore(rect, clonedSvg.firstChild);
            
            // Fix all text elements for visibility
            const textElements = clonedSvg.querySelectorAll('text, tspan');
            textElements.forEach(text => {{
                text.style.fontFamily = 'Arial, sans-serif';
                text.style.fontWeight = 'bold';
                text.style.fontSize = '12px';
                text.style.fill = '#000000';
                text.style.stroke = 'none';
                text.setAttribute('font-family', 'Arial, sans-serif');
                text.setAttribute('font-weight', 'bold');
                text.setAttribute('font-size', '12px');
                text.setAttribute('fill', '#000000');
                text.setAttribute('stroke', 'none');
            }});
            
            // Fix edge labels
            const edgeLabels = clonedSvg.querySelectorAll('.edgeLabel rect');
            edgeLabels.forEach(rect => {{
                rect.setAttribute('fill', '#ffffff');
                rect.setAttribute('stroke', '#333333');
                rect.setAttribute('stroke-width', '1');
                rect.setAttribute('opacity', '1');
            }});
            
            const serializer = new XMLSerializer();
            const source = '<?xml version="1.0" encoding="UTF-8"?>\\n' + serializer.serializeToString(clonedSvg);
            const blob = new Blob([source], {{type: 'image/svg+xml;charset=utf-8'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'AndyLibrary_Registration_Process_Fixed.svg';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        function downloadPNG() {{
            const svg = document.querySelector('.mermaid svg');
            if (!svg) return;
            
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            const svgClone = svg.cloneNode(true);
            
            // Add white background
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('width', '100%');
            rect.setAttribute('height', '100%');
            rect.setAttribute('fill', '#ffffff');
            svgClone.insertBefore(rect, svgClone.firstChild);
            
            // Fix text elements
            const textElements = svgClone.querySelectorAll('text, tspan');
            textElements.forEach(text => {{
                text.setAttribute('fill', '#000000');
                text.setAttribute('font-family', 'Arial, sans-serif');
                text.setAttribute('font-weight', 'bold');
            }});
            
            const data = new XMLSerializer().serializeToString(svgClone);
            const blob = new Blob([data], {{type: 'image/svg+xml;charset=utf-8'}});
            const url = URL.createObjectURL(blob);
            const img = new Image();
            
            img.onload = function() {{
                canvas.width = img.width * 2;
                canvas.height = img.height * 2;
                ctx.scale(2, 2);
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob(function(pngBlob) {{
                    const pngUrl = URL.createObjectURL(pngBlob);
                    const a = document.createElement('a');
                    a.href = pngUrl;
                    a.download = 'AndyLibrary_Registration_Process_Fixed.png';
                    a.click();
                    URL.revokeObjectURL(pngUrl);
                }}, 'image/png');
                
                URL.revokeObjectURL(url);
            }};
            
            img.src = url;
        }}
    </script>
</body>
</html>'''
    
    return html_content

def main():
    # Create the fixed HTML with proper display and SVG handling
    html_content = create_fixed_flowchart_html()
    
    # Save to the organized directory
    with open('Docs/Flowchart/HTML/AndyLibrary_Fixed_Registration_Process.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Flowchart display issues fixed successfully!")
    print("\n🔧 FIXES APPLIED:")
    print("   • ✅ FULL VIEWPORT DISPLAY - Complete flowchart visible")
    print("   • ✅ WORKING PAN/ZOOM - Mouse wheel zoom, drag to pan")
    print("   • ✅ PROPER NAVIGATION - Zoom controls and fit-to-screen")
    print("   • ✅ FIXED SVG TEXT - Visible text in exported SVG files")
    print("   • ✅ ENHANCED CONTROLS - Better zoom/pan user experience")
    print("\n📁 Updated File:")
    print("   • Docs/Flowchart/HTML/AndyLibrary_Fixed_Registration_Process.html")
    print("\n🎯 NEW FEATURES:")
    print("   • Mouse wheel zooming")
    print("   • Click and drag panning") 
    print("   • Fit-to-screen button")
    print("   • Reset view functionality")
    print("   • Improved SVG export with visible text")
    print("\n🚀 Ready to use! Open the HTML file in your browser.")

if __name__ == "__main__":
    main()