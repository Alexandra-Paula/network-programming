"""
Lista email-uri prin IMAP
Descarcare email cu atasamente
"""
import imaplib
from typing import List

from constants.app_constants import AppConstants
from interfaces.email_interfaces import IEmailRetrievalService
from models.email_connection_info import EmailConnectionInfo
from models.email_message import EmailMessage
from services.email_content_service import EmailContentService


class ImapEmailService(IEmailRetrievalService):

    #serviciu de preluare email prin protocolul IMAP
    def __init__(self):
        self._content_svc = EmailContentService()

    def get_email_list(self, conn: EmailConnectionInfo,
                       limit: int = None,
                       folder: str = "INBOX") -> List[EmailMessage]:

        #criteriul 2: returneaza lista de email-uri via IMAP
        #descarca doar antetele

        if limit is None:
            limit = AppConstants.Email.MAX_EMAILS_TO_LOAD

        messages = []
        imap = None
        try:
            imap = imaplib.IMAP4_SSL(AppConstants.Imap.GMAIL_SERVER,
                                     AppConstants.Imap.GMAIL_PORT)
            imap.login(conn.email, conn.password)
            imap.select(folder, readonly=True)

            status, data = imap.search(None, "ALL")
            if status != "OK":
                return []

            msg_ids = data[0].split()
            recent = msg_ids[-limit:][::-1]  # ultimele `limit`, invers

            for mid in recent:
                _, raw = imap.fetch(mid, "(BODY.PEEK[HEADER])")
                if not raw or not raw[0]:
                    continue
                parsed = self._content_svc.parse_raw_bytes(raw[0][1])

                msg = EmailMessage(
                    uid=mid.decode(),
                    subject=self._content_svc.decode_header(
                        parsed.get("Subject", "(fără subiect)")),
                    sender=self._content_svc.decode_header(
                        parsed.get("From", "(necunoscut)")),
                    recipients=self._content_svc.decode_header(
                        parsed.get("To", "")),
                    date=parsed.get("Date", ""),
                )
                messages.append(msg)

        except Exception as exc:
            raise RuntimeError(
                AppConstants.Messages.ERROR_LOADING_EMAILS.format(str(exc))
            ) from exc
        finally:
            if imap:
                try:
                    imap.logout()
                except Exception:
                    pass

        return messages

    def get_email_full(self, conn: EmailConnectionInfo,
                       uid: str,
                       folder: str = "INBOX") -> EmailMessage:

        #criteriul3: descarca un email complet cu atașamente via IMAP
        imap = None
        try:
            imap = imaplib.IMAP4_SSL(AppConstants.Imap.GMAIL_SERVER,
                                     AppConstants.Imap.GMAIL_PORT)
            imap.login(conn.email, conn.password)
            imap.select(folder, readonly=True)

            status, raw = imap.fetch(uid.encode(), "(RFC822)")
            if status != "OK" or not raw or not raw[0]:
                raise RuntimeError(f"Email-ul cu ID {uid} nu a fost găsit.")

            parsed = self._content_svc.parse_raw_bytes(raw[0][1])
            body_text, body_html = self._content_svc.extract_body(parsed)
            attachments = self._content_svc.extract_attachments(parsed)

            return EmailMessage(
                uid=uid,
                subject=self._content_svc.decode_header(
                    parsed.get("Subject", "(fără subiect)")),
                sender=self._content_svc.decode_header(
                    parsed.get("From", "")),
                recipients=self._content_svc.decode_header(
                    parsed.get("To", "")),
                date=parsed.get("Date", ""),
                body_text=body_text,
                body_html=body_html,
                attachments=attachments,
            )

        except Exception as exc:
            raise RuntimeError(str(exc)) from exc
        finally:
            if imap:
                try:
                    imap.logout()
                except Exception:
                    pass
