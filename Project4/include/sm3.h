#ifndef SM3_H
#define SM3_H

#include <cstdint>
#include <cstddef>
#include <vector>
#include <string>

#define SM3_DIGEST_LENGTH 32

struct SM3_CTX {
    uint32_t state[8];   // 链值
    uint64_t length;     // 已处理比特长度
    uint8_t buffer[64];  // 缓冲区
    size_t buf_used;     // 缓冲字节数
};

void sm3_init(SM3_CTX* ctx);
void sm3_update(SM3_CTX* ctx, const uint8_t* data, size_t len);
void sm3_final(SM3_CTX* ctx, uint8_t digest[SM3_DIGEST_LENGTH]);
std::vector<uint8_t> sm3_hash(const uint8_t* data, size_t len);

// 长度扩展攻击接口示例
std::pair<std::vector<uint8_t>, std::vector<uint8_t>> sm3_length_extension_attack(
    const uint8_t orig_digest[SM3_DIGEST_LENGTH], 
    size_t orig_len_bytes, 
    const uint8_t* ext_msg, size_t ext_len);

// Merkle树核心接口示例
using ByteArray = std::vector<uint8_t>;
ByteArray sm3_merkle_hash(const std::vector<ByteArray>& leaves);
std::vector<ByteArray> sm3_merkle_proof(const std::vector<ByteArray>& leaves, size_t idx);
bool sm3_verify_merkle_proof(const ByteArray& root, const ByteArray& leaf, 
                             const std::vector<ByteArray>& proof, size_t idx);

#endif
