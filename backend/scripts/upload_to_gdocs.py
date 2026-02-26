#!/usr/bin/env python3
"""
Upload WHATSAPP_PRD.md to Google Docs
"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Token location (canonical path from TOOLS.md)
TOKEN_PATH = '/Users/nikunjvora/clawd/ops/credentials/google_tokens.json'
PRD_PATH = '/Users/nikunjvora/clawd/ventures/jodi/product/WHATSAPP_PRD.md'

def markdown_to_gdocs_structure(md_text):
    """
    Convert markdown to Google Docs structured content
    Simple conversion: headers, bold, italic, lists
    """
    requests = []
    current_index = 1
    
    lines = md_text.split('\n')
    
    for line in lines:
        if not line.strip():
            # Empty line - add paragraph
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': '\n'
                }
            })
            current_index += 1
            continue
        
        # Headers
        if line.startswith('# '):
            text = line[2:] + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': text
                }
            })
            # Style as heading 1
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': current_index,
                        'endIndex': current_index + len(text)
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_1'
                    },
                    'fields': 'namedStyleType'
                }
            })
            current_index += len(text)
        elif line.startswith('## '):
            text = line[3:] + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': text
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': current_index,
                        'endIndex': current_index + len(text)
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_2'
                    },
                    'fields': 'namedStyleType'
                }
            })
            current_index += len(text)
        elif line.startswith('### '):
            text = line[4:] + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': text
                }
            })
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': current_index,
                        'endIndex': current_index + len(text)
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'HEADING_3'
                    },
                    'fields': 'namedStyleType'
                }
            })
            current_index += len(text)
        else:
            # Regular text
            text = line + '\n'
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': text
                }
            })
            current_index += len(text)
    
    return requests

def upload_prd_to_gdocs():
    """Upload PRD to Google Docs"""
    
    # Load credentials
    with open(TOKEN_PATH, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes')
    )
    
    # Build Docs API service
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    try:
        # Create new document
        doc = docs_service.documents().create(body={
            'title': 'JODI WhatsApp PRD — Product Requirements Document'
        }).execute()
        
        doc_id = doc['documentId']
        print(f"✓ Created Google Doc: {doc_id}")
        print(f"  URL: https://docs.google.com/document/d/{doc_id}/edit")
        
        # Read markdown content
        with open(PRD_PATH, 'r') as f:
            md_content = f.read()
        
        # Insert content (simple approach: just insert raw text, formatting happens in Docs)
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': md_content
                }
            }
        ]
        
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        print("✓ Uploaded content")
        
        # Share with nikunj.vora@gmail.com (editor access)
        drive_service.permissions().create(
            fileId=doc_id,
            body={
                'type': 'user',
                'role': 'writer',
                'emailAddress': 'nikunj.vora@gmail.com'
            },
            sendNotificationEmail=False
        ).execute()
        
        print("✓ Shared with nikunj.vora@gmail.com (editor access)")
        
        # Share with ea.nikvora@gmail.com (viewer access)
        drive_service.permissions().create(
            fileId=doc_id,
            body={
                'type': 'user',
                'role': 'writer',
                'emailAddress': 'ea.nikvora@gmail.com'
            },
            sendNotificationEmail=False
        ).execute()
        
        print("✓ Shared with ea.nikvora@gmail.com (editor access)")
        
        return doc_id
        
    except HttpError as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    doc_id = upload_prd_to_gdocs()
    if doc_id:
        print(f"\n🎉 SUCCESS!")
        print(f"\nGoogle Doc URL:")
        print(f"https://docs.google.com/document/d/{doc_id}/edit")
    else:
        print("\n❌ FAILED")
