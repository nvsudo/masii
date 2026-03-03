#!/usr/bin/env python3
"""Update JODI Product Tracker Google Doc"""

import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CREDS_FILE = Path("/Users/nikunjvora/clawd/ops/credentials/google_tokens.json")
TRACKER_FILE = Path("/Users/nikunjvora/clawd/JODI/PRODUCT_TRACKER.md")
DOC_ID = "1q_q8OCARDBEbhycG1QEPaF7SgZIeFH3D8jM37UXi_-M"

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
    docs_service = build('docs', 'v1', credentials=creds)
    
    # Get current doc to find end index
    doc = docs_service.documents().get(documentId=DOC_ID).execute()
    end_index = doc['body']['content'][-1]['endIndex']
    
    # Read new content
    with open(TRACKER_FILE) as f:
        content = f.read()
    
    # Delete all existing content (except first char which is always preserved)
    requests = [
        {
            'deleteContentRange': {
                'range': {
                    'startIndex': 1,
                    'endIndex': end_index - 1
                }
            }
        },
        {
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }
    ]
    
    docs_service.documents().batchUpdate(
        documentId=DOC_ID,
        body={'requests': requests}
    ).execute()
    
    print(f"✅ Updated: https://docs.google.com/document/d/{DOC_ID}/edit")

if __name__ == "__main__":
    main()
