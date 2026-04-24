"""
Lista email-uri prin POP3
Descarcare email cu atasamente
"""
import poplib
from typing import List

from constants.app_constants import AppConstants
from interfaces.email_interfaces import IEmailRetrievalService
from models.email_connection_info import EmailConnectionInfo
from models.email_message import EmailMessage
from services.email_content_service import EmailContentService


class Pop3EmailService(IEmailRetrievalService):

    def __init__(self):
        self._content_svc = EmailContentService()

    def get_email_list(self, conn: EmailConnectionInfo,
                       limit: int = None) -> List[EmailMessage]:

        #criteriul 1: returneaza lista de email-uri via POP3

        if limit is None:
            limit = AppConstants.Email.MAX_EMAILS_TO_LOAD

        messages = []
        pop = None
        try:
            pop = poplib.POP3_SSL(AppConstants.Pop3.GMAIL_SERVER,
                                  AppConstants.Pop3.GMAIL_PORT)
            pop.user(conn.email)
            pop.pass_(conn.password)

            num_msgs, _ = pop.stat()
            start = max(1, num_msgs - limit + 1)

            for i in range(num_msgs, start - 1, -1):
                raw = pop.retr(i)[1]
                raw_bytes = b"\n".join(raw)
                parsed = self._content_svc.parse_raw_bytes(raw_bytes)

                msg = EmailMessage(
                    uid=str(i),
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
            if pop:
                try:
                    pop.quit()
                except Exception:
                    pass

        return messages

    def get_email_full(self, conn: EmailConnectionInfo,
                       uid: str) -> EmailMessage:

       #criteriul 3: descarca un email complet cu atasamente via POP3

        pop = None
        try:
            pop = poplib.POP3_SSL(AppConstants.Pop3.GMAIL_SERVER,
                                  AppConstants.Pop3.GMAIL_PORT)
            pop.user(conn.email)
            pop.pass_(conn.password)

            raw = pop.retr(int(uid))[1]
            raw_bytes = b"\n".join(raw)
            parsed = self._content_svc.parse_raw_bytes(raw_bytes)

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
            if pop:
                try:
                    pop.quit()
                except Exception:
                    pass
