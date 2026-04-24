from abc import ABC, abstractmethod
from typing import List

from models.email_message import EmailMessage, ComposeEmailData, EmailAttachment
from models.email_connection_info import EmailConnectionInfo

class IEmailRetrievalService(ABC):
    """
    interfata pentru serviciile de preluare email
    """

    @abstractmethod
    def get_email_list(self, conn: EmailConnectionInfo,
                       limit: int) -> List[EmailMessage]:
        """returneaza lista de emails (doar anteturi)"""
        ...

    @abstractmethod
    def get_email_full(self, conn: EmailConnectionInfo,
                       uid: str) -> EmailMessage:
        """descarca email ul complet inclusiv atasamentele"""
        ...


class IEmailSendingService(ABC):
    """
    interfata pentru serviciul de trimitere email
    """

    @abstractmethod
    def send_email(self, conn: EmailConnectionInfo,
                   data: ComposeEmailData) -> None:
        """trimite un email (cu sau fara atasamente)"""
        ...


class IEmailContentService(ABC):
    """
    interfata pentru procesarea continutului email
    """

    @abstractmethod
    def decode_header(self, value: str) -> str:
        """decodeaza un antet email (Base64 / quoted-printable)"""
        ...

    @abstractmethod
    def extract_body(self, raw_msg) -> tuple:
        """extrage corpul text + HTML dintr un mesaj raw"""
        ...


class IAttachmentService(ABC):
    """
    interfata pentru gestionarea atasamentelor
    """

    @abstractmethod
    def save_attachments(self, attachments: List[EmailAttachment],
                         directory: str) -> int:
        """salvează atasamentele pe disc. returnează numarul salvat"""
        ...
