#include "sm3.h"
#include <cstring>
#include <iostream>

// --- 常量定义 ---

static const uint32_t IV[8] = {
    0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
    0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
};

static inline uint32_t ROTL(uint32_t x, uint32_t n) {
    return (x << n) | (x >> (32 - n));
}

static inline uint32_t FF(uint32_t x, uint32_t y, uint32_t z, int j) {
    if (j <= 15) return x ^ y ^ z;
    else return (x & y) | (x & z) | (y & z);
}

static inline uint32_t GG(uint32_t x, uint32_t y, uint32_t z, int j) {
    if (j <= 15) return x ^ y ^ z;
    else return (x & y) | ((~x) & z);
}

static inline uint32_t P0(uint32_t x) {
    return x ^ ROTL(x, 9) ^ ROTL(x, 17);
}

static inline uint32_t P1(uint32_t x) {
    return x ^ ROTL(x, 15) ^ ROTL(x, 23);
}

static const uint32_t T_j[64] = {
    0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519,
    0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519, 0x79CC4519,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A,
    0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A, 0x7A879D8A
};

// --- 内部函数声明 ---

static void sm3_compress(SM3_CTX* ctx, const uint8_t block[64]);
static void sm3_padding(SM3_CTX* ctx, uint8_t out[SM3_DIGEST_LENGTH]);

// --- API 实现 ---

void sm3_init(SM3_CTX* ctx) {
    std::memcpy(ctx->state, IV, sizeof(IV));
    ctx->length = 0;
    ctx->buf_used = 0;
}

void sm3_update(SM3_CTX* ctx, const uint8_t* data, size_t len) {
    ctx->length += len * 8; // bit length
    while (len > 0) {
        size_t space = 64 - ctx->buf_used;
        size_t to_copy = (len < space) ? len : space;
        std::memcpy(ctx->buffer + ctx->buf_used, data, to_copy);
        ctx->buf_used += to_copy;
        data += to_copy;
        len -= to_copy;
        if (ctx->buf_used == 64) {
            sm3_compress(ctx, ctx->buffer);
            ctx->buf_used = 0;
        }
    }
}

void sm3_final(SM3_CTX* ctx, uint8_t out[SM3_DIGEST_LENGTH]) {
    sm3_padding(ctx, out);
}

std::vector<uint8_t> sm3_hash(const uint8_t* data, size_t len) {
    SM3_CTX ctx;
    uint8_t digest[SM3_DIGEST_LENGTH];
    sm3_init(&ctx);
    sm3_update(&ctx, data, len);
    sm3_final(&ctx, digest);
    return std::vector<uint8_t>(digest, digest + SM3_DIGEST_LENGTH);
}

// --- 核心压缩函数 ---

static void sm3_compress(SM3_CTX* ctx, const uint8_t block[64]) {
    uint32_t W[68], W_prime[64];
    // 消息扩展
    for (int i = 0; i < 16; ++i) {
        W[i] = (block[i * 4] << 24) | (block[i * 4 + 1] << 16) | (block[i * 4 + 2] << 8) | (block[i * 4 + 3]);
    }
    for (int j = 16; j < 68; ++j) {
        uint32_t tmp = W[j - 16] ^ W[j - 9] ^ ROTL(W[j - 3], 15);
        W[j] = P1(tmp) ^ ROTL(W[j - 13], 7) ^ W[j - 6];
    }
    for (int j = 0; j < 64; ++j) {
        W_prime[j] = W[j] ^ W[j + 4];
    }

    // 初始化寄存器
    uint32_t A = ctx->state[0];
    uint32_t B = ctx->state[1];
    uint32_t C = ctx->state[2];
    uint32_t D = ctx->state[3];
    uint32_t E = ctx->state[4];
    uint32_t F = ctx->state[5];
    uint32_t G = ctx->state[6];
    uint32_t H = ctx->state[7];

    for (int j = 0; j < 64; ++j) {
        uint32_t SS1 = ROTL((ROTL(A, 12) + E + ROTL(T_j[j], j)) & 0xFFFFFFFF, 7);
        uint32_t SS2 = SS1 ^ ROTL(A, 12);
        uint32_t TT1 = (FF(A, B, C, j) + D + SS2 + W_prime[j]) & 0xFFFFFFFF;
        uint32_t TT2 = (GG(E, F, G, j) + H + SS1 + W[j]) & 0xFFFFFFFF;
        D = C;
        C = ROTL(B, 9);
        B = A;
        A = TT1;
        H = G;
        G = ROTL(F, 19);
        F = E;
        E = P0(TT2);
    }

    ctx->state[0] ^= A;
    ctx->state[1] ^= B;
    ctx->state[2] ^= C;
    ctx->state[3] ^= D;
    ctx->state[4] ^= E;
    ctx->state[5] ^= F;
    ctx->state[6] ^= G;
    ctx->state[7] ^= H;
}

// --- 填充函数 ---

static void sm3_padding(SM3_CTX* ctx, uint8_t out[SM3_DIGEST_LENGTH]) {
    size_t i = ctx->buf_used;
    ctx->buffer[i++] = 0x80;
    if (i > 56) {
        while (i < 64) ctx->buffer[i++] = 0x00;
        sm3_compress(ctx, ctx->buffer);
        i = 0;
    }
    while (i < 56) ctx->buffer[i++] = 0x00;

    // 消息长度64bit大端写入
    uint64_t len_be = ctx->length;
    for (int j = 7; j >= 0; --j) {
        ctx->buffer[i++] = (len_be >> (8 * j)) & 0xFF;
    }
    sm3_compress(ctx, ctx->buffer);

    // 输出摘要
    for (i = 0; i < 8; ++i) {
        out[i * 4] = (ctx->state[i] >> 24) & 0xFF;
        out[i * 4 + 1] = (ctx->state[i] >> 16) & 0xFF;
        out[i * 4 + 2] = (ctx->state[i] >> 8) & 0xFF;
        out[i * 4 + 3] = ctx->state[i] & 0xFF;
    }
}
