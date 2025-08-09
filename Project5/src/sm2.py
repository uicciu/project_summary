# sm2.py

import os
import random
from gmssl import sm3, func

# ===== 调试模式配置 =====
DEBUG_FIXED_KEYS = True   # 固定私钥/公钥
DEBUG_FIXED_K    = True   # 固定签名随机数 k

FIXED_PRIVATE_KEY = int(
    "128D97B99C874D5443E4D2F2A9FA9130EBF2B7E9E1E5D7A441BDCE3D1F2A29AC", 16
)

FIXED_K = int(
    "1F1E1D1C1B1A191817161514131211100F0E0D0C0B0A09080706050403020100", 16
)
# ======================

# 椭圆曲线参数（SM2推荐参数）
p  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b  = 0x28E9FA9E9D9F5E344D5AEF7F6BFFFF5F
Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
n  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123

G = (Gx, Gy)

# 椭圆曲线加法和乘法（略，可用你已有的实现）

class SM2:
    def __init__(self, private_key=None, public_key=None):
        if DEBUG_FIXED_KEYS:
            self.private_key = FIXED_PRIVATE_KEY
            self.public_key = self._point_mul(self.private_key, G)
        else:
            self.private_key = private_key
            self.public_key = public_key

    def sign(self, message):
        e = self._hash_message(message)

        if DEBUG_FIXED_K:
            k = FIXED_K % n
        else:
            k = random.randint(1, n - 1)

        x1, y1 = self._point_mul(k, G)
        r = (e + x1) % n
        if r == 0 or r + k == n:
            return self.sign(message)

        d = self.private_key
        s = pow(1 + d, -1, n) * (k - r * d) % n
        if s == 0:
            return self.sign(message)

        return (r, s)

    def verify(self, message, signature):
        # 验证逻辑同你原来的版本
        pass

    def _hash_message(self, message):
        # SM3 哈希（可加上 Z 计算）
        digest_hex = sm3.sm3_hash(func.bytes_to_list(message.encode()))
        return int(digest_hex, 16)

    def _point_mul(self, k, P):
        # 椭圆曲线点乘实现
        pass
