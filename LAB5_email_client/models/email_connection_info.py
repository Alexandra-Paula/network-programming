from dataclasses import dataclass, field

@dataclass
class EmailConnectionInfo:
    email:    str = ""
    password: str = ""

    def is_valid(self) -> bool:
        return bool(self.email.strip()) and bool(self.password.strip())

    def __repr__(self):
        return f"EmailConnectionInfo(email={self.email!r}, password=***)"
