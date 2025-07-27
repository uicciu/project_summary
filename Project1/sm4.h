#ifndef SM4_H
#define SM4_H

#include <cstdint>
#include <array>

class SM4 {
public:
    using Block = std::array<uint8_t, 16>;
    using Key = std::array<uint8_t, 16>;

    SM4();
    void setKey(const Key& key, bool isEncrypt = true);
    void encryptBlock(const Block& in, Block& out);
    void decryptBlock(const Block& in, Block& out);

protected:
    void keyExpansion(const Key& key, bool isEncrypt);
    uint32_t T(uint32_t x);          // 非线性变换
    uint32_t L(uint32_t b);          // 线性变换

    std::array<uint32_t, 32> rk;     // 轮密钥
};

#endif // SM4_H
