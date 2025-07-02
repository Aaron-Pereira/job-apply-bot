import os
import base64
import re
from email import message_from_bytes
from time import sleep

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the Gmail read-only scope required for accessing inbox data
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Authorize and return the Gmail API service."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), '..', 'token.json')  # Path to saved user credentials
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')  # Path to OAuth2 credentials

    # Load existing credentials if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        # If no token exists, initiate the OAuth2 flow
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the new token for future use
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # Build and return the Gmail API service object
    return build('gmail', 'v1', credentials=creds)


def get_latest_verification_code(service, subject_filter=""):
    """
    Returns the latest 6-digit verification code found in the email body.
    If subject_filter is empty, it searches all emails in the inbox.
    """
    # Build the Gmail search query
    query = f'subject:"{subject_filter}"' if subject_filter else ''
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q=query
    ).execute()

    # Get the most recent email message
    messages = results.get('messages', [])
    if not messages:
        return None

    message_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=message_id, format='raw').execute()

    # Decode raw email message and convert to MIME format
    raw_msg = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    mime_msg = message_from_bytes(raw_msg)

    # Extract body content (handle multipart emails too)
    if mime_msg.is_multipart():
        body = ''
        for part in mime_msg.get_payload():
            if part.get_content_type() == 'text/plain':
                body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        body = mime_msg.get_payload(decode=True).decode('utf-8', errors='ignore')

    # Search for a 6-digit code in the body
    match = re.search(r'\b\d{6}\b', body)
    return match.group(0) if match else None


def get_latest_verification_code_from_subject(service, subject_filter="is your code for SEEK"):
    """
    Returns the latest 6-digit verification code found in the subject line
    of the most recent email matching subject_filter.
    """
    # Search for the latest email matching the subject filter
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q=f'subject:"{subject_filter}"'
    ).execute()

    messages = results.get('messages', [])
    if not messages:
        return None

    message_id = messages[0]['id']
    # Request only metadata (not full body) for efficiency
    msg = service.users().messages().get(
        userId='me',
        id=message_id,
        format='metadata',
        metadataHeaders=['subject']
    ).execute()

    # Extract the subject header
    headers = msg.get('payload', {}).get('headers', [])
    subject = ""
    for header in headers:
        if header['name'].lower() == 'subject':
            subject = header['value']
            break

    # Extract a 6-digit code from the subject line
    match = re.search(r'\b\d{6}\b', subject)
    return match.group(0) if match else None


def wait_for_code(subject="", retries=10, delay=5):
    """
    Repeatedly polls Gmail (up to `retries` times) for a 6-digit code
    found in the email body, optionally filtering by subject.
    """
    service = get_gmail_service()
    for _ in range(retries):
        code = get_latest_verification_code(service, subject_filter=subject)
        if code:
            return code
        sleep(delay)
    return None


def wait_for_code_from_subject(subject_filter="is your code for SEEK", retries=10, delay=5):
    """
    Repeatedly polls Gmail (up to `retries` times) for a 6-digit code
    found in the subject line of emails matching subject_filter.
    """
    service = get_gmail_service()
    for _ in range(retries):
        code = get_latest_verification_code_from_subject(service, subject_filter=subject_filter)
        if code:
            return code
        sleep(delay)
    return None
