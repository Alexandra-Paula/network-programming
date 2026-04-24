"""
Trimite email text simplu
Trimite email cu atasament
Subject + Reply-To
"""
import os
import smtplib
import email.utils
from email.message import EmailMessage as StdEmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from constants.app_constants import AppConstants
from interfaces.email_interfaces import IEmailSendingService
from models.email_connection_info import EmailConnectionInfo
from models.email_message import ComposeEmailData


class SmtpEmailService(IEmailSendingService):
    """
    Serviciu de trimitere email prin protocolul SMTP cu STARTTLS
    """

    def send_email(self, conn: EmailConnectionInfo,
                   data: ComposeEmailData) -> None:
        """
        Criterii 4 & 5: Trimite email cu sau fara atasamente
        Criteriu 6: Include Subject și Reply-To
        """
        if data.attachments:
            self._send_with_attachments(conn, data)
        else:
            self._send_plain(conn, data)

    #criteriul 4, text simplu
    def _send_plain(self, conn: EmailConnectionInfo,
                    data: ComposeEmailData) -> None:
        msg = StdEmailMessage()
        msg["From"]       = conn.email
        msg["To"]         = data.to
        msg["Subject"]    = data.subject                     
        msg["Date"]       = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid()

        if data.reply_to:
            msg["Reply-To"] = data.reply_to                  

        msg.set_content(data.body, charset="utf-8")

        self._send_via_smtp(conn, msg)

    #criteriul 5, cu atasament
    def _send_with_attachments(self, conn: EmailConnectionInfo,
                                data: ComposeEmailData) -> None:
        msg = MIMEMultipart()
        msg["From"]       = conn.email
        msg["To"]         = data.to
        msg["Subject"]    = data.subject                     
        msg["Date"]       = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid()

        if data.reply_to:
            msg["Reply-To"] = data.reply_to                  

        msg.attach(MIMEText(data.body, "plain", "utf-8"))

        for path in data.attachments:
            if not os.path.isfile(path):
                continue
            filename = os.path.basename(path)
            with open(path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment",
                            filename=filename)
            msg.attach(part)

        self._send_via_smtp(conn, msg)


    #conexiune SMTP comuna
    def _send_via_smtp(self, conn: EmailConnectionInfo, msg) -> None:
        try:
            with smtplib.SMTP(AppConstants.Smtp.GMAIL_SERVER,
                              AppConstants.Smtp.GMAIL_PORT) as server:
                server.ehlo()
                server.starttls()          #criptare TLS
                server.ehlo()
                server.login(conn.email, conn.password)
                server.send_message(msg)
        except smtplib.SMTPAuthenticationError as exc:
            raise RuntimeError(
                "Autentificare eșuată. Verificați email-ul și App Password-ul."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                AppConstants.Messages.ERROR_SENDING_EMAIL.format(str(exc))
            ) from exc
