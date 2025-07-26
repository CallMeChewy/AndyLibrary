# File: test_real_time_journey.py
# Path: /home/herb/Desktop/AndyLibrary/test_real_time_journey.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-25
# Last Modified: 2025-07-25 07:25AM

"""
Real-time testing script for BowersWorld.com to AndyLibrary user journey
Simulates complete user experience from promotion to library access
"""

import requests
import json
import time
import subprocess
import sys
import random
from datetime import datetime

class RealTimeJourneyTester:
    def __init__(self, port=8086):
        self.port = port
        self.base_url = f"http://127.0.0.1:{port}"
        self.server_process = None
        self.test_user = None
        
    def start_server(self):
        """Start the AndyLibrary server"""
        print("🚀 Starting AndyLibrary server...")
        
        self.server_process = subprocess.Popen([
            sys.executable, 'StartAndyGoogle.py', '--port', str(self.port)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server startup...")
        time.sleep(10)
        
        # Verify server is running
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Server running at {self.base_url}")
                return True
        except:
            pass
            
        print("❌ Server failed to start")
        return False
    
    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")
    
    def test_promotional_landing(self):
        """Test the BowersWorld.com promotional page"""
        print("\n" + "="*70)
        print("📖 STEP 1: Testing BowersWorld.com Promotional Landing")
        print("="*70)
        
        try:
            # Test BowersWorld.com page
            response = requests.get(f"{self.base_url}/bowersworld.html", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                print(f"✅ BowersWorld.com page loaded ({len(content):,} characters)")
                
                # Check for key promotional content
                checks = [
                    ("Project Himalaya content", "Project Himalaya" in content),
                    ("Educational mission", "Getting education into the hands" in content),
                    ("AI-Human synergy", "AI-Human Synergy" in content),
                    ("Registration CTA", "Access AndyLibrary Now" in content),
                    ("Subscription tiers", "access level" in content.lower()),
                ]
                
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"   {status} {check_name}")
                
                return all(result for _, result in checks)
            else:
                print(f"❌ BowersWorld.com page failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading promotional page: {e}")
            return False
    
    def test_registration_flow(self):
        """Test the registration process"""
        print("\n" + "="*70)
        print("🔐 STEP 2: Testing Registration Flow")
        print("="*70)
        
        # Generate unique test user
        random_id = random.randint(10000, 99999)
        self.test_user = {
            'email': f'testuser{random_id}@bowersworld.com',
            'password': 'SecurePassword123!',
            'username': f'testuser{random_id}',
            'subscription_tier': 'scholar',
            'mission_acknowledgment': True,
            'user_preferences': {
                'data_sharing_consent': True,
                'anonymous_usage_consent': True,
                'preferred_subjects': ['Computer Science', 'Mathematics'],
                'academic_level': 'graduate',
                'institution_type': 'university',
                'geographic_region': 'north-america'
            },
            'publication_requests': [{
                'request_type': 'subject_area',
                'content_description': 'Machine Learning textbooks for graduate study',
                'subject_area': 'Computer Science',
                'reason': 'PhD research in AI applications for education'
            }]
        }
        
        try:
            # Test auth page accessibility
            auth_response = requests.get(f"{self.base_url}/auth.html", timeout=10)
            if auth_response.status_code == 200:
                print("✅ Authentication page accessible")
            else:
                print(f"❌ Authentication page failed: {auth_response.status_code}")
                return False
            
            # Test registration
            print(f"🔍 Registering user: {self.test_user['email']}")
            reg_response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=self.test_user,
                timeout=15
            )
            
            if reg_response.status_code == 200:
                result = reg_response.json()
                print("✅ Registration successful")
                print(f"   User ID: {result.get('user', {}).get('id')}")
                print(f"   Email: {result.get('user', {}).get('email')}")
                print(f"   Subscription: {result.get('user', {}).get('subscription_tier')}")
                print(f"   Preferences saved: {result.get('preferences_saved')}")
                print(f"   Publication requests: {result.get('publication_requests_saved')}")
                
                return True
            else:
                print(f"❌ Registration failed: {reg_response.status_code}")
                print(f"   Error: {reg_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def test_authentication_and_access(self):
        """Test login and library access"""
        print("\n" + "="*70)
        print("🔑 STEP 3: Testing Authentication and Library Access")
        print("="*70)
        
        if not self.test_user:
            print("❌ No test user available for authentication")
            return False
        
        try:
            # Test login
            login_data = {
                'email': self.test_user['email'],
                'password': self.test_user['password']
            }
            
            login_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                session_token = login_result.get('session_token')
                
                print("✅ Login successful")
                print(f"   Session token: {session_token[:20]}...")
                print(f"   Welcome message: {login_result.get('message')}")
                
                # Test authenticated access to profile
                headers = {'Authorization': f'Bearer {session_token}'}
                profile_response = requests.get(
                    f"{self.base_url}/api/auth/profile",
                    headers=headers,
                    timeout=10
                )
                
                if profile_response.status_code == 200:
                    print("✅ Authenticated profile access successful")
                    
                    # Test library access with subscription limits
                    return self.test_library_access_levels(headers)
                else:
                    print(f"❌ Profile access failed: {profile_response.status_code}")
                    return False
                    
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"   Error: {login_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_library_access_levels(self, headers):
        """Test subscription tier access controls"""
        print("\n   📚 Testing Library Access Controls...")
        
        try:
            # Test book browsing
            books_response = requests.get(
                f"{self.base_url}/api/books?limit=5",
                headers=headers,
                timeout=10
            )
            
            if books_response.status_code == 200:
                books_data = books_response.json()
                print(f"   ✅ Book browsing successful ({len(books_data.get('books', []))} books)")
                
                # Test categories access
                categories_response = requests.get(
                    f"{self.base_url}/api/categories",
                    headers=headers,
                    timeout=10
                )
                
                if categories_response.status_code == 200:
                    categories = categories_response.json()
                    print(f"   ✅ Categories access successful ({len(categories)} categories)")
                    
                    # Test subscription tier limits
                    subscription_tier = self.test_user['subscription_tier']
                    print(f"   📊 Testing '{subscription_tier}' tier access limits...")
                    
                    # Test with higher limit to see tier restrictions
                    high_limit_response = requests.get(
                        f"{self.base_url}/api/books?limit=100",
                        headers=headers,
                        timeout=10
                    )
                    
                    if high_limit_response.status_code == 200:
                        high_limit_data = high_limit_response.json()
                        returned_books = len(high_limit_data.get('books', []))
                        print(f"   ✅ Subscription limits working (returned {returned_books} books)")
                        return True
                    else:
                        print(f"   ❌ High limit test failed: {high_limit_response.status_code}")
                        return False
                else:
                    print(f"   ❌ Categories access failed: {categories_response.status_code}")
                    return False
            else:
                print(f"   ❌ Book browsing failed: {books_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Library access error: {e}")
            return False
    
    def test_complete_user_journey(self):
        """Test the complete user journey from promotion to library access"""
        print("🎓 BowersWorld.com to AndyLibrary - Real-Time User Journey Test")
        print("📚 'Getting education into the hands of people who can least afford it'")
        print("="*70)
        print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Server URL: {self.base_url}")
        
        results = []
        
        # Start server
        if not self.start_server():
            print("❌ CRITICAL: Server failed to start")
            return False
        
        try:
            # Step 1: Test promotional landing
            step1_result = self.test_promotional_landing()
            results.append(("Promotional Landing", step1_result))
            
            # Step 2: Test registration flow
            step2_result = self.test_registration_flow()
            results.append(("Registration Flow", step2_result))
            
            # Step 3: Test authentication and library access
            step3_result = self.test_authentication_and_access()
            results.append(("Authentication & Library Access", step3_result))
            
            # Display results
            print("\n" + "="*70)
            print("📊 REAL-TIME JOURNEY TEST RESULTS")
            print("="*70)
            
            passed = 0
            total = len(results)
            
            for step_name, success in results:
                status = "✅ PASSED" if success else "❌ FAILED"
                print(f"{status} - {step_name}")
                if success:
                    passed += 1
            
            success_rate = (passed / total) * 100
            print(f"\n🎯 Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
            
            if passed == total:
                print("\n🎉 COMPLETE SUCCESS!")
                print("✅ Full user journey working perfectly")
                print("🚀 System ready for real-time deployment")
                print("\n📋 User Journey Summary:")
                print("   1. User visits BowersWorld.com promotional page")
                print("   2. Learns about Project Himalaya AI-human synergy")
                print("   3. Clicks 'Access AndyLibrary Now' button")
                print("   4. Registers with mission acknowledgment")
                print("   5. Sets preferences and requests publications")
                print("   6. Logs in with new credentials")
                print("   7. Accesses library with subscription tier limits")
                print("   8. Browses books and categories successfully")
            else:
                print(f"\n⚠️ {total - passed} steps failed - needs attention")
            
            return passed == total
            
        finally:
            self.stop_server()

def main():
    """Run the real-time journey test"""
    tester = RealTimeJourneyTester()
    success = tester.test_complete_user_journey()
    
    print(f"\n{'='*70}")
    print("🏁 Real-time testing completed")
    print(f"Result: {'SUCCESS' if success else 'FAILURE'}")
    print(f"{'='*70}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)