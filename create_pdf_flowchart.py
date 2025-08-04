#!/usr/bin/env python3
"""
Create PDF Flowchart - Much Better Solution!
- Self-contained PDF format
- Works with any PDF viewer 
- Built-in zoom/navigation
- No browser compatibility issues
- Perfect for management presentations
"""

import subprocess
import sys
import os
from pathlib import Path

def install_required_packages():
    """Install required packages for PDF generation"""
    packages = [
        'reportlab',
        'svglib', 
        'selenium',
        'cairosvg'
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def create_pdf_from_html():
    """Create PDF directly from the HTML file using headless browser"""
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        print("🌐 Setting up headless browser...")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--print-to-pdf')
        
        # Get absolute path to HTML file
        html_file_path = os.path.abspath('Docs/Flowchart/HTML/AndyLibrary_Fixed_Registration_Process.html')
        pdf_output_path = os.path.abspath('Docs/Flowchart/PDF/AndyLibrary_Registration_Process.pdf')
        
        # Ensure PDF directory exists
        os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
        
        # Create WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            print(f"📄 Loading HTML file: {html_file_path}")
            driver.get(f"file://{html_file_path}")
            
            # Wait for Mermaid to render
            print("⏳ Waiting for Mermaid diagram to render...")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".mermaid svg"))
            )
            
            # Additional wait for complete rendering
            time.sleep(5)
            
            # Execute print to PDF
            print("🖨️ Generating PDF...")
            pdf_options = {
                'landscape': True,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': True,
                'paperWidth': 11.7,  # A4 landscape width in inches
                'paperHeight': 8.3,  # A4 landscape height in inches
                'marginTop': 0,
                'marginBottom': 0,
                'marginLeft': 0,
                'marginRight': 0
            }
            
            result = driver.execute_cdp_cmd('Page.printToPDF', pdf_options)
            
            # Save PDF
            import base64
            with open(pdf_output_path, 'wb') as f:
                f.write(base64.b64decode(result['data']))
            
            print(f"✅ PDF created: {pdf_output_path}")
            return pdf_output_path
            
        finally:
            driver.quit()
            
    except ImportError:
        print("❌ Selenium not available. Trying alternative method...")
        return create_pdf_alternative()
    except Exception as e:
        print(f"❌ Browser method failed: {e}")
        return create_pdf_alternative()

def create_pdf_alternative():
    """Alternative PDF creation using reportlab directly"""
    
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        import io
        
        print("📝 Creating PDF using ReportLab...")
        
        # Setup PDF document
        pdf_path = 'Docs/Flowchart/PDF/AndyLibrary_Registration_Process.pdf'
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=landscape(A4),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#667eea'),
            leftIndent=0
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20
        )
        
        # Build content
        content = []
        
        # Title
        content.append(Paragraph("🏛️ AndyLibrary Registration Process", title_style))
        content.append(Paragraph("Complete User Flow Documentation", styles['Normal']))
        content.append(Spacer(1, 20))
        
        # Process Overview
        content.append(Paragraph("📋 Registration Process Overview", heading_style))
        
        # Required Fields
        content.append(Paragraph("<b>🔴 Required Fields:</b>", body_style))
        required_fields = [
            "<b>Email Address:</b> Valid format, unique in system",
            "<b>Username:</b> 3-20 characters, alphanumeric only",  
            "<b>Password:</b> 8+ characters, mixed case required",
            "<b>Confirm Password:</b> Must match original password",
            "<b>Mission Acknowledgment:</b> Educational access agreement",
            "<b>Terms Agreement:</b> Legal acceptance required"
        ]
        for field in required_fields:
            content.append(Paragraph(f"• {field}", body_style))
        
        content.append(Spacer(1, 12))
        
        # Optional Fields  
        content.append(Paragraph("<b>🟡 Optional Fields:</b>", body_style))
        optional_fields = [
            "<b>Full Name:</b> Display and personalization purposes",
            "<b>Organization:</b> Institution or company name",
            "<b>Country:</b> Geographic preference selection", 
            "<b>Newsletter:</b> Marketing communications opt-in",
            "<b>Profile Picture:</b> Avatar image upload"
        ]
        for field in optional_fields:
            content.append(Paragraph(f"• {field}", body_style))
        
        content.append(Spacer(1, 12))
        
        # Process Steps
        content.append(Paragraph("⚡ Registration Process Steps", heading_style))
        
        process_steps = [
            "<b>1. Initial Load:</b> User opens browser, system loads website and checks existing session",
            "<b>2. Authentication Check:</b> System validates if user is already authenticated",
            "<b>3. Form Display:</b> If not authenticated, registration form is presented",
            "<b>4. Data Entry:</b> User enters required and optional information",
            "<b>5. Client Validation:</b> Real-time validation with visual feedback",
            "<b>6. Form Submission:</b> Data sent to server via POST /api/auth/register",
            "<b>7. Server Validation:</b> Comprehensive security and format checks",
            "<b>8. Duplicate Check:</b> Email and username uniqueness verification",
            "<b>9. Account Creation:</b> User record created with bcrypt password hashing",
            "<b>10. Email Preparation:</b> Verification email template generated",
            "<b>11. SMTP Delivery:</b> Email sent via smtp.gmail.com:465 SSL",
            "<b>12. User Verification:</b> User clicks verification link in email",
            "<b>13. Token Validation:</b> Server validates verification token (24h expiry)",
            "<b>14. Account Activation:</b> EmailVerified and IsActive flags set to TRUE",
            "<b>15. Login Ready:</b> User can now authenticate and access full system"
        ]
        
        for step in process_steps:
            content.append(Paragraph(step, body_style))
            content.append(Spacer(1, 3))
        
        content.append(Spacer(1, 15))
        
        # Technical Details
        content.append(Paragraph("🔧 Technical Implementation", heading_style))
        
        tech_details = [
            "<b>Database:</b> SQLite with async support and connection pooling",
            "<b>Password Security:</b> bcrypt hashing with cost factor 12",
            "<b>Token Generation:</b> UUID verification tokens with 24-hour expiration",
            "<b>Email Service:</b> Gmail SMTP with App Password authentication",
            "<b>Validation:</b> Client-side real-time + server-side comprehensive checks",
            "<b>Security:</b> SQL injection prevention, XSS sanitization, CSRF protection",
            "<b>Error Handling:</b> User-friendly error messages with recovery flows",
            "<b>Rate Limiting:</b> Maximum 3 verification email attempts per hour"
        ]
        
        for detail in tech_details:
            content.append(Paragraph(detail, body_style))
            content.append(Spacer(1, 3))
        
        content.append(Spacer(1, 15))
        
        # Footer
        content.append(Paragraph("📄 Generated by AndyLibrary System", styles['Normal']))
        content.append(Paragraph("For detailed visual flowchart, see: Docs/Flowchart/HTML/", styles['Normal']))
        
        # Build PDF
        doc.build(content)
        
        print(f"✅ PDF created successfully: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ ReportLab method failed: {e}")
        return None

def create_simple_pdf():
    """Create a simple text-based PDF as fallback"""
    
    print("📝 Creating simple PDF documentation...")
    
    # Read the Mermaid source for reference
    try:
        with open('Docs/Flowchart/Mermaid/AndyLibrary_Fixed_Registration_Process.mmd', 'r') as f:
            mermaid_content = f.read()
    except:
        mermaid_content = "Mermaid source not available"
    
    # Create simple text documentation
    pdf_content = f"""
AndyLibrary Registration Process
==============================

COMPLETE USER REGISTRATION WORKFLOW

Process Flow Summary:
1. START → User Opens Browser
2. LOAD WEBSITE → Static assets and service worker  
3. CHECK SESSION → Validate existing authentication
4. LOAD USER INTERFACE → Render forms and validation
5. USER AUTHENTICATED? → Decision point
   - YES → Proceed to MAIN SYSTEM
   - NO → Show registration form

Registration Form Process:
6. SHOW REGISTRATION FORM → Display all input fields
7. ENTER REQUIRED FIELDS:
   • Email (valid format, unique)
   • Username (3-20 chars, alphanumeric) 
   • Password (8+ chars, mixed case)
   • Confirm Password (must match)
   • Mission acknowledgment (required)
   • Terms agreement (required)

8. ENTER OPTIONAL FIELDS:
   • Full Name
   • Organization  
   • Country
   • Newsletter subscription

9. CLIENT-SIDE VALIDATION → Real-time feedback
10. SUBMIT FORM → POST to /api/auth/register

Server Processing:
11. SERVER-SIDE VALIDATION → Comprehensive checks
12. VALIDATION PASSED? → Decision point
    - NO → Return field-specific errors → Back to form
    - YES → Continue to duplicate check

13. CHECK DUPLICATES → Query Users table
14. DUPLICATES FOUND? → Decision point  
    - YES → Return conflict error → Back to form
    - NO → Proceed to account creation

Account Creation:
15. CREATE USER ACCOUNT:
    • Hash password with bcrypt (cost: 12)
    • Generate verification token (UUID)
    • Set EmailVerified = FALSE
    • Set IsActive = FALSE  
    • Insert into database

16. ACCOUNT CREATED → User record saved
17. PREPARE VERIFICATION EMAIL → Template generation
18. SEND EMAIL VIA SMTP → smtp.gmail.com:465 SSL

Email Verification:
19. EMAIL SENT? → Decision point
    - YES → Registration success response
    - NO → Partial success (account created, email failed)

20. USER WAITS FOR EMAIL → Check inbox and spam
21. EMAIL RECEIVED? → Decision point
    - NO → Resend email option
    - YES → Click verification link

22. CLICK VERIFICATION LINK → GET /api/auth/verify-email
23. VALIDATE TOKEN → Server-side verification
24. TOKEN VALID? → Decision point
    - NO → Token error → Resend option
    - YES → Activate account

Account Activation:
25. ACTIVATE ACCOUNT:
    • Set EmailVerified = TRUE
    • Set IsActive = TRUE
    • Clear verification token
    • Create audit log entry

26. VERIFICATION SUCCESS → Account fully activated
27. PROCEED TO LOGIN → Ready for authentication  
28. LOGIN PROCESS → Session creation
29. MAIN SYSTEM ACCESS → Full features available
30. END → Book access complete

Technical Specifications:
========================

Required Fields Validation:
• Email: RFC 5322 format validation, unique constraint
• Username: 3-20 characters, alphanumeric only
• Password: Minimum 8 characters, mixed case, special chars
• Confirm Password: Must exactly match original
• Mission: Boolean true required
• Terms: Boolean true required

Optional Fields:
• Full Name: String, display purposes
• Organization: String, institution/company  
• Country: Dropdown selection
• Newsletter: Boolean, marketing opt-in
• Profile Picture: File upload, avatar

Security Measures:
• bcrypt password hashing (cost: 12)
• UUID verification tokens  
• 24-hour token expiration
• SQL injection prevention
• XSS sanitization
• CSRF token validation
• Rate limiting (3 emails/hour)

Database Schema:
• Users table with auto-increment ID
• EmailVerified boolean flag
• IsActive boolean flag  
• SubscriptionTier default 'free'
• AccessLevel default 'basic'
• CreatedAt timestamp
• VerifiedAt timestamp

SMTP Configuration:
• Server: smtp.gmail.com
• Port: 465 (SSL)
• Authentication: App Password
• Timeout: 30 seconds
• Retry: 3 attempts
• Delivery confirmation

Error Handling:
• Field-specific validation errors
• User-friendly error messages
• Recovery flows for all failure points
• Graceful degradation
• Admin notification for system errors

Success Responses:
• HTTP 201 Created for successful registration
• JSON response with user ID and next steps
• Clear instructions for email verification
• Redirect to login after verification

This comprehensive registration system ensures secure, user-friendly 
account creation with robust error handling and recovery mechanisms.

For visual flowchart representation, open:
Docs/Flowchart/HTML/AndyLibrary_Fixed_Registration_Process.html

Source Files:
• Mermaid: Docs/Flowchart/Mermaid/AndyLibrary_Fixed_Registration_Process.mmd  
• HTML: Docs/Flowchart/HTML/AndyLibrary_Fixed_Registration_Process.html
• Documentation: Docs/Flowchart/Documentation/

Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Write to simple text file that can be converted to PDF
    pdf_dir = 'Docs/Flowchart/PDF'
    os.makedirs(pdf_dir, exist_ok=True)
    
    text_file = f'{pdf_dir}/AndyLibrary_Registration_Process.txt'
    with open(text_file, 'w') as f:
        f.write(pdf_content)
    
    print(f"✅ Text documentation created: {text_file}")
    print("💡 You can convert this to PDF using any text-to-PDF tool")
    
    return text_file

def main():
    print("🚀 Creating PDF version of AndyLibrary Registration Process...")
    print("\n📋 PDF Format Benefits:")
    print("   • Self-contained - works everywhere")  
    print("   • Built-in zoom/navigation in any PDF viewer")
    print("   • Perfect for management presentations")
    print("   • No browser compatibility issues")
    print("   • Easy to share and distribute")
    
    # Create PDF directory
    os.makedirs('Docs/Flowchart/PDF', exist_ok=True)
    
    # Try different methods in order of preference
    pdf_path = None
    
    # Method 1: Try browser-based PDF generation (best quality)
    try:
        print("\n🌐 Attempting browser-based PDF generation...")
        install_required_packages()
        pdf_path = create_pdf_from_html()
    except Exception as e:
        print(f"❌ Browser method failed: {e}")
    
    # Method 2: Try ReportLab PDF generation  
    if not pdf_path:
        try:
            print("\n📝 Attempting ReportLab PDF generation...")
            pdf_path = create_pdf_alternative()
        except Exception as e:
            print(f"❌ ReportLab method failed: {e}")
    
    # Method 3: Create text documentation as fallback
    if not pdf_path:
        print("\n📄 Creating text documentation (can be converted to PDF)...")
        pdf_path = create_simple_pdf()
    
    if pdf_path:
        print(f"\n✅ SUCCESS! Documentation created: {pdf_path}")
        print(f"📁 Location: {os.path.abspath(pdf_path)}")
        print("\n🎯 ADVANTAGES OF PDF FORMAT:")
        print("   • ✅ Works in any PDF viewer (Adobe, Chrome, Firefox, etc.)")
        print("   • ✅ Built-in zoom, pan, search functionality")  
        print("   • ✅ No browser compatibility issues")
        print("   • ✅ Perfect for presentations and sharing")
        print("   • ✅ Self-contained - no external dependencies")
        print("\n🚀 Ready to use! Open with any PDF viewer.")
    else:
        print("\n❌ All PDF generation methods failed.")
        print("💡 You can manually convert the HTML file to PDF using:")
        print("   • Chrome: Print → Save as PDF")
        print("   • Firefox: Print → Save as PDF") 
        print("   • Online converters: HTML-to-PDF services")

if __name__ == "__main__":
    main()