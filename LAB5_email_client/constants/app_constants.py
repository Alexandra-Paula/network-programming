class AppConstants:

    class Smtp:
        GMAIL_SERVER = "smtp.gmail.com"
        GMAIL_PORT   = 587          # STARTTLS
        USE_SSL      = True

    class Pop3:
        GMAIL_SERVER = "pop.gmail.com"
        GMAIL_PORT   = 995          # SSL

    class Imap:
        GMAIL_SERVER = "imap.gmail.com"
        GMAIL_PORT   = 993          # SSL

    class Email:
        MAX_EMAILS_TO_LOAD      = 15
        REPLY_PREFIX            = "Re: "
        ORIGINAL_MESSAGE_HEADER = "\n\n---------- Original Message ----------\n"
        ATTACHMENTS_DIR         = "attachments"

    class Messages:
        ENTER_EMAIL_PASSWORD          = "Introduceți email-ul și parola (App Password)"
        CONNECTING_TO_SERVER          = "Conectare la server..."
        SENDING_EMAIL                 = "Se trimite email-ul..."
        EMAIL_SENT_SUCCESS            = "Email trimis cu succes!"
        ERROR_LOADING_EMAILS          = "Eroare la încărcarea email-urilor: {0}"
        ERROR_SENDING_EMAIL           = "Eroare la trimiterea email-ului: {0}"
        ADDED_ATTACHMENT              = "Atașament adăugat: {0}"
        LOADED_EMAILS_COUNT           = "Încărcate {0} email-uri"
        DOWNLOADED_ATTACHMENTS_COUNT  = "Descărcate {0} atașamente"
        NO_EMAIL_SELECTED             = "Selectați un email din listă"
        AUTH_HINT                     = ("NOTĂ: Folosiți o 'App Password' Gmail.\n"
                                         "Cont Google → Securitate → Parole aplicații")

    class UI:
        WINDOW_TITLE  = "📧 Email Client"
        WINDOW_SIZE   = "1100x700"
        FONT_MAIN     = ("Segoe UI", 10)
        FONT_BOLD     = ("Segoe UI", 10, "bold")
        FONT_TITLE    = ("Segoe UI", 13, "bold")
        FONT_MONO     = ("Courier New", 9)
        BG_DARK       = "#1e1e2e"
        BG_PANEL      = "#2a2a3e"
        BG_ITEM       = "#313145"
        BG_HOVER      = "#3d3d5c"
        ACCENT        = "#89b4fa"
        ACCENT2       = "#cba6f7"
        TEXT_MAIN     = "#cdd6f4"
        TEXT_DIM      = "#6c7086"
        SUCCESS       = "#a6e3a1"
        ERROR_COLOR   = "#f38ba8"
        WARNING       = "#fab387"
