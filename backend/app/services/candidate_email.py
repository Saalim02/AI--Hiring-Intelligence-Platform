"""Safe extraction of contact details from resume text."""
import re
from dataclasses import dataclass
from email_validator import EmailNotValidError, validate_email

EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9.-]+)(?![\w.-])", re.I)


@dataclass(frozen=True)
class EmailExtraction:
    email: str | None
    status: str
    candidate_name: str | None


def _possible_name(text: str, email: str | None) -> str | None:
    for line in text.splitlines()[:12]:
        value = " ".join(line.strip().split())
        if not value or (email and email.lower() in value.lower()) or "@" in value:
            continue
        if re.search(r"(?:https?://|\+?\d[\d ()-]{6,})", value):
            continue
        if any(token in value.lower() for token in ("resume", "curriculum vitae", "phone", "email", "linkedin", "github")):
            continue
        words = value.split()
        if 2 <= len(words) <= 4 and all(re.fullmatch(r"[A-Za-z][A-Za-z.'-]*", word) for word in words):
            return value[:200]
    return None


def extract_candidate_email(text: str) -> EmailExtraction:
    raw = list(dict.fromkeys(match.group(1).strip(".,;:()[]<>").lower() for match in EMAIL_RE.finditer(text or "")))
    valid: list[str] = []
    for value in raw:
        try:
            valid.append(validate_email(value, check_deliverability=False).normalized)
        except EmailNotValidError:
            continue
    if len(valid) > 1:
        return EmailExtraction(None, "ambiguous", _possible_name(text, None))
    if not valid:
        return EmailExtraction(None, "missing" if not raw else "invalid", _possible_name(text, None))
    return EmailExtraction(valid[0], "valid", _possible_name(text, valid[0]))
