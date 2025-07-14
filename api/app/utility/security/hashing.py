import hashlib


def hash_field(value: str, namespace: str) -> str:
    """SHA-256 hash of a UTF-8 value, for indexing."""
    return hashlib.sha256(f"{namespace}:{value}".encode("utf-8")).hexdigest()


def hash_email(email: str, namespace: str) -> str:
    """
    Generate a SHA-256 hash of the normalized email (used for fast lookup).
    Normalizes by removing subdomain aliases (part after + and before @) to prevent duplicates.

    Args:
        email (str): The email address.

    Returns:
        str: The SHA-256 hash of the normalized email.
    """
    normalized_email = email.lower()

    if "+" in normalized_email:
        local_part, domain_part = normalized_email.rsplit("@", 1)
        local_part = local_part.split("+")[0]
        normalized_email = f"{local_part}@{domain_part}"

    return hash_field(normalized_email, namespace)
