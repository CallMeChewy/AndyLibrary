# File: DatabaseServer.py
# Simple HTTP server for database downloads
import http.server
import socketserver
import os
from pathlib import Path

class DatabaseHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/home/herb/Desktop/AndyLibrary/Public", **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Content-Disposition', 'attachment')
        super().end_headers()

def serve_database(port=8080):
    """Serve database files on specified port"""
    for port_try in range(port, port + 10):
        try:
            with socketserver.TCPServer(("", port_try), DatabaseHandler) as httpd:
                print(f"🌐 Database server running on http://localhost:{port_try}")
                print(f"📥 Database URL: http://localhost:{port_try}/GrandsonLibrary_Latest.db")
                httpd.serve_forever()
        except OSError:
            continue
    print("❌ No available ports found")

if __name__ == "__main__":
    serve_database()
