# tests/test_sm2.py
from src.sm2_core import gen_keypair, sign, verify

def test_basic_sign_verify():
    d, P = gen_keypair()
    ID = b"TEST_ID"
    M = b"message for testing"
    r, s = sign(d, ID, M)
    assert verify(P, ID, M, (r, s))

if __name__ == "__main__":
    test_basic_sign_verify()
    print("Test passed")
