import base64
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import unquote, urlsplit

import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from life_automation.core.constants import (
    GOOGLE_OAUTH_CLIENT_ID,
    GOOGLE_OAUTH_CLIENT_SECRET,
    GOOGLE_OAUTH_REDIRECT_URI,
)
from life_automation.types.mail import MailService

GMAIL_SCOPES = [
    # User info
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
    # Gmail
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
]


class Gmail(MailService):
    def get_oauth_authorization_url(self):
        # OAuth client configuration in dictionary format
        client_config = {
            "web": {
                "client_id": GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_OAUTH_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        # Initiate the OAuth flow using the client config dictionary
        flow = Flow.from_client_config(
            client_config, GMAIL_SCOPES, redirect_uri=GOOGLE_OAUTH_REDIRECT_URI
        )
        auth_url, _ = flow.authorization_url(prompt="consent")

        return auth_url

    def _setup_and_get_label(
        self,
        *,
        service,
        parent_label_name: str,
        label_name: str,
    ) -> str | None:
        # Fetch the list of existing labels
        try:
            labels_list = service.users().labels().list(userId="me").execute()
            labels = labels_list.get("labels", [])

            # Check if the nested label already exists
            for label in labels:
                if label["name"] == f"{parent_label_name}/{label_name}":
                    return label["id"]  # Return the existing label

            # First, ensure the parent label exists
            parent_label_id = None
            for label in labels:
                if label["name"] == parent_label_name:
                    parent_label_id = label["id"]
                    break

            # If parent label doesn't exist, create it
            if not parent_label_id:
                parent_label = {
                    "type": "user",
                    "name": parent_label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                    "color": {"backgroundColor": "#e3d7ff", "textColor": "#3d188e"},
                }
                parent_label = (
                    service.users()
                    .labels()
                    .create(userId="me", body=parent_label)
                    .execute()
                )
                parent_label_id = parent_label["id"]

            # Now, create the "Referral Requests" label under "Jobs"
            new_label = {
                "type": "user",
                "name": f"{parent_label_name}/{label_name}",
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
                "parentId": parent_label_id,  # Nested under "Jobs"
                "color": {"backgroundColor": "#e3d7ff", "textColor": "#3d188e"},
            }
            created_label = (
                service.users().labels().create(userId="me", body=new_label).execute()
            )

            return created_label["id"]
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    def _label_message(
        self,
        *,
        service,
        label_id: str,
        message_id: str,
    ) -> bool:
        try:
            modification = {"addLabelIds": [label_id]}
            service.users().messages().modify(
                userId="me",
                id=message_id,
                body=modification,
            ).execute()
            return True
        except Exception as error:
            print(f"Failed to label the email: {error}")
            return False

    def _prepare_and_send_message(
        self,
        *,
        service,
        to_email: str,
        subject: str,
        html_body: str,
        attachments: list[str],
    ) -> str | None:
        # Create MIME email message
        message = MIMEMultipart()
        message["to"] = to_email
        message["subject"] = subject
        msg_content = MIMEText(html_body, "html")
        message.attach(msg_content)

        # Attach each PDF from the list of URLs
        for attachment_url in attachments:
            try:
                # Download the PDF file
                response = requests.get(attachment_url)
                response.raise_for_status()  # Raise an error for bad responses

                # Fallback: Extract filename from URL and sanitize
                url_path = urlsplit(attachment_url).path
                filename = unquote(os.path.basename(url_path))

                # Ensure the filename ends with .pdf
                if not filename.endswith(".pdf"):
                    filename += ".pdf"

                # Create a MIMEBase object for the PDF attachment
                attachment_part = MIMEBase("application", "pdf")
                attachment_part.set_payload(response.content)
                encoders.encode_base64(attachment_part)

                # Set the content headers
                attachment_part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}",
                )

                # Attach the file to the message
                message.attach(attachment_part)
            except Exception as error:
                print(f"Failed to attach {attachment_url}: {error}")
                continue

        # Base64url encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        # Create the request body for Gmail API
        message_body = {"raw": raw_message}

        # Send the email using Gmail API's messages.send endpoint
        try:
            message = (
                service.users()
                .messages()
                .send(userId="me", body=message_body)
                .execute()
            )
            return message["id"]
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    def send(
        self,
        credentials: Credentials,
        *,
        to_email: str,
        subject: str,
        html_body: str,
        attachments: list[str],
    ):
        # Build the Gmail API client
        service = build("gmail", "v1", credentials=credentials)

        # Step 1: Fetch and ensure label is created
        label_id = self._setup_and_get_label(
            service=service,
            parent_label_name="Jobs",
            label_name="Referral Requests (automated)",
        )
        if label_id is None:
            raise RuntimeError("Cannot create label")

        # Step 2: Send the message
        message_id = self._prepare_and_send_message(
            service=service,
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            attachments=attachments,
        )
        if message_id is None:
            raise RuntimeError("Cannot send the message")

        # Step 3: Label the message
        for _ in range(1):  # 5 tries
            success = self._label_message(
                service=service,
                label_id=label_id,
                message_id=message_id,
            )
            if success:
                return

        raise RuntimeError("Failed to label the message")
