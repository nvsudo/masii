#!/usr/bin/env python3
"""
Google OAuth re-authentication with full permissions.

This script generates a new OAuth token with FULL access:
- Gmail (read, send, modify)
- Calendar (full access)
- Drive (FULL access - not just readonly)
- Docs, Sheets, Slides (full access)

Run this when you need to refresh permissions or add new scopes.
"""

import json
import urllib.parse
import urllib.request
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

CLIENT_SECRET_FILE = "client_secret_1056899789657-4mtn53t6sk8crfl7ierhmm4jvboqcajs.apps.googleusercontent.com.json"
TOKENS_FILE = "google_tokens.json"

# FULL SCOPES - includes drive (not drive.readonly)
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",  # FULL DRIVE ACCESS (not readonly)
]

# Global to capture auth code
auth_code = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authorization successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress log messages

def load_client_secret():
    with open(CLIENT_SECRET_FILE) as f:
        data = json.load(f)
        return data['installed']

def exchange_code_for_token(client_info, code):
    """Exchange authorization code for access & refresh tokens"""
    data = urllib.parse.urlencode({
        'code': code,
        'client_id': client_info['client_id'],
        'client_secret': client_info['client_secret'],
        'redirect_uri': 'http://localhost:8080',
        'grant_type': 'authorization_code'
    }).encode()
    
    req = urllib.request.Request(client_info['token_uri'], data=data)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def main():
    print("=" * 70)
    print("Google OAuth Re-Authentication")
    print("=" * 70)
    print()
    print("This will request FULL permissions for:")
    print("  ✓ Gmail (read, send, modify)")
    print("  ✓ Calendar (full access)")
    print("  ✓ Drive (FULL - can create, share, organize files)")
    print("  ✓ Docs, Sheets, Slides (full access)")
    print()
    print("Account: ea.nikvora@gmail.com (AI's working account)")
    print()
    
    client_info = load_client_secret()
    
    # Build authorization URL
    auth_params = {
        'client_id': client_info['client_id'],
        'redirect_uri': 'http://localhost:8080',
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'  # Force consent screen to get refresh token
    }
    
    auth_url = f"{client_info['auth_uri']}?{urllib.parse.urlencode(auth_params)}"
    
    print("Step 1: Opening browser for authorization...")
    print()
    print("If browser doesn't open, visit this URL:")
    print(auth_url)
    print()
    
    webbrowser.open(auth_url)
    
    # Start local server to receive callback
    print("Step 2: Waiting for authorization callback...")
    print("(A local server is running on http://localhost:8080)")
    print()
    
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    
    # Wait for one request (the OAuth callback)
    server.handle_request()
    
    if not auth_code:
        print("❌ Failed to receive authorization code")
        sys.exit(1)
    
    print("✅ Authorization code received")
    print()
    print("Step 3: Exchanging code for tokens...")
    
    tokens = exchange_code_for_token(client_info, auth_code)
    
    # Build the tokens file format
    tokens_data = {
        'token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'token_uri': client_info['token_uri'],
        'client_id': client_info['client_id'],
        'client_secret': client_info['client_secret'],
        'scopes': SCOPES,
        'universe_domain': 'googleapis.com',
        'account': '',
        'expiry': ''  # Will be calculated on first use
    }
    
    # Save tokens
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens_data, f, indent=2)
    
    print("✅ Tokens saved to:", TOKENS_FILE)
    print()
    print("=" * 70)
    print("SUCCESS! Full Google API permissions granted")
    print("=" * 70)
    print()
    print("Updated scopes:")
    for scope in SCOPES:
        print(f"  ✓ {scope.split('/')[-1]}")
    print()
    print("You can now:")
    print("  - Create Google Docs, Sheets, Slides")
    print("  - Share documents programmatically")
    print("  - Organize files in Drive")
    print("  - Full Gmail and Calendar access")
    print()
    print("Next: Test with python3 google_api.py profile")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
