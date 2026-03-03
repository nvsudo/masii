#!/usr/bin/env python3
"""Google API helper — handles token refresh and common API calls.

✅ Current OAuth token has FULL permissions (as of 2026-02-10):
   - Gmail (read, send, modify)
   - Calendar (full access)
   - Drive (full access - create, share, organize)
   - Docs, Sheets, Slides, Presentations
   
   See TOOLS.md for scope details and re-auth instructions if needed.
"""

import json, urllib.request, urllib.parse, sys, os

TOKENS_PATH = os.path.join(os.path.dirname(__file__), "google_tokens.json")

def load_creds():
    with open(TOKENS_PATH) as f:
        return json.load(f)

def refresh_access_token():
    creds = load_creds()
    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request(creds["token_uri"], data=data)
    resp = urllib.request.urlopen(req)
    tokens = json.loads(resp.read())
    return tokens["access_token"]

def api_get(url, access_token=None):
    if not access_token:
        access_token = refresh_access_token()
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {access_token}")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def api_post(url, body, access_token=None):
    if not access_token:
        access_token = refresh_access_token()
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# --- Gmail helpers ---

def gmail_profile():
    return api_get("https://gmail.googleapis.com/gmail/v1/users/me/profile")

def gmail_list(query="", max_results=10):
    params = urllib.parse.urlencode({"q": query, "maxResults": max_results})
    return api_get(f"https://gmail.googleapis.com/gmail/v1/users/me/messages?{params}")

def gmail_get(msg_id, fmt="full"):
    return api_get(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format={fmt}")

def gmail_send(to, subject, body_text):
    import base64
    from email.mime.text import MIMEText
    msg = MIMEText(body_text)
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return api_post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        {"raw": raw}
    )

# --- Calendar helpers ---

def calendar_events(time_min=None, time_max=None, max_results=10, calendar_id="primary"):
    from datetime import datetime, timezone
    if not time_min:
        time_min = datetime.now(timezone.utc).isoformat()
    params = {"timeMin": time_min, "maxResults": max_results, "singleEvents": True, "orderBy": "startTime"}
    if time_max:
        params["timeMax"] = time_max
    qs = urllib.parse.urlencode(params)
    return api_get(f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(calendar_id)}/events?{qs}")

# --- CLI ---

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "profile"
    if cmd == "profile":
        print(json.dumps(gmail_profile(), indent=2))
    elif cmd == "inbox":
        q = sys.argv[2] if len(sys.argv) > 2 else "is:inbox"
        print(json.dumps(gmail_list(q), indent=2))
    elif cmd == "read":
        print(json.dumps(gmail_get(sys.argv[2]), indent=2))
    elif cmd == "calendar":
        print(json.dumps(calendar_events(), indent=2))
    elif cmd == "token":
        print(refresh_access_token())
    else:
        print(f"Usage: {sys.argv[0]} [profile|inbox|read <id>|calendar|token]")
