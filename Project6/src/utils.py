# utils.py
import random
from hashlib import sha256

# 大素数 p，用于群 G (这里用 2^521-1 模拟)
p = 2 ** 521 - 1

def hash_to_group(identifier: str) -> int:
    """将标识符哈希映射到群元素"""
    h = sha256(identifier.encode()).digest()
    return int.from_bytes(h, 'big') % p

def shuffle_with_indices(data):
    """打乱列表顺序并返回打乱后列表和对应原索引"""
    indices = list(range(len(data)))
    random.shuffle(indices)
    shuffled = [data[i] for i in indices]
    return shuffled, indices

def unshuffle(data, indices):
    """根据索引恢复列表原始顺序"""
    unshuffled = [None] * len(data)
    for i, idx in enumerate(indices):
        unshuffled[idx] = data[i]
    return unshuffled
