import hashlib
import json
import time


class CertificateBlockchain:
    BLOCK_SIZE = 10

    @staticmethod
    def calculate_hash(certificate_data: dict, previous_hash: str, nonce: int) -> str:
        block_string = json.dumps({
            'data': certificate_data,
            'previous_hash': previous_hash,
            'nonce': nonce,
            'timestamp': certificate_data.get('issued_date', ''),
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    @staticmethod
    def mine_block(certificate_data: dict, previous_hash: str = '0' * 64) -> dict:
        nonce = 0
        target = '0000'  # Difficulty: hash must start with 4 zeros

        while True:
            cert_hash = CertificateBlockchain.calculate_hash(certificate_data, previous_hash, nonce)
            if cert_hash.startswith(target):
                return {
                    'hash': cert_hash,
                    'previous_hash': previous_hash,
                    'nonce': nonce,
                    'data': certificate_data,
                }
            nonce += 1

    @staticmethod
    def verify_certificate(certificate_data: dict, cert_hash: str, previous_hash: str, nonce: int) -> bool:
        calculated_hash = CertificateBlockchain.calculate_hash(certificate_data, previous_hash, nonce)
        return calculated_hash == cert_hash

    @staticmethod
    def generate_qr_data(cert_hash: str) -> str:
        return f"https://ediv-portal.onrender.com/api/blockchain-certs/verify/?hash={cert_hash}"

    @staticmethod
    def generate_certificate_data(student, school, cert_type, title, issued_date, extra_data=None) -> dict:
        return {
            'student_name': student.user.get_full_name(),
            'student_id': student.student_id,
            'school_name': school.name,
            'school_code': school.school_code,
            'certificate_type': cert_type,
            'title': title,
            'issued_date': str(issued_date),
            'grade': extra_data.get('grade', '') if extra_data else '',
            'score': extra_data.get('score', '') if extra_data else '',
            'programme': extra_data.get('programme', '') if extra_data else '',
        }
