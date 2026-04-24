import os
from typing import List

from interfaces.email_interfaces import IAttachmentService
from models.email_message import EmailAttachment


class AttachmentService(IAttachmentService):
    #Gestioneaza salvarea atasamentelor pe disc

    def save_attachments(self, attachments: List[EmailAttachment],
                         directory: str) -> int:
        #salveaza lista de atasamente in directorul dat
        #returneaza numarul de fisiere salvate
        if not attachments:
            return 0

        os.makedirs(directory, exist_ok=True)
        saved = 0

        for attachment in attachments:
            try:
                filepath = os.path.join(directory, attachment.filename)
                #evita suprascrierea fisierelor existente
                filepath = self._unique_path(filepath)
                with open(filepath, "wb") as f:
                    f.write(attachment.data)
                saved += 1
            except Exception as e:
                print(f"  [AttachmentService] Eroare la salvare {attachment.filename}: {e}")

        return saved

    def _unique_path(self, filepath: str) -> str:
        """Genereaza un nume unic dacă fisierul există deja"""
        if not os.path.exists(filepath):
            return filepath
        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        return f"{base}_{counter}{ext}"
