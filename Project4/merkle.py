from sm3 import sm3_hash

class MerkleTree:
    def __init__(self, leaves):
        self.leaves = leaves
        self.levels = []
        self.build_tree()
    
    def build_tree(self):
        level = [bytes.fromhex(leaf) if isinstance(leaf, str) else leaf for leaf in self.leaves]
        self.levels.append(level)
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i+1] if i+1 < len(level) else left
                combined = left + right
                next_level.append(bytes.fromhex(sm3_hash(combined)) if isinstance(combined, bytes) else combined)
            level = next_level
            self.levels.append(level)
    
    def root(self):
        return self.levels[-1][0].hex()

    def get_proof(self, idx):
        proof = []
        for level in self.levels[:-1]:
            sibling_idx = idx ^ 1
            if sibling_idx < len(level):
                proof.append(level[sibling_idx].hex())
            idx >>= 1
        return proof
    
    def verify_proof(self, leaf, proof, root):
        computed_hash = leaf
        for sibling in proof:
            combined = bytes.fromhex(computed_hash) + bytes.fromhex(sibling)
            computed_hash = sm3_hash(combined)
        return computed_hash == root
