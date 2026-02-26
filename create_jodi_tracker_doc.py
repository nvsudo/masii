#!/usr/bin/env python3
"""Create JODI Product Tracker Google Doc"""

import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CREDS_FILE = Path("/Users/nikunjvora/clawd/ops/credentials/google_tokens.json")
TRACKER_FILE = Path("/Users/nikunjvora/clawd/JODI/PRODUCT_TRACKER.md")

def load_credentials():
    with open(CREDS_FILE) as f:
        creds_data = json.load(f)
    
    return Credentials(
        token=creds_data.get("access_token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
        scopes=creds_data.get("scopes", [])
    )

def main():
    creds = load_credentials()
    
    # Create docs service
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Create empty doc
    doc = docs_service.documents().create(body={'title': 'JODI — Product Tracker'}).execute()
    doc_id = doc['documentId']
    print(f"Created doc: {doc_id}")
    
    # Read markdown content
    with open(TRACKER_FILE) as f:
        content = f.read()
    
    # Insert content
    requests = [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]
    
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()
    print("Inserted content")
    
    # Share with N
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'nikunj.vora@gmail.com'
    }
    
    drive_service.permissions().create(
        fileId=doc_id,
        body=permission
    ).execute()
    print("Shared with nikunj.vora@gmail.com")
    
    print(f"\nhttps://docs.google.com/document/d/{doc_id}/edit")

if __name__ == "__main__":
    main()
