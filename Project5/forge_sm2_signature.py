# forge_sm2_signature.py

from sm2 import SM2
from hashlib import sha256
from random import randint
from binascii import hexlify

# 模拟SM2参数
sm2 = SM2()

# 假设私钥（由攻击者伪造签名用，目标是伪造成中本聪）
private_key = randint(1, sm2.n - 1)
public_key = sm2.kG(private_key)

# 攻击者想要伪造的数据
message = b"Satoshi Nakamoto's forged SM2 signature."

# 计算消息哈希
e = int(sha256(message).hexdigest(), 16)

# 漏洞利用场景：使用不安全的签名实现（例如直接复用 k）
# 选择一个随机 k 并复用（或由泄露获得）
k = randint(1, sm2.n - 1)
R = sm2.kG(k)
r = (e + R[0]) % sm2.n
s = (sm2.inv(1 + private_key) * (k - r * private_key)) % sm2.n

assert r != 0 and s != 0

print("伪造签名:")
print("Message:", message.decode())
print("r =", hex(r))
print("s =", hex(s))

# 验证伪造签名是否通过
print("\n验证结果:", sm2.verify((r, s), message, public_key))
