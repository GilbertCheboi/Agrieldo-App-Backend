# animals/testsheets.py
import gspread
from google.oauth2.service_account import Credentials
from django.conf import settings

def test_google_sheet_connection(sheet_id=None):
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]

    creds = Credentials.from_service_account_file(
        settings.GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=SCOPES
    )

    client = gspread.authorize(creds)

    if not sheet_id:
        raise ValueError("Provide the SHEET ID to test")

    sh = client.open_by_key(sheet_id)
    print("✅ Connected successfully!")
    print("Worksheets:")
    for ws in sh.worksheets():
        print(" -", ws.title)
    return sh

