from dataclasses import dataclass, field
from typing import List


@dataclass
class EmailAttachment:
    """un atasament al unui email"""
    filename:     str
    content_type: str
    data:         bytes

    @property
    def size_kb(self) -> float:
        return round(len(self.data) / 1024, 1)


@dataclass
class EmailMessage:
    """
    modelul principal al unui email
    """
    uid:          str  = ""
    subject:      str  = ""
    sender:       str  = ""
    recipients:   str  = ""
    date:         str  = ""
    body_text:    str  = ""
    body_html:    str  = ""
    attachments:  List[EmailAttachment] = field(default_factory=list)
    raw_headers:  dict = field(default_factory=dict)

    @property
    def has_attachments(self) -> bool:
        return len(self.attachments) > 0

    @property
    def attachment_count(self) -> int:
        return len(self.attachments)

    @property
    def short_subject(self) -> str:
        return self.subject[:60] + "…" if len(self.subject) > 60 else self.subject

    @property
    def short_sender(self) -> str:
        return self.sender[:40] + "…" if len(self.sender) > 40 else self.sender

    def __repr__(self):
        return f"EmailMessage(uid={self.uid!r}, subject={self.subject!r})"


@dataclass
class ComposeEmailData:
    """
    date pentru compunerea unui email nou
    """
    to:          str  = ""
    subject:     str  = ""
    body:        str  = ""
    reply_to:    str  = ""
    attachments: List[str] = field(default_factory=list) 

    def is_valid(self) -> bool:
        return bool(self.to.strip()) and bool(self.subject.strip())
