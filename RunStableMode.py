# File: RunStableMode.py
# Path: /home/herb/Desktop/AndyLibrary/RunStableMode.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-23
# Last Modified: 2025-07-23 10:40PM

"""
AndyLibrary Stable Mode Runner
Provides a stable way to run the library in Google Drive mode with automatic fallback
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

class StableModeRunner:
    """Runs AndyLibrary with stability monitoring and auto-restart"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.max_restarts = 3
        self.restart_delay = 2  # seconds
        
    def run_with_monitoring(self, mode='gdrive', port=None):
        """Run the server with monitoring and auto-restart on crashes"""
        print("🚀 AndyLibrary Stable Mode Runner")
        print("=" * 50)
        
        restart_count = 0
        
        while restart_count < self.max_restarts:
            try:
                print(f"🔄 Starting AndyLibrary (attempt {restart_count + 1}/{self.max_restarts})")
                print(f"🌐 Mode: {mode.upper()}")
                
                # Build command
                cmd = [sys.executable, "StartAndyGoogle.py", "--mode", mode]
                if port:
                    cmd.extend(["--port", str(port)])
                
                # Start process
                process = subprocess.Popen(
                    cmd,
                    cwd=self.script_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Monitor output
                startup_success = False
                for line in process.stdout:
                    print(line.rstrip())
                    
                    # Check for successful startup
                    if "✅ AndyGoogle API server started successfully" in line:
                        startup_success = True
                        print("✅ Server started successfully!")
                        
                    # Check for critical errors
                    if "❌" in line or "ERROR:" in line:
                        print(f"⚠️ Error detected: {line.rstrip()}")
                
                # Wait for process to complete
                return_code = process.wait()
                
                if startup_success and return_code == 0:
                    print("✅ Server shut down gracefully")
                    break
                else:
                    print(f"⚠️ Server crashed with return code: {return_code}")
                    restart_count += 1
                    
                    if restart_count < self.max_restarts:
                        print(f"🔄 Restarting in {self.restart_delay} seconds...")
                        time.sleep(self.restart_delay)
                    
            except KeyboardInterrupt:
                print("\n👋 Stopped by user")
                if 'process' in locals():
                    process.terminate()
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                restart_count += 1
                
        if restart_count >= self.max_restarts:
            print(f"❌ Maximum restarts ({self.max_restarts}) reached. Switching to LOCAL mode...")
            return self.run_fallback_mode()
            
    def run_fallback_mode(self):
        """Run in safe LOCAL mode as fallback"""
        print("\n🔄 Starting FALLBACK mode (LOCAL only)")
        try:
            subprocess.run([
                sys.executable, "StartAndyGoogle.py", 
                "--mode", "local"
            ], cwd=self.script_dir)
        except KeyboardInterrupt:
            print("\n👋 Fallback mode stopped by user")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AndyLibrary in stable mode")
    parser.add_argument('--mode', choices=['local', 'gdrive'], default='gdrive',
                       help='Operating mode (default: gdrive)')
    parser.add_argument('--port', type=int, help='Port to use')
    
    args = parser.parse_args()
    
    runner = StableModeRunner()
    runner.run_with_monitoring(mode=args.mode, port=args.port)

if __name__ == "__main__":
    main()