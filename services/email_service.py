import base64
from email import message
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from datetime import datetime
import email.utils

from models.schemas import EmailData


class GmailService:
    def __init__(self, token_data: Dict[str, Any]):
        self.credentials = Credentials.from_authorized_user_info(token_data)
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def get_recent_emails(self, max_results: int = 10) -> List[EmailData]:
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q='in:inbox'
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def _get_email_details(self, message_id: str) -> EmailData:
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            sender = self._get_header_value(headers, 'From')
            subject = self._get_header_value(headers, 'Subject')
            date = self._get_header_value(headers, 'Date')

            print(message)
            
            snippet = message.get('snippet', '')
            body = ''
            payload = message.get('payload', {})
            parts = payload.get('parts', [])
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            formatted_date = self._format_date(date)
            
            return EmailData(
                id=message_id,
                sender=sender,
                subject=subject,
                snippet=body or snippet,
                date=formatted_date
            )
            
        except HttpError as error:
            print(f"Error getting email details for {message_id}: {error}")
            return None
    
    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _format_date(self, date_str: str) -> str:
        try:
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_str
    
    def search_emails(self, query: str, max_results: int = 10) -> List[EmailData]:
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def get_email_by_id(self, message_id: str) -> EmailData:
        try:
            return self._get_email_details(message_id)
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")