# demo_basic.py
from src.sm2_core import gen_keypair, sign, verify

ID = b"ALICE123@EXAMPLE.COM"
M = b"Hello, this is a message to sign."

def main():
    d, P = gen_keypair()
    print("Private key d:", hex(d))
    print("Public key P:", (hex(P[0]), hex(P[1])))
    r, s = sign(d, ID, M)
    print("Signature r, s:", hex(r), hex(s))
    ok = verify(P, ID, M, (r, s))
    print("Verification:", ok)

if __name__ == "__main__":
    main()
