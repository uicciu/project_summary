# party.py
import secrets
from phe import paillier
from utils import p, hash_to_group, shuffle_with_indices

class Party1:
    """持有标识符集合的参与方"""
    def __init__(self, identifiers):
        self.V = identifiers
        self.k1 = secrets.randbelow(p - 1) + 1
        self.Z = None
        self.public_key = None
        self.intersection_size = 0

    def receive_public_key(self, pk):
        self.public_key = pk

    def round1_send_hashed(self):
        self.V_hashed = [pow(hash_to_group(v), self.k1, p) for v in self.V]
        self.V_hashed, self.shuffle_idx = shuffle_with_indices(self.V_hashed)
        return self.V_hashed

    def receive_Z(self, Z):
        self.Z = set(Z)  # 转为集合方便查找

    def round3_compute_intersection_sum(self, data_from_p2):
        # data_from_p2: List of tuples (hashed, encrypted value)
        matched_ciphertexts = []
        for h_val, enc_val in data_from_p2:
            val = pow(h_val, self.k1, p)
            if val in self.Z:
                matched_ciphertexts.append(enc_val)
        self.intersection_size = len(matched_ciphertexts)
        if not matched_ciphertexts:
            return self.public_key.encrypt(0)
        total_enc = matched_ciphertexts[0]
        for ct in matched_ciphertexts[1:]:
            total_enc += ct
        return total_enc

class Party2:
    """持有标识符和值对的参与方"""
    def __init__(self, items):
        self.W = items
        self.k2 = secrets.randbelow(p - 1) + 1
        self.public_key, self.private_key = paillier.generate_paillier_keypair()

    def get_public_key(self):
        return self.public_key

    def round2_process_and_send(self, hashed_from_p1):
        Z = [pow(h, self.k2, p) for h in hashed_from_p1]

        processed = []
        for w, t in self.W:
            hw = pow(hash_to_group(w), self.k2, p)
            ct = self.public_key.encrypt(t)
            processed.append((hw, ct))

        processed, _ = shuffle_with_indices(processed)
        return Z, processed

    def round3_decrypt_sum(self, encrypted_sum):
        return self.private_key.decrypt(encrypted_sum)
