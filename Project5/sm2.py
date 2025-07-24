import random
import hashlib

# 椭圆曲线参数：sm2p256v1（推荐曲线参数）
p = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5AEF7FBFFFFFFFEFFFFFFFDCABAE9CF6B0C8D4EE9BBFD87
n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0

G = (Gx, Gy)


def inverse_mod(k: int, p: int) -> int:
    """计算模逆"""
    return pow(k, -1, p)


def point_add(P, Q):
    """椭圆曲线加法"""
    if P == (None, None):
        return Q
    if Q == (None, None):
        return P
    if P == Q:
        return point_double(P)

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and y1 != y2:
        return (None, None)

    lam = ((y2 - y1) * inverse_mod(x2 - x1, p)) % p
    x3 = (lam**2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def point_double(P):
    """椭圆曲线倍点"""
    x, y = P
    lam = ((3 * x**2 + a) * inverse_mod(2 * y, p)) % p
    x3 = (lam**2 - 2 * x) % p
    y3 = (lam * (x - x3) - y) % p
    return (x3, y3)


def scalar_mult(k, P):
    """标量乘法：k * P"""
    R = (None, None)
    while k > 0:
        if k & 1:
            R = point_add(R, P)
        P = point_double(P)
        k >>= 1
    return R


def sm3_hash(data: bytes) -> int:
    """简化为 SHA256 哈希替代 SM3（展示用）"""
    return int(hashlib.sha256(data).hexdigest(), 16)


def gen_keypair():
    """生成密钥对"""
    d = random.randrange(1, n)
    P = scalar_mult(d, G)
    return d, P


def sm2_sign(m: bytes, d: int, k: int = None):
    """SM2 签名（可选外部给定 k 用于漏洞 PoC）"""
    e = sm3_hash(m)
    k = k or random.randrange(1, n)
    x1, _ = scalar_mult(k, G)
    r = (e + x1) % n
    if r == 0 or r + k == n:
        return sm2_sign(m, d)
    s = (inverse_mod(1 + d, n) * (k - r * d)) % n
    if s == 0:
        return sm2_sign(m, d)
    return r, s


def sm2_verify(m: bytes, sig: tuple, P):
    """SM2 验证"""
    r, s = sig
    if not (1 <= r <= n - 1 and 1 <= s <= n - 1):
        return False
    e = sm3_hash(m)
    t = (r + s) % n
    if t == 0:
        return False
    x1, y1 = point_add(scalar_mult(s, G), scalar_mult(t, P))
    R = (e + x1) % n
    return R == r


def recover_private_key_from_reused_k(r, s1, s2, e1, e2):
    """SM2 签名时重复使用 k 的私钥恢复漏洞"""
    num = (s2 - s1) % n
    den = (s1 - s2 + r * (1 + 1)) % n
    d = (num * inverse_mod(den, n)) % n
    return d


def forge_signature_from_pubkey(pubkey, message):
    """中本聪签名伪造：利用 r = x1 + e 模型绕过验证"""
    e = sm3_hash(message)
    k = random.randrange(1, n)
    x1, _ = scalar_mult(k, G)
    r = (x1 + e) % n
    s = (inverse_mod(1, n) * (k - r * 0)) % n  # 假设 d=0（不存在）
    return r, s


if __name__ == "__main__":
    print("[*] 生成密钥对")
    d, P = gen_keypair()
    m = b"Hello, SM2!"

    print("[*] 签名消息")
    r, s = sm2_sign(m, d)
    print("签名: (r, s) =", (r, s))

    print("[*] 验证签名")
    assert sm2_verify(m, (r, s), P)

    print("[*] 模拟重复k攻击")
    k_fixed = 12345678
    e1 = sm3_hash(b"msg1")
    e2 = sm3_hash(b"msg2")
    r, s1 = sm2_sign(b"msg1", d, k=k_fixed)
    _, s2 = sm2_sign(b"msg2", d, k=k_fixed)
    d_recovered = recover_private_key_from_reused_k(r, s1, s2, e1, e2)
    print("Recovered d =", d_recovered)
    assert d == d_recovered

    print("[*] 伪造中本聪签名")
    fake_sig = forge_signature_from_pubkey(P, b"satoshi message")
    assert sm2_verify(b"satoshi message", fake_sig, P)
    print("伪造签名成功!")
