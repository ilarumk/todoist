from abc import ABC, abstractmethod
import boto3
from google.cloud import pubsub_v1
from sendgrid import SendGridAPIClient
from typing import Dict, Any
import os

class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, subject: str, html_content: str, to_email: str, from_email: str) -> Dict[str, Any]:
        pass

class AWSEmailProvider(EmailProvider):
    def __init__(self, region: str):
        self.ses = boto3.client('ses', region_name=region)
    
    def send_email(self, subject: str, html_content: str, to_email: str, from_email: str) -> Dict[str, Any]:
        try:
            response = self.ses.send_email(
                Source=from_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Html': {'Data': html_content}}
                }
            )
            return {'success': True, 'message_id': response['MessageId']}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class SendGridEmailProvider(EmailProvider):
    def __init__(self, api_key: str):
        self.client = SendGridAPIClient(api_key)
    
    def send_email(self, subject: str, html_content: str, to_email: str, from_email: str) -> Dict[str, Any]:
        try:
            response = self.client.send({
                'personalizations': [{'to': [{'email': to_email}]}],
                'from': {'email': from_email},
                'subject': subject,
                'content': [{'type': 'text/html', 'value': html_content}]
            })
            return {'success': True, 'status_code': response.status_code}
        except Exception as e:
            return {'success': False, 'error': str(e)}
