# poc/poc_k_reuse.py
# Demonstrate private key recovery when same k used in two signatures (educational).

import secrets
from src.sm2_core import gen_keypair, sign
from src.ecc import n, modinv
from src.utils import hash_msg, bytes_to_int

# We'll monkeypatch secrets.randbelow to force reuse of k in the sign function
fixed_k = 1234567890123456789012345678901234567890 % n

_original_randbelow = secrets.randbelow

def fixed_randbelow(x):
    # secrets.randbelow(x) returns [0, x-1]; we want k in [1, n-1]
    # return fixed_k - 1 to keep in that convention
    return (fixed_k - 1) % (x)

def recover_d_from_two_sigs(r1, s1, r2, s2):
    num = (s2 - s1) % n
    den = (s1 + r1 - s2 - r2) % n
    if den == 0:
        raise ValueError("Cannot invert denominator (den==0).")
    d_rec = (num * modinv(den, n)) % n
    return d_rec

def demo():
    d, P = gen_keypair()
    ID = b"ALICE"
    m1 = b"msg one"
    m2 = b"msg two"

    # patch to reuse k
    secrets.randbelow = fixed_randbelow
    r1, s1 = sign(d, ID, m1)
    r2, s2 = sign(d, ID, m2)
    secrets.randbelow = _original_randbelow

    print("Signatures:")
    print("r1,s1 =", r1, s1)
    print("r2,s2 =", r2, s2)

    d_rec = recover_d_from_two_sigs(r1, s1, r2, s2)
    print("Recovered d equals original?", d_rec == d)
    print("Original d:", d)
    print("Recovered d:", d_rec)

if __name__ == "__main__":
    demo()
