# src/utils.py
# Utility functions: hashing, Z calculation, conversions

import hashlib
from typing import Tuple

try:
    from gmssl import sm3
    HAS_SM3 = True
except Exception:
    HAS_SM3 = False

from .ecc import a, b, Gx, Gy

def hash_msg(msg: bytes) -> bytes:
    """
    Compute hash. Prefer SM3 if gmssl installed; otherwise fallback to SHA-256.
    Returns raw bytes.
    """
    if HAS_SM3:
        # gmssl.sm3.sm3_hash accepts a list of byte values and returns hex string
        return bytes.fromhex(sm3.sm3_hash(list(msg)))
    else:
        return hashlib.sha256(msg).digest()


def int_to_bytes(x: int, length: int) -> bytes:
    return x.to_bytes(length, byteorder='big')


def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, byteorder='big')


def calc_z(ID: bytes, Px: int, Py: int) -> bytes:
    """
    Calculate Z per SM2:
    Z = H(ENTL || ID || a || b || Gx || Gy || Px || Py)
    ENTL is ID length in bits, 2 bytes big-endian.
    """
    entl = (len(ID) * 8).to_bytes(2, 'big')
    data = bytearray()
    data += entl
    data += ID
    for val in (a, b, Gx, Gy, Px, Py):
        data += int_to_bytes(val, 32)
    return hash_msg(bytes(data))
