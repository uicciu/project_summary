# poc/poc_missing_z.py
# Demonstrate why omitting Z (i.e. using e = H(M) instead of H(Z||M)) weakens binding to identity.

from src.sm2_core import gen_keypair
from src.utils import hash_msg, bytes_to_int
from src.ecc import n, scalar_mul, Gx, Gy
from src.sm2_core import G
import secrets
from src.sm2_core import verify

def demo():
    d, P = gen_keypair()
    ID1 = b"ALICE"
    ID2 = b"BOB"
    M = b"transfer $100"

    # Incorrect signing: e = H(M) (omitting Z)
    e = bytes_to_int(hash_msg(M)) % n
    k = secrets.randbelow(n - 1) + 1
    x1y1 = scalar_mul(k, G)
    x1 = x1y1[0]
    r = (e + x1) % n
    inv = pow(1 + d, -1, n)
    s = (inv * (k - r * d)) % n
    sig = (r, s)

    print("Signature (r,s):", sig)
    # Proper verify (with correct Z) should succeed for correct ID only
    ok1 = verify(P, ID1, M, sig)
    ok2 = verify(P, ID2, M, sig)
    print("Verify with ID1 (proper):", ok1)
    print("Verify with ID2 (proper):", ok2)
    print("Note: If system validates only against H(M) naive check, signature may be misapplied across IDs.")

if __name__ == "__main__":
    demo()
