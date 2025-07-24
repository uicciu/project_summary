import hashlib
from gmssl import sm3, func
from random import randint
from ecdsa import ellipticcurve, curves

# 使用 secp256k1 曲线（比特币使用的曲线）
curve = curves.SECP256k1.curve
G = curves.SECP256k1.generator
n = G.order()

# 哈希函数（比特币一般用 SHA256，也可以替换成 SM3）
def hash_message(msg: str):
    return int(hashlib.sha256(msg.encode()).hexdigest(), 16)

# 计算 r, s（SM2 与 ECDSA 类似）
def sm2_sign(msg_hash: int, d: int, k: int):
    P = k * G
    r = (msg_hash + P.x()) % n
    s = ((k - r * d) * pow(1 + d, -1, n)) % n
    return r, s

# 伪造签名（复用 k）
def forge_signature(msg1, msg2, r, s1, s2):
    e1 = hash_message(msg1)
    e2 = hash_message(msg2)

    numerator = (s2 - s1) % n
    denominator = (e2 - e1) % n
    k = (numerator * pow(denominator, -1, n)) % n
    d = ((k - s1) * pow(r + s1, -1, n)) % n
    return k, d

# 模拟攻击流程
def main():
    msg1 = "I am Satoshi Nakamoto"
    msg2 = "I donate 1000 BTC to ChatGPT"

    # 合法私钥（用于模拟签名者）
    d = randint(1, n-1)
    P = d * G

    print(f"[真实私钥 d] = {hex(d)}")
    print(f"[公钥 P] = ({hex(P.x())}, {hex(P.y())})")

    # 攻击者观察到两个消息使用相同的随机数 k 签名
    k = randint(1, n-1)
    e1 = hash_message(msg1)
    e2 = hash_message(msg2)

    r1, s1 = sm2_sign(e1, d, k)
    r2, s2 = sm2_sign(e2, d, k)

    assert r1 == r2  # r 相同
    print(f"[攻击者捕获签名1] r = {hex(r1)}, s = {hex(s1)}")
    print(f"[攻击者捕获签名2] r = {hex(r2)}, s = {hex(s2)}")

    # 开始伪造
    k_recovered, d_recovered = forge_signature(msg1, msg2, r1, s1, s2)

    print(f"[伪造者恢复的 k] = {hex(k_recovered)}")
    print(f"[伪造者恢复的 d] = {hex(d_recovered)}")
    assert d_recovered == d

    # 用恢复的 d 对任意消息签名
    forged_r, forged_s = sm2_sign(hash_message("Send 1000 BTC to attacker"), d_recovered, randint(1, n-1))
    print(f"[伪造签名] r = {hex(forged_r)}, s = {hex(forged_s)}")

if __name__ == "__main__":
    main()
