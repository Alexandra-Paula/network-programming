from services.pop3_email_service import Pop3EmailService
from services.imap_email_service import ImapEmailService
from services.smtp_email_service import SmtpEmailService
from services.attachment_service import AttachmentService
from services.email_content_service import EmailContentService


class EmailServiceFactory:
    #Factory care creeaza + returneaza instante ale serviciilor email
    _pop3_service:       Pop3EmailService       = None
    _imap_service:       ImapEmailService       = None
    _smtp_service:       SmtpEmailService       = None
    _attachment_service: AttachmentService      = None
    _content_service:    EmailContentService    = None

    @classmethod
    def get_pop3_service(cls) -> Pop3EmailService:
        if cls._pop3_service is None:
            cls._pop3_service = Pop3EmailService()
        return cls._pop3_service

    @classmethod
    def get_imap_service(cls) -> ImapEmailService:
        if cls._imap_service is None:
            cls._imap_service = ImapEmailService()
        return cls._imap_service

    @classmethod
    def get_smtp_service(cls) -> SmtpEmailService:
        if cls._smtp_service is None:
            cls._smtp_service = SmtpEmailService()
        return cls._smtp_service

    @classmethod
    def get_attachment_service(cls) -> AttachmentService:
        if cls._attachment_service is None:
            cls._attachment_service = AttachmentService()
        return cls._attachment_service

    @classmethod
    def get_content_service(cls) -> EmailContentService:
        if cls._content_service is None:
            cls._content_service = EmailContentService()
        return cls._content_service
