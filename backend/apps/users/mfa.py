import base64
import io

import pyotp


def generate_mfa_secret():
    """Generate a random 32-char base32 secret for TOTP."""
    return pyotp.random_base32(length=32)


def get_mfa_qr_code_url(secret, email):
    """Generate a QR code data URL for MFA setup.

    Returns a base64-encoded PNG data URI that can be rendered directly
    in an <img> tag. Falls back to otpauth:// URI if qrcode is unavailable.
    """
    uri = f'otpauth://totp/Education%20District%20IV:{email}?secret={secret}&issuer=Education%20District%20IV'
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f'data:image/png;base64,{img_base64}'
    except ImportError:
        # Fallback: return the otpauth URI (user must enter manually)
        return uri


def verify_mfa_code(secret, code):
    """Verify a TOTP code (allow 1 step drift)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def get_mfa_provisioning_uri(secret, email, issuer='Education District IV'):
    """Full provisioning URI for TOTP setup."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)
