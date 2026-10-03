import hashlib

SALT = "microguard_privacy_salt_v1"  # move to an env var later if you want it configurable


def hash_value(value: str) -> str:
    if not value:
        return value
    return hashlib.sha256((SALT + value).encode("utf-8")).hexdigest()[:16]