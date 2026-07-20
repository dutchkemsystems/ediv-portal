import pyotp


def generate_mfa_secret():
    """Generate a random 32-char base32 secret for TOTP."""
    return pyotp.random_base32(length=32)


def get_mfa_qr_code_url(secret, email):
    """Return the otpauth:// URL for QR code generation."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name='Education District IV')


def verify_mfa_code(secret, code):
    """Verify a TOTP code (allow 1 step drift)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def get_mfa_provisioning_uri(secret, email, issuer='Education District IV'):
    """Full provisioning URI for TOTP setup."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)
