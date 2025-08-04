# File: test_smtp.py
# Path: /home/herb/Desktop/AndyLibrary/test_smtp.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-08-04
# Last Modified: 2025-08-04 12:33AM

import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def TestSMTPConnection():
    """Test SMTP connection to Gmail with the configured credentials"""
    
    # Gmail SMTP settings - trying SSL port 465
    SMTPHost = "smtp.gmail.com"
    SMTPPort = 465
    Username = "HimalayaProject1@gmail.com"
    Password = "svah cggw kvcp pdck"
    
    print("🔍 Testing SMTP Connection...")
    print(f"Host: {SMTPHost}")
    print(f"Port: {SMTPPort}")
    print(f"Username: {Username}")
    print(f"Password: {'*' * len(Password)}")
    print()
    
    # Test 1: Socket connection
    print("📡 Testing socket connection...")
    try:
        TestSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TestSocket.settimeout(10)  # 10 second timeout
        Result = TestSocket.connect_ex((SMTPHost, SMTPPort))
        TestSocket.close()
        
        if Result == 0:
            print("✅ Socket connection successful")
        else:
            print(f"❌ Socket connection failed with error code: {Result}")
            return False
    except Exception as e:
        print(f"❌ Socket connection failed: {e}")
        return False
    
    # Test 2: SMTP connection and authentication
    print("\n🔐 Testing SMTP authentication...")
    try:
        SMTPServer = smtplib.SMTP_SSL(SMTPHost, SMTPPort)  # Use SSL instead of TLS
        SMTPServer.set_debuglevel(1)  # Enable debug output
        print("✅ SSL connection established")
        
        SMTPServer.login(Username, Password)
        print("✅ SMTP authentication successful")
        
        # Test 3: Send test email
        print("\n📧 Testing email send...")
        Message = MIMEMultipart()
        Message['From'] = Username
        Message['To'] = "newuser@bowersworld.com"
        Message['Subject'] = "SMTP Test - AndyLibrary Connection Test"
        
        Body = """
        This is a test email from AndyLibrary SMTP configuration test.
        
        If you receive this email, the SMTP connection is working properly.
        
        Test timestamp: 2025-08-04 12:33AM
        """
        
        Message.attach(MIMEText(Body, 'plain'))
        
        Text = Message.as_string()
        SMTPServer.sendmail(Username, "newuser@bowersworld.com", Text)
        print("✅ Test email sent successfully")
        
        SMTPServer.quit()
        print("✅ SMTP connection closed cleanly")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication failed: {e}")
        print("💡 This usually means:")
        print("   - Wrong username/password")
        print("   - 2FA enabled without App Password")
        print("   - Less secure app access disabled")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ SMTP Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Gmail SMTP Connection Test")
    print("=" * 50)
    
    Success = TestSMTPConnection()
    
    print("\n" + "=" * 50)
    if Success:
        print("🎉 SMTP test completed successfully!")
        print("📧 Email should have been sent to newuser@bowersworld.com")
    else:
        print("❌ SMTP test failed!")
        print("🔧 Check network connection, credentials, and Gmail settings")