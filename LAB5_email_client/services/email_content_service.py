import email
import email.header
from email import policy
from email.parser import BytesParser
from typing import Tuple

from interfaces.email_interfaces import IEmailContentService
from models.email_message import EmailAttachment


class EmailContentService(IEmailContentService):
    #proceseaza + decodeaza continutul email-urilor

    def decode_header(self, value: str) -> str:
        #decodeaza antetele email (base64 / quoted-printable)
        if not value:
            return ""
        try:
            parts = email.header.decode_header(value)
            result = []
            for part, charset in parts:
                if isinstance(part, bytes):
                    result.append(part.decode(charset or "utf-8", errors="replace"))
                else:
                    result.append(str(part))
            return "".join(result)
        except Exception:
            return str(value)

    def extract_body(self, raw_msg) -> Tuple[str, str]:
        #extrage corpul text/plain + text/html
        #retur (body_text, body_html)

        body_text = ""
        body_html = ""

        if raw_msg.is_multipart():
            for part in raw_msg.walk():
                ct   = part.get_content_type()
                disp = str(part.get("Content-Disposition", ""))
                if "attachment" in disp:
                    continue
                if ct == "text/plain" and not body_text:
                    body_text = self._decode_part(part)
                elif ct == "text/html" and not body_html:
                    body_html = self._decode_part(part)
        else:
            ct = raw_msg.get_content_type()
            if ct == "text/plain":
                body_text = self._decode_part(raw_msg)
            elif ct == "text/html":
                body_html = self._decode_part(raw_msg)

        return body_text, body_html

    def extract_attachments(self, raw_msg) -> list:
        """extrage lista de atasamente"""
        attachments = []
        for part in raw_msg.walk():
            disp = str(part.get("Content-Disposition", ""))
            if "attachment" in disp:
                filename = part.get_filename()
                if filename:
                    filename = self.decode_header(filename)
                    data = part.get_payload(decode=True) or b""
                    attachments.append(EmailAttachment(
                        filename=filename,
                        content_type=part.get_content_type(),
                        data=data
                    ))
        return attachments

    def parse_raw_bytes(self, raw_bytes: bytes):
        """parseaza bytes raw intr un obiect email"""
        return BytesParser(policy=policy.default).parsebytes(raw_bytes)

    def _decode_part(self, part) -> str:
        """decodeaza payload ul unei parti de email"""
        payload = part.get_payload(decode=True)
        if not payload:
            return ""
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")
