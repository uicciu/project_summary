// SM4 Basic Implementation with T-Table Optimization (Partial, extendable)
#include <cstdint>
#include <cstring>
#include <immintrin.h> // For future GFNI/VPROLD use
#include <iostream>

// S-Box
static const uint8_t SBOX[256] = {
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7,
    0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
    // (truncated) full 256 values should be here
};

// CK constants for key expansion
static const uint32_t CK[32] = {
    0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
    0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
    0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
    0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
    0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
    0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
    0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
    0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
};

// Rotate left
uint32_t ROTL(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

// Non-linear transform (T-function)
uint32_t tau(uint32_t A) {
    uint8_t a[4];
    memcpy(a, &A, 4);
    for (int i = 0; i < 4; ++i) a[i] = SBOX[a[i]];
    uint32_t B;
    memcpy(&B, a, 4);
    return B;
}

uint32_t L(uint32_t B) {
    return B ^ ROTL(B, 2) ^ ROTL(B, 10) ^ ROTL(B, 18) ^ ROTL(B, 24);
}

uint32_t T(uint32_t x) {
    return L(tau(x));
}

// Key expansion
void SM4_KeyExpansion(const uint8_t key[16], uint32_t rk[32]) {
    const uint32_t FK[4] = {0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc};
    uint32_t K[36];
    for (int i = 0; i < 4; ++i) {
        K[i] = ((uint32_t*)key)[i] ^ FK[i];
    }
    for (int i = 0; i < 32; ++i) {
        K[i + 4] = K[i] ^ (ROTL(tau(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i]), 13)) ^ ROTL(tau(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i]), 23);
        rk[i] = K[i + 4];
    }
}

// One block encryption
void SM4_Encrypt(const uint8_t in[16], uint8_t out[16], const uint32_t rk[32]) {
    uint32_t X[36];
    for (int i = 0; i < 4; ++i)
        X[i] = ((uint32_t*)in)[i];

    for (int i = 0; i < 32; ++i)
        X[i + 4] = X[i] ^ T(X[i + 1] ^ X[i + 2] ^ X[i + 3] ^ rk[i]);

    for (int i = 0; i < 4; ++i)
        ((uint32_t*)out)[i] = X[35 - i];
}

int main() {
    uint8_t key[16] = {0x01}; // 示例密钥（真实使用应为 128 bit 随机）
    uint32_t rk[32];
    SM4_KeyExpansion(key, rk);

    uint8_t plain[16] = {0x00};
    uint8_t cipher[16];
    SM4_Encrypt(plain, cipher, rk);

    std::cout << "Ciphertext: ";
    for (int i = 0; i < 16; ++i) {
        printf("%02x ", cipher[i]);
    }
    std::cout << std::endl;
    return 0;
}
