import pyotp


def verify_otp(
    secret: str, otp_code: str, method: str = "TOTP", counter: int = 0
) -> bool:
    """Verify a one-time password (TOTP or HOTP)."""
    try:
        if method == "TOTP":
            return pyotp.TOTP(secret).verify(otp_code)
        elif method == "HOTP":
            return pyotp.HOTP(secret).verify(otp_code, counter)
        return False
    except Exception:
        return False
