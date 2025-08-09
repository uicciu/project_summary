# poc/fake_satoshi_signature.py
# Research sketch: attempt to find (r,s) that satisfy verification without secret key via brute force.
# This is expected to fail in general (security property), but script shows reasoning.

import secrets
from src.sm2_core import gen_keypair
from src.utils import hash_msg, bytes_to_int, calc_z
from src.ecc import scalar_mul, point_add, Gx, Gy
from src.sm2_core import G

def demo():
    d, P = gen_keypair()
    ID = b"ALICE"
    M = b"important message"
    Z = calc_z(ID, P[0], P[1])
    e = bytes_to_int(hash_msg(Z + M)) % (2**256)  # demonstration
    print("e (truncated):", e & 0xffffffff)

    # naive small search (extremely unlikely to find solution)
    tries = 2000
    for i in range(tries):
        r = secrets.randbelow(1 << 32)
        s = secrets.randbelow(1 << 32)
        t = (r + s)
        sG = scalar_mul(s, G)
        tP = scalar_mul(t, P)
        X = point_add(sG, tP)
        if X is None:
            continue
        x1 = X[0]
        if (e + x1) % (1 << 32) == r:
            print("Found candidate (r,s) — extremely unlikely in practice:", r, s)
            return
    print("No forged signature found in small search (expected).")

if __name__ == "__main__":
    demo()
