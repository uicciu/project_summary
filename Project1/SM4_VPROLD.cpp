// SM4 Implementation with SIMD and VPROLD-based Linear Transform Optimization (no AES-NI)
#include <cstdint>
#include <cstring>
#include <immintrin.h>
#include <iostream>
#include <chrono>

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
    static const uint8_t SBOX[256] = {
        0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7,
        0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
        // (truncated for brevity)
    };
    for (int i = 0; i < 4; ++i) a[i] = SBOX[a[i]];
    uint32_t B;
    memcpy(&B, a, 4);
    return B;
}

uint32_t L_vprold(uint32_t B) {
    __m128i v = _mm_set1_epi32(B);
    __m128i r2  = _mm_rol_epi32(v, 2);
    __m128i r10 = _mm_rol_epi32(v, 10);
    __m128i r18 = _mm_rol_epi32(v, 18);
    __m128i r24 = _mm_rol_epi32(v, 24);
    __m128i res = _mm_xor_si128(v, _mm_xor_si128(r2, _mm_xor_si128(r10, _mm_xor_si128(r18, r24))));
    return _mm_extract_epi32(res, 0);
}

uint32_t T(uint32_t x) {
    return L_vprold(tau(x));
}

void SM4_KeyExpansion(const uint8_t key[16], uint32_t rk[32]) {
    const uint32_t FK[4] = {0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc};
    uint32_t K[36];
    for (int i = 0; i < 4; ++i) {
        K[i] = ((uint32_t*)key)[i] ^ FK[i];
    }
    for (int i = 0; i < 32; ++i) {
        uint32_t tmp = K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i];
        uint32_t t = T(tmp);
        K[i + 4] = K[i] ^ t;
        rk[i] = K[i + 4];
    }
}

void SM4_Encrypt_SIMD(const uint8_t in[16], uint8_t out[16], const uint32_t rk[32]) {
    __m128i x = _mm_loadu_si128((__m128i*)in);
    uint32_t* X = (uint32_t*)&x;
    uint32_t tmp[36];
    tmp[0] = X[0]; tmp[1] = X[1]; tmp[2] = X[2]; tmp[3] = X[3];

    for (int i = 0; i < 32; ++i)
        tmp[i + 4] = tmp[i] ^ T(tmp[i + 1] ^ tmp[i + 2] ^ tmp[i + 3] ^ rk[i]);

    uint32_t result[4] = {tmp[35], tmp[34], tmp[33], tmp[32]};
    _mm_storeu_si128((__m128i*)out, _mm_loadu_si128((__m128i*)result));
}

int main() {
    uint8_t key[16] = {0x01};
    uint8_t plain[16] = {0x00};
    uint8_t cipher[16];
    uint32_t rk[32];
    SM4_KeyExpansion(key, rk);

    constexpr int ROUNDS = 100000;

    auto start_simd = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < ROUNDS; ++i)
        SM4_Encrypt_SIMD(plain, cipher, rk);
    auto end_simd = std::chrono::high_resolution_clock::now();

    auto duration_simd = std::chrono::duration_cast<std::chrono::microseconds>(end_simd - start_simd).count();

    std::cout << "VPROLD L() SIMD: " << duration_simd << " us for " << ROUNDS << " rounds\n";

    return 0;
}
