import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

# path fix so imports work when run from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants.app_constants import AppConstants
from models.email_connection_info import EmailConnectionInfo
from models.email_message import ComposeEmailData
from services.email_service_factory import EmailServiceFactory

C = AppConstants.UI

class LoginFrame(tk.Frame):
    #panou de autentificare

    def __init__(self, parent, on_connect):
        super().__init__(parent, bg=AppConstants.UI.BG_PANEL, pady=6)
        self._on_connect = on_connect
        self._build()

    def _build(self):
        tk.Label(self, text="📧", bg=C.BG_PANEL, fg=C.ACCENT,
                 font=("Segoe UI", 18)).pack(side="left", padx=(12, 4))

        tk.Label(self, text="Email:", bg=C.BG_PANEL, fg=C.TEXT_MAIN,
                 font=C.FONT_BOLD).pack(side="left", padx=(0, 4))
        self._email_var = tk.StringVar()
        e = tk.Entry(self, textvariable=self._email_var, width=28,
                     bg=C.BG_ITEM, fg=C.TEXT_MAIN, insertbackground=C.TEXT_MAIN,
                     relief="flat", font=C.FONT_MAIN, bd=6)
        e.pack(side="left", padx=(0, 10))

        tk.Label(self, text="App Password:", bg=C.BG_PANEL, fg=C.TEXT_MAIN,
                 font=C.FONT_BOLD).pack(side="left", padx=(0, 4))
        self._pass_var = tk.StringVar()
        p = tk.Entry(self, textvariable=self._pass_var, show="●", width=20,
                     bg=C.BG_ITEM, fg=C.TEXT_MAIN, insertbackground=C.TEXT_MAIN,
                     relief="flat", font=C.FONT_MAIN, bd=6)
        p.pack(side="left", padx=(0, 10))

        btn = tk.Button(self, text="Conectare", command=self._connect,
                        bg=C.ACCENT, fg=C.BG_DARK, font=C.FONT_BOLD,
                        relief="flat", padx=14, cursor="hand2")
        btn.pack(side="left")

        self._status = tk.Label(self, text=AppConstants.Messages.AUTH_HINT,
                                bg=C.BG_PANEL, fg=C.TEXT_DIM,
                                font=("Segoe UI", 8), wraplength=320,
                                justify="left")
        self._status.pack(side="left", padx=14)

    def _connect(self):
        email = self._email_var.get().strip()
        pwd   = self._pass_var.get().strip()
        if not email or not pwd:
            messagebox.showwarning("Atenție",
                                   AppConstants.Messages.ENTER_EMAIL_PASSWORD)
            return
        conn = EmailConnectionInfo(email=email, password=pwd)
        self._on_connect(conn)

    def set_status(self, text: str, color: str = None):
        self._status.config(text=text, fg=color or C.TEXT_DIM)

    def get_connection(self) -> EmailConnectionInfo:
        return EmailConnectionInfo(
            email=self._email_var.get().strip(),
            password=self._pass_var.get().strip()
        )


class EmailListPanel(tk.Frame):
    """lista de emails"""

    def __init__(self, parent, on_select):
        super().__init__(parent, bg=C.BG_PANEL, width=380)
        self.pack_propagate(False)
        self._on_select = on_select
        self._emails    = []
        self._build()

    def _build(self):
        # Toolbar
        bar = tk.Frame(self, bg=C.BG_PANEL)
        bar.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(bar, text="Inbox", bg=C.BG_PANEL, fg=C.ACCENT,
                 font=C.FONT_TITLE).pack(side="left")

        self._proto_var = tk.StringVar(value="IMAP")
        for proto in ("POP3", "IMAP"):
            tk.Radiobutton(bar, text=proto, variable=self._proto_var, value=proto,
                           bg=C.BG_PANEL, fg=C.TEXT_MAIN,
                           selectcolor=C.BG_DARK, activebackground=C.BG_PANEL,
                           font=C.FONT_MAIN).pack(side="right")
        tk.Label(bar, text="Protocol:", bg=C.BG_PANEL, fg=C.TEXT_DIM,
                 font=C.FONT_MAIN).pack(side="right", padx=(0, 4))

        # Listbox cu scrollbar
        frame = tk.Frame(self, bg=C.BG_PANEL)
        frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        sb = tk.Scrollbar(frame, orient="vertical",
                          bg=C.BG_ITEM, troughcolor=C.BG_DARK)
        sb.pack(side="right", fill="y")

        self._lb = tk.Listbox(frame, yscrollcommand=sb.set,
                              bg=C.BG_ITEM, fg=C.TEXT_MAIN,
                              selectbackground=C.BG_HOVER,
                              selectforeground=C.ACCENT,
                              font=C.FONT_MAIN, relief="flat",
                              activestyle="none", bd=0,
                              highlightthickness=0)
        self._lb.pack(fill="both", expand=True)
        sb.config(command=self._lb.yview)
        self._lb.bind("<<ListboxSelect>>", self._on_lb_select)

        # Buton refresh
        self._refresh_btn = tk.Button(self, text="⟳  Încarcă email-uri",
                                      command=self._on_refresh,
                                      bg=C.BG_HOVER, fg=C.TEXT_MAIN,
                                      font=C.FONT_BOLD, relief="flat",
                                      pady=6, cursor="hand2")
        self._refresh_btn.pack(fill="x", padx=8, pady=(0, 8))

    def _on_lb_select(self, _event):
        sel = self._lb.curselection()
        if sel and self._emails:
            self._on_select(self._emails[sel[0]])

    def _on_refresh(self):
        # Delegat la MainWindow prin callback
        if hasattr(self, "_refresh_callback"):
            self._refresh_callback(self._proto_var.get())

    def set_refresh_callback(self, cb):
        self._refresh_callback = cb

    def load_emails(self, emails: list):
        self._emails = emails
        self._lb.delete(0, "end")
        for em in emails:
            icon = "📎 " if em.has_attachments else "   "
            self._lb.insert("end",
                            f"{icon}{em.short_sender}\n"
                            f"    {em.short_subject}")

    def get_protocol(self) -> str:
        return self._proto_var.get()


class EmailDetailPanel(tk.Frame):
    """ detalii email + atasamente """

    def __init__(self, parent, on_download):
        super().__init__(parent, bg=C.BG_DARK)
        self._on_download = on_download
        self._current_msg = None
        self._build()

    def _build(self):
        # Anteturi
        hdr = tk.Frame(self, bg=C.BG_PANEL, pady=10)
        hdr.pack(fill="x")

        fields = [("De la:", "_lbl_from"), ("Către:", "_lbl_to"),
                  ("Subiect:", "_lbl_subject"), ("Data:", "_lbl_date")]
        for label, attr in fields:
            row = tk.Frame(hdr, bg=C.BG_PANEL)
            row.pack(fill="x", padx=14, pady=1)
            tk.Label(row, text=label, bg=C.BG_PANEL, fg=C.TEXT_DIM,
                     font=C.FONT_BOLD, width=8, anchor="w").pack(side="left")
            lbl = tk.Label(row, text="—", bg=C.BG_PANEL, fg=C.TEXT_MAIN,
                           font=C.FONT_MAIN, anchor="w", wraplength=600)
            lbl.pack(side="left", fill="x", expand=True)
            setattr(self, attr, lbl)

        # Atasamente
        self._attach_frame = tk.Frame(self, bg=C.BG_PANEL)
        self._attach_frame.pack(fill="x")

        self._attach_bar = tk.Frame(self._attach_frame, bg=C.BG_PANEL)

        # Corp email
        body_frame = tk.Frame(self, bg=C.BG_DARK)
        body_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(body_frame, text="Conținut mesaj", bg=C.BG_DARK,
                 fg=C.ACCENT2, font=C.FONT_BOLD).pack(anchor="w", pady=(0, 4))

        self._body_text = scrolledtext.ScrolledText(
            body_frame, bg=C.BG_ITEM, fg=C.TEXT_MAIN,
            font=C.FONT_MONO, relief="flat", state="disabled",
            wrap="word", padx=10, pady=10,
            insertbackground=C.TEXT_MAIN
        )
        self._body_text.pack(fill="both", expand=True)

    def show_email(self, msg):
        """Afiseaza detaliile unui email in panou """
        self._current_msg = msg
        self._lbl_from.config(text=msg.sender or "—")
        self._lbl_to.config(text=msg.recipients or "—")
        self._lbl_subject.config(text=msg.subject or "—")
        self._lbl_date.config(text=msg.date or "—")

        body = msg.body_text or (
            "[Mesaj HTML – nu se poate afișa ca text simplu]"
            if msg.body_html else "(corp gol)")
        self._body_text.config(state="normal")
        self._body_text.delete("1.0", "end")
        self._body_text.insert("end", body)
        self._body_text.config(state="disabled")

        # Atasamente
        for w in self._attach_bar.winfo_children():
            w.destroy()
        self._attach_bar.pack_forget()

        if msg.attachments:
            self._attach_bar.pack(fill="x", padx=10, pady=(0, 6))
            tk.Label(self._attach_bar, text="📎 Atașamente:",
                     bg=C.BG_PANEL, fg=C.ACCENT, font=C.FONT_BOLD).pack(
                side="left", padx=(8, 6))
            for att in msg.attachments:
                tk.Label(self._attach_bar,
                         text=f"{att.filename} ({att.size_kb} KB)",
                         bg=C.BG_ITEM, fg=C.TEXT_MAIN, font=C.FONT_MAIN,
                         padx=8, pady=2).pack(side="left", padx=4)
            tk.Button(self._attach_bar, text="⬇ Salvează atașamentele",
                      command=self._download,
                      bg=C.SUCCESS, fg=C.BG_DARK, font=C.FONT_BOLD,
                      relief="flat", padx=10, cursor="hand2").pack(
                side="right", padx=8, pady=4)

    def _download(self):
        if self._current_msg:
            self._on_download(self._current_msg)

    def clear(self):
        for attr in ("_lbl_from", "_lbl_to", "_lbl_subject", "_lbl_date"):
            getattr(self, attr).config(text="—")
        self._body_text.config(state="normal")
        self._body_text.delete("1.0", "end")
        self._body_text.config(state="disabled")
        self._attach_bar.pack_forget()


class ComposeWindow(tk.Toplevel):
    """
    Fereastra de compunere email
    """

    def __init__(self, parent, conn: EmailConnectionInfo, on_sent):
        super().__init__(parent)
        self.title("✉ Compune email nou")
        self.configure(bg=C.BG_DARK)
        self.geometry("680x540")
        self.grab_set()

        self._conn    = conn
        self._on_sent = on_sent
        self._attachments = []
        self._build()

    def _build(self):
        tk.Label(self, text="✉  Email nou", bg=C.BG_DARK, fg=C.ACCENT,
                 font=C.FONT_TITLE).pack(pady=(14, 8))

        form = tk.Frame(self, bg=C.BG_DARK)
        form.pack(fill="x", padx=20)

        def row(label, var=None, secret=False):
            f = tk.Frame(form, bg=C.BG_DARK)
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label, bg=C.BG_DARK, fg=C.TEXT_DIM,
                     font=C.FONT_BOLD, width=12, anchor="e").pack(side="left")
            if var is None:
                return f
            e = tk.Entry(f, textvariable=var, show="●" if secret else "",
                         bg=C.BG_ITEM, fg=C.TEXT_MAIN,
                         insertbackground=C.TEXT_MAIN,
                         relief="flat", font=C.FONT_MAIN, bd=6)
            e.pack(side="left", fill="x", expand=True, padx=(6, 0))
            return f

        self._to_var       = tk.StringVar()
        self._subject_var  = tk.StringVar()
        self._reply_to_var = tk.StringVar()

        row("Către (To):", self._to_var)
        row("Subiect:", self._subject_var)
        row("Reply-To:", self._reply_to_var)  

        # Atasamente
        att_frame = row("Atașamente:")
        self._att_label = tk.Label(att_frame, text="(niciun fișier)",
                                   bg=C.BG_DARK, fg=C.TEXT_DIM, font=C.FONT_MAIN)
        self._att_label.pack(side="left", padx=(6, 8))
        tk.Button(att_frame, text="+ Adaugă fișier",
                  command=self._add_attachment,
                  bg=C.BG_HOVER, fg=C.TEXT_MAIN,
                  font=C.FONT_MAIN, relief="flat", padx=8,
                  cursor="hand2").pack(side="left")

        # Corp
        tk.Label(self, text="Mesaj:", bg=C.BG_DARK, fg=C.TEXT_DIM,
                 font=C.FONT_BOLD).pack(anchor="w", padx=20, pady=(8, 2))
        self._body_text = scrolledtext.ScrolledText(
            self, bg=C.BG_ITEM, fg=C.TEXT_MAIN, font=C.FONT_MAIN,
            relief="flat", padx=10, pady=8, insertbackground=C.TEXT_MAIN
        )
        self._body_text.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Status
        self._status_lbl = tk.Label(self, text="", bg=C.BG_DARK,
                                    fg=C.SUCCESS, font=C.FONT_MAIN)
        self._status_lbl.pack()

        # Butoane
        btn_frame = tk.Frame(self, bg=C.BG_DARK)
        btn_frame.pack(pady=(0, 14))

        tk.Button(btn_frame, text="✕ Anulează",
                  command=self.destroy,
                  bg=C.BG_HOVER, fg=C.TEXT_MAIN,
                  font=C.FONT_BOLD, relief="flat", padx=14,
                  cursor="hand2").pack(side="left", padx=8)

        tk.Button(btn_frame, text="⟶ Trimite",
                  command=self._send,
                  bg=C.ACCENT, fg=C.BG_DARK,
                  font=C.FONT_BOLD, relief="flat", padx=20,
                  cursor="hand2").pack(side="left", padx=8)

    def _add_attachment(self):
        paths = filedialog.askopenfilenames(title="Selectează fișiere")
        if paths:
            self._attachments.extend(paths)
            names = ", ".join(os.path.basename(p) for p in self._attachments)
            self._att_label.config(
                text=names[:60] + ("…" if len(names) > 60 else ""),
                fg=C.TEXT_MAIN)

    def _send(self):
        data = ComposeEmailData(
            to=self._to_var.get().strip(),
            subject=self._subject_var.get().strip(),
            body=self._body_text.get("1.0", "end").strip(),
            reply_to=self._reply_to_var.get().strip(),
            attachments=list(self._attachments),
        )

        if not data.is_valid():
            messagebox.showwarning("Câmpuri lipsă",
                                   "Completați câmpurile 'Către' și 'Subiect'.")
            return

        self._status_lbl.config(
            text=AppConstants.Messages.SENDING_EMAIL, fg=C.WARNING)
        self.update()

        def worker():
            try:
                svc = EmailServiceFactory.get_smtp_service()
                svc.send_email(self._conn, data)
                self.after(0, lambda: self._sent_ok())
            except Exception as exc:
                self.after(0, lambda: self._sent_err(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _sent_ok(self):
        self._status_lbl.config(
            text=AppConstants.Messages.EMAIL_SENT_SUCCESS, fg=C.SUCCESS)
        self._on_sent(AppConstants.Messages.EMAIL_SENT_SUCCESS)
        self.after(1500, self.destroy)

    def _sent_err(self, err: str):
        self._status_lbl.config(
            text=f"Eroare: {err[:80]}", fg=C.ERROR_COLOR)


class StatusBar(tk.Frame):
    """Bara de stare (jos)."""

    def __init__(self, parent):
        super().__init__(parent, bg=C.BG_PANEL, pady=4)
        self._lbl = tk.Label(self, text="Gata.", bg=C.BG_PANEL,
                             fg=C.TEXT_DIM, font=("Segoe UI", 9),
                             anchor="w")
        self._lbl.pack(side="left", padx=12)

        self._progress = ttk.Progressbar(self, mode="indeterminate",
                                         length=120)

    def set(self, text: str, color: str = None, loading: bool = False):
        self._lbl.config(text=text, fg=color or C.TEXT_DIM)
        if loading:
            self._progress.pack(side="right", padx=12)
            self._progress.start(10)
        else:
            self._progress.stop()
            self._progress.pack_forget()


class MainWindow:
    """
    Fereastra principala a aplicatiei
    """

    def __init__(self):
        self._root = tk.Tk()
        self._root.title(C.WINDOW_TITLE)
        self._root.geometry(C.WINDOW_SIZE)
        self._root.configure(bg=C.BG_DARK)
        self._root.minsize(800, 500)

        self._conn          = EmailConnectionInfo()
        self._current_proto = "IMAP"

        self._build()
        self._apply_style()

    #  Build UI
    def _build(self):
        # Login bar
        self._login = LoginFrame(self._root, on_connect=self._on_connect)
        self._login.pack(fill="x")

        sep = tk.Frame(self._root, bg=C.ACCENT2, height=1)
        sep.pack(fill="x")

        # Toolbar
        toolbar = tk.Frame(self._root, bg=C.BG_PANEL, pady=6)
        toolbar.pack(fill="x")

        tk.Button(toolbar, text="⟳  Reîncarcă",
                  command=self._reload_emails,
                  bg=C.BG_HOVER, fg=C.TEXT_MAIN, font=C.FONT_BOLD,
                  relief="flat", padx=12, cursor="hand2").pack(side="left", padx=8)

        tk.Button(toolbar, text="✉  Email nou",
                  command=self._open_compose,
                  bg=C.ACCENT, fg=C.BG_DARK, font=C.FONT_BOLD,
                  relief="flat", padx=12, cursor="hand2").pack(side="left", padx=4)

        tk.Button(toolbar, text="⬇  Descarcă complet",
                  command=self._download_selected,
                  bg=C.BG_HOVER, fg=C.TEXT_MAIN, font=C.FONT_BOLD,
                  relief="flat", padx=12, cursor="hand2").pack(side="left", padx=4)

        # Panou principal (stanga + dreapta)
        pane = tk.PanedWindow(self._root, orient="horizontal",
                              bg=C.BG_DARK, sashwidth=4,
                              sashrelief="flat", sashpad=2)
        pane.pack(fill="both", expand=True)

        self._list_panel = EmailListPanel(pane, on_select=self._on_email_select)
        self._list_panel.set_refresh_callback(self._load_emails)
        pane.add(self._list_panel, minsize=280)

        self._detail_panel = EmailDetailPanel(
            pane, on_download=self._save_attachments)
        pane.add(self._detail_panel, minsize=400)

        # Status bar
        self._status = StatusBar(self._root)
        self._status.pack(fill="x", side="bottom")

    def _apply_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Horizontal.TProgressbar",
                        background=C.ACCENT, troughcolor=C.BG_ITEM)

    #  Callbacks
    def _on_connect(self, conn: EmailConnectionInfo):
        self._conn = conn
        self._status.set(AppConstants.Messages.CONNECTING_TO_SERVER,
                         loading=True)
        self._load_emails(self._list_panel.get_protocol())

    def _load_emails(self, protocol: str):
        if not self._conn.is_valid():
            messagebox.showwarning("Autentificare",
                                   AppConstants.Messages.ENTER_EMAIL_PASSWORD)
            return

        self._current_proto = protocol
        self._status.set(f"Se încarcă email-uri via {protocol}…",
                         loading=True)
        self._detail_panel.clear()

        def worker():
            try:
                if protocol == "POP3":
                    svc  = EmailServiceFactory.get_pop3_service()
                else:
                    svc  = EmailServiceFactory.get_imap_service()
                emails = svc.get_email_list(self._conn)
                self._root.after(0, lambda: self._emails_loaded(emails, protocol))
            except Exception as exc:
                self._root.after(0, lambda: self._load_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _emails_loaded(self, emails, protocol):
        self._list_panel.load_emails(emails)
        msg = AppConstants.Messages.LOADED_EMAILS_COUNT.format(len(emails))
        self._status.set(f"{msg} via {protocol}", color=C.SUCCESS)
        self._login.set_status(
            f"✓ Conectat – {len(emails)} mesaje", color=C.SUCCESS)

    def _load_error(self, err: str):
        self._status.set(f"Eroare: {err[:100]}", color=C.ERROR_COLOR)
        self._login.set_status(f"✗ {err[:80]}", color=C.ERROR_COLOR)
        messagebox.showerror("Eroare",
                             AppConstants.Messages.ERROR_LOADING_EMAILS.format(err))

    def _reload_emails(self):
        self._load_emails(self._list_panel.get_protocol())

    def _on_email_select(self, email_msg):
        """
        cand utilizatorul selectează un email din lista,
        se descarca versiunea completa (cu corp + atasamente)
        """
        if not self._conn.is_valid():
            return
        self._status.set("Se descarcă email-ul…", loading=True)

        def worker():
            try:
                if self._current_proto == "POP3":
                    svc = EmailServiceFactory.get_pop3_service()
                else:
                    svc = EmailServiceFactory.get_imap_service()
                full = svc.get_email_full(self._conn, email_msg.uid)
                self._root.after(0, lambda: self._show_email(full))
            except Exception as exc:
                self._root.after(0,
                    lambda: self._status.set(f"Eroare: {exc}", color=C.ERROR_COLOR))

        threading.Thread(target=worker, daemon=True).start()

    def _show_email(self, msg):
        self._detail_panel.show_email(msg)
        att_info = (f" – {msg.attachment_count} atașament(e)"
                    if msg.has_attachments else "")
        self._status.set(f"Email afișat{att_info}", color=C.TEXT_MAIN)

    def _download_selected(self):
        """Buton explicit 'Descarcă complet' din toolbar"""
        self._status.set("Selectați un email din listă pentru a-l descărca.",
                         color=C.WARNING)

    def _save_attachments(self, msg):
        """Salveaza atasamentele unui email pe disc"""
        if not msg.attachments:
            messagebox.showinfo("Atașamente", "Email-ul nu are atașamente.")
            return

        directory = filedialog.askdirectory(title="Selectează directorul de salvare")
        if not directory:
            return

        svc   = EmailServiceFactory.get_attachment_service()
        count = svc.save_attachments(msg.attachments, directory)
        msg_text = AppConstants.Messages.DOWNLOADED_ATTACHMENTS_COUNT.format(count)
        self._status.set(msg_text, color=C.SUCCESS)
        messagebox.showinfo("Atașamente salvate",
                            f"{msg_text}\nLocație: {directory}")

    def _open_compose(self):
        """Deschide fereastra de compunere email (criterii 4, 5, 6)"""
        if not self._conn.is_valid():
            messagebox.showwarning("Autentificare",
                                   AppConstants.Messages.ENTER_EMAIL_PASSWORD)
            return
        conn = self._login.get_connection()
        ComposeWindow(self._root, conn,
                      on_sent=lambda m: self._status.set(m, color=C.SUCCESS))

    def run(self):
        self._root.mainloop()
