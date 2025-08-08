#include <iostream>
#include <vector>
#include <string>
#include <cassert>
#include <algorithm>
#include <cstring>
#include "sm3.h"  // 需要有 sm3_hash(uint8_t*, size_t) 返回 std::vector<uint8_t>，长度32

using ByteVec = std::vector<uint8_t>;

// 辅助：打印16进制
std::string to_hex(const ByteVec& data) {
    static const char* hex_chars = "0123456789abcdef";
    std::string hex;
    for (auto b : data) {
        hex.push_back(hex_chars[b >> 4]);
        hex.push_back(hex_chars[b & 0xF]);
    }
    return hex;
}

// Merkle树节点结构
struct MerkleNode {
    ByteVec hash;
    MerkleNode* left;
    MerkleNode* right;
    MerkleNode(const ByteVec& h) : hash(h), left(nullptr), right(nullptr) {}
};

// 计算两个hash拼接的hash
ByteVec hash_concat(const ByteVec& left_hash, const ByteVec& right_hash) {
    ByteVec combined;
    combined.reserve(left_hash.size() + right_hash.size());
    combined.insert(combined.end(), left_hash.begin(), left_hash.end());
    combined.insert(combined.end(), right_hash.begin(), right_hash.end());
    return sm3_hash(combined.data(), combined.size());
}

// 构建Merkle树，返回根节点指针
MerkleNode* build_merkle_tree(const std::vector<ByteVec>& leaves) {
    if (leaves.empty()) return nullptr;

    // 创建叶节点
    std::vector<MerkleNode*> nodes;
    for (const auto& leaf : leaves) {
        nodes.push_back(new MerkleNode(leaf));
    }

    // 如果叶子数不是2的幂，重复最后一个叶子直到满足
    while ((nodes.size() & (nodes.size() -1)) != 0) {
        nodes.push_back(new MerkleNode(nodes.back()->hash));
    }

    // 自底向上合并
    while (nodes.size() > 1) {
        std::vector<MerkleNode*> parents;
        for (size_t i = 0; i < nodes.size(); i += 2) {
            ByteVec parent_hash = hash_concat(nodes[i]->hash, nodes[i+1]->hash);
            MerkleNode* parent = new MerkleNode(parent_hash);
            parent->left = nodes[i];
            parent->right = nodes[i+1];
            parents.push_back(parent);
        }
        nodes = std::move(parents);
    }

    return nodes[0];
}

// 生成认证路径，返回路径hash列表（从叶到根）
bool merkle_proof(MerkleNode* root, const ByteVec& target_leaf, std::vector<ByteVec>& proof, MerkleNode* current=nullptr) {
    if (!current) current = root;
    if (!current) return false;

    // 如果当前节点是叶子
    if (!current->left && !current->right) {
        return current->hash == target_leaf;
    }

    // 在左子树查找
    if (merkle_proof(current->left, target_leaf, proof)) {
        proof.push_back(current->right->hash);
        return true;
    }
    // 在右子树查找
    if (merkle_proof(current->right, target_leaf, proof)) {
        proof.push_back(current->left->hash);
        return true;
    }

    return false;
}

// 验证认证路径
bool verify_merkle_proof(const ByteVec& root_hash, const ByteVec& leaf, const std::vector<ByteVec>& proof, size_t index) {
    ByteVec hash = leaf;
    size_t idx = index;
    for (const auto& sibling_hash : proof) {
        if (idx % 2 == 0) {
            hash = hash_concat(hash, sibling_hash);
        } else {
            hash = hash_concat(sibling_hash, hash);
        }
        idx /= 2;
    }
    return hash == root_hash;
}

// 释放树内存
void free_merkle_tree(MerkleNode* node) {
    if (!node) return;
    free_merkle_tree(node->left);
    free_merkle_tree(node->right);
    delete node;
}

int main() {
    std::vector<std::string> data = {"apple", "banana", "cherry", "date", "elderberry"};
    std::vector<ByteVec> leaves;

    // 计算叶子hash
    for (const auto& s : data) {
        ByteVec hash = sm3_hash((const uint8_t*)s.data(), s.size());
        leaves.push_back(hash);
        std::cout << "Leaf: " << s << " hash: " << to_hex(hash) << std::endl;
    }

    // 构建Merkle树
    MerkleNode* root = build_merkle_tree(leaves);
    std::cout << "Merkle root hash: " << to_hex(root->hash) << std::endl;

    // 生成认证路径
    size_t target_index = 2; // cherry
    std::vector<ByteVec> proof;
    bool found = merkle_proof(root, leaves[target_index], proof);
    if (!found) {
        std::cerr << "Leaf not found in tree" << std::endl;
        free_merkle_tree(root);
        return 1;
    }

    std::cout << "Proof path hashes (bottom to top):" << std::endl;
    for (const auto& h : proof) {
        std::cout << to_hex(h) << std::endl;
    }

    // 验证认证路径
    bool valid = verify_merkle_proof(root->hash, leaves[target_index], proof, target_index);
    std::cout << "Verification result: " << (valid ? "valid" : "invalid") << std::endl;

    free_merkle_tree(root);
    return 0;
}
