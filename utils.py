import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # a-z, A-Z, 0-9 (Base62)


def generate_short_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))