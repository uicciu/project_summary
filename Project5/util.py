# utils.py
# SM2 椭圆曲线基础工具函数

p = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5AEF7FBFFFFFFFEFFFFFFFDCABAE9CF6B0C8D4EE9BBFD87

def inverse_mod(k, p):
    """计算 k 关于模 p 的逆元"""
    if k == 0:
        raise ZeroDivisionError('division by zero')
    return pow(k, -1, p)

def is_on_curve(P):
    """判断点 P=(x,y) 是否在椭圆曲线上"""
    if P is None:
        return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0

def point_add(P, Q):
    """椭圆曲线加法"""
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and y1 != y2:
        return None

    if P == Q:
        lam = (3 * x1 * x1 + a) * inverse_mod(2 * y1, p) % p
    else:
        lam = (y2 - y1) * inverse_mod(x2 - x1, p) % p

    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p

    return (x3, y3)

def scalar_mult(k, P):
    """标量乘法 k*P"""
    R = None
    addend = P

    while k > 0:
        if k & 1:
            R = point_add(R, addend)
        addend = point_add(addend, addend)
        k >>= 1

    return R
