// SM4 Implementation with T-Table Optimization and Timing Comparison
#include <cstdint>
#include <cstring>
#include <immintrin.h>
#include <iostream>
#include <chrono>

// S-Box
static const uint8_t SBOX[256] = {
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7,
    0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
    // (truncated for brevity)
};

static uint32_t TTable[256];

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

uint32_t ROTL(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

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

uint32_t T_TTABLE(uint32_t x) {
    uint8_t *b = (uint8_t*)&x;
    return TTable[b[0]] ^ ROTL(TTable[b[1]], 8) ^ ROTL(TTable[b[2]], 16) ^ ROTL(TTable[b[3]], 24);
}

void SM4_KeyExpansion(const uint8_t key[16], uint32_t rk[32]) {
    const uint32_t FK[4] = {0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc};
    uint32_t K[36];
    for (int i = 0; i < 4; ++i) {
        K[i] = ((uint32_t*)key)[i] ^ FK[i];
    }
    for (int i = 0; i < 32; ++i) {
        uint32_t tmp = K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i];
        uint8_t *b = (uint8_t*)&tmp;
        uint32_t t = TTable[b[0]] ^ ROTL(TTable[b[1]], 8) ^ ROTL(TTable[b[2]], 16) ^ ROTL(TTable[b[3]], 24);
        K[i + 4] = K[i] ^ t ^ ROTL(t, 13) ^ ROTL(t, 23);
        rk[i] = K[i + 4];
    }
}

void SM4_Encrypt_TTABLE(const uint8_t in[16], uint8_t out[16], const uint32_t rk[32]) {
    uint32_t X[36];
    for (int i = 0; i < 4; ++i)
        X[i] = ((uint32_t*)in)[i];

    for (int i = 0; i < 32; ++i)
        X[i + 4] = X[i] ^ T_TTABLE(X[i + 1] ^ X[i + 2] ^ X[i + 3] ^ rk[i]);

    for (int i = 0; i < 4; ++i)
        ((uint32_t*)out)[i] = X[35 - i];
}

void SM4_Encrypt_BASE(const uint8_t in[16], uint8_t out[16], const uint32_t rk[32]) {
    uint32_t X[36];
    for (int i = 0; i < 4; ++i)
        X[i] = ((uint32_t*)in)[i];

    for (int i = 0; i < 32; ++i)
        X[i + 4] = X[i] ^ T(X[i + 1] ^ X[i + 2] ^ X[i + 3] ^ rk[i]);

    for (int i = 0; i < 4; ++i)
        ((uint32_t*)out)[i] = X[35 - i];
}

void init_ttable() {
    for (int i = 0; i < 256; ++i) {
        uint32_t x = i << 24;
        TTable[i] = L(tau(x));
    }
}

int main() {
    init_ttable();

    uint8_t key[16] = {0x01};
    uint8_t plain[16] = {0x00};
    uint8_t cipher[16];
    uint32_t rk[32];
    SM4_KeyExpansion(key, rk);

    constexpr int ROUNDS = 100000;

    auto start_base = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ROUNDS; ++i)
        SM4_Encrypt_BASE(plain, cipher, rk);
    auto end_base = std::chrono::high_resolution_clock::now();

    auto start_ttbl = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ROUNDS; ++i)
        SM4_Encrypt_TTABLE(plain, cipher, rk);
    auto end_ttbl = std::chrono::high_resolution_clock::now();

    auto duration_base = std::chrono::duration_cast<std::chrono::microseconds>(end_base - start_base).count();
    auto duration_ttbl = std::chrono::duration_cast<std::chrono::microseconds>(end_ttbl - start_ttbl).count();

    std::cout << "Base T(): " << duration_base << " us for " << ROUNDS << " rounds\n";
    std::cout << "T-Table : " << duration_ttbl << " us for " << ROUNDS << " rounds\n";

    return 0;
}
