import struct

IV = [
    0x7380166F,
    0x4914B2B9,
    0x172442D7,
    0xDA8A0600,
    0xA96F30BC,
    0x163138AA,
    0xE38DEE4D,
    0xB0FB0E4E,
]

T_j = [0x79CC4519] * 16 + [0x7A879D8A] * 48

def rotate_left(x, n):
    return ((x << n) & 0xFFFFFFFF) | (x >> (32 - n))

def FF_j(X, Y, Z, j):
    if 0 <= j <= 15:
        return X ^ Y ^ Z
    else:
        return (X & Y) | (X & Z) | (Y & Z)

def GG_j(X, Y, Z, j):
    if 0 <= j <= 15:
        return X ^ Y ^ Z
    else:
        return (X & Y) | (~X & Z)

def P_0(X):
    return X ^ rotate_left(X, 9) ^ rotate_left(X, 17)

def P_1(X):
    return X ^ rotate_left(X, 15) ^ rotate_left(X, 23)

def padding(msg):
    l = len(msg) * 8
    msg += b'\x80'
    while (len(msg) * 8) % 512 != 448:
        msg += b'\x00'
    msg += struct.pack('>Q', l)
    return msg

def msg_extend(B):
    W = []
    for i in range(16):
        W.append(struct.unpack('>I', B[i*4:i*4+4])[0])
    for j in range(16, 68):
        W.append(P_1(W[j-16] ^ W[j-9] ^ rotate_left(W[j-3], 15)) ^ rotate_left(W[j-13], 7) ^ W[j-6])
    W_1 = []
    for j in range(64):
        W_1.append(W[j] ^ W[j+4])
    return W, W_1

def CF(V_i, B_i):
    W, W_1 = msg_extend(B_i)
    A, B, C, D, E, F, G, H = V_i
    for j in range(64):
        SS1 = rotate_left((rotate_left(A, 12) + E + rotate_left(T_j[j], j)) & 0xFFFFFFFF, 7)
        SS2 = SS1 ^ rotate_left(A, 12)
        TT1 = (FF_j(A, B, C, j) + D + SS2 + W_1[j]) & 0xFFFFFFFF
        TT2 = (GG_j(E, F, G, j) + H + SS1 + W[j]) & 0xFFFFFFFF
        D = C
        C = rotate_left(B, 9)
        B = A
        A = TT1
        H = G
        G = rotate_left(F, 19)
        F = E
        E = P_0(TT2)
    V_j = [A ^ V_i[0], B ^ V_i[1], C ^ V_i[2], D ^ V_i[3],
           E ^ V_i[4], F ^ V_i[5], G ^ V_i[6], H ^ V_i[7]]
    return V_j

def sm3_hash(msg):
    msg = padding(msg)
    n = len(msg) // 64
    V = IV
    for i in range(n):
        B_i = msg[i*64:(i+1)*64]
        V = CF(V, B_i)
    result = b''.join(struct.pack('>I', x) for x in V)
    return result.hex()
