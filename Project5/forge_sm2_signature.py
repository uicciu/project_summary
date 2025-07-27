# forge_sm2_signature.py

import argparse
from hashlib import sha256
from random import randint
from binascii import hexlify

from sm2 import SM2


def hash_message(message: bytes) -> int:
    """计算 SHA-256 哈希值（模拟 SM3）"""
    return int(sha256(message).hexdigest(), 16)


def forge_signature(sm2: SM2, message: bytes, private_key: int):
    """使用不安全实现伪造签名（复用 k）"""
    k = randint(1, sm2.n - 1)
    R = sm2.kG(k)
    e = hash_message(message)
    r = (e + R[0]) % sm2.n
    s = (sm2.inv(1 + private_key) * (k - r * private_key)) % sm2.n
    return r, s, k


def run_forgery(message: str):
    sm2 = SM2()

    # 生成攻击者伪造用的私钥
    private_key = randint(1, sm2.n - 1)
    public_key = sm2.kG(private_key)
    message_bytes = message.encode()

    # 伪造签名
    r, s, k = forge_signature(sm2, message_bytes, private_key)

    # 验证签名
    valid = sm2.verify((r, s), message_bytes, public_key)

    print("[*] 伪造 SM2 签名")
    print("消息:", message)
    print("私钥（伪造者）:", hex(private_key))
    print("公钥:", f"({hex(public_key[0])}, {hex(public_key[1])})")
    print("随机数 k:", hex(k))
    print("签名 r =", hex(r))
    print("签名 s =", hex(s))
    print("验证结果:", "通过 ✅" if valid else "失败 ❌")


def main():
    parser = argparse.ArgumentParser(description="SM2 伪造签名演示（重复使用 k 漏洞）")
    parser.add_argument(
        "-m", "--message",
        type=str,
        default="Satoshi Nakamoto's forged SM2 signature.",
        help="要伪造签名的消息内容"
    )
    args = parser.parse_args()
    run_forgery(args.message)


if __name__ == "__main__":
    main()
