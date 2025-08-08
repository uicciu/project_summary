#include <iostream>
#include <vector>
#include <cstring>
#include <cassert>
#include "sm3.h"

// 计算 SM3 填充，返回填充数据（不含原消息，只含填充）
// input_len 是原消息长度（字节）
std::vector<uint8_t> sm3_padding_for_length(size_t input_len) {
    uint64_t bit_len = input_len * 8;

    // 先加一个0x80
    std::vector<uint8_t> pad = {0x80};

    // 计算需要补多少0，保证 (len + 1 + k) % 64 = 56（64字节=512bit，56字节后跟8字节长度）
    size_t pad_zero_len = (56 - (input_len + 1) % 64) % 64;
    pad.insert(pad.end(), pad_zero_len, 0);

    // 再加64bit大端长度
    for (int i = 7; i >= 0; --i) {
        pad.push_back((bit_len >> (8 * i)) & 0xFF);
    }
    return pad;
}

// 将16进制摘要（字符串）转为字节数组
std::vector<uint8_t> hex_to_bytes(const std::string& hex) {
    std::vector<uint8_t> bytes;
    assert(hex.size() % 2 == 0);
    for (size_t i = 0; i < hex.size(); i += 2) {
        uint8_t b = (uint8_t) std::stoi(hex.substr(i, 2), nullptr, 16);
        bytes.push_back(b);
    }
    return bytes;
}

// 将字节数组打印为16进制字符串
std::string bytes_to_hex(const std::vector<uint8_t>& data) {
    static const char* hex_chars = "0123456789abcdef";
    std::string hex;
    for (auto b : data) {
        hex.push_back(hex_chars[b >> 4]);
        hex.push_back(hex_chars[b & 0xF]);
    }
    return hex;
}

// 长度扩展攻击核心
// orig_digest: 原始SM3摘要（32字节）
// orig_len_bytes: 原消息长度（字节），需要猜测
// ext_msg, ext_len: 追加的扩展消息
// 返回值：伪造的新摘要，伪造的消息输入（原消息未知，只给伪造填充和扩展消息）
std::pair<std::vector<uint8_t>, std::vector<uint8_t>> sm3_length_extension_attack(
    const uint8_t orig_digest[SM3_DIGEST_LENGTH],
    size_t orig_len_bytes,
    const uint8_t* ext_msg, size_t ext_len)
{
    // 1. 构造伪造输入 = 原消息 || padding || ext_msg
    std::vector<uint8_t> forged_input;
    // 因为不知道原消息，通常攻击者只能构造伪造的输入：
    // 伪造输入 = padding_for(orig_len_bytes) + ext_msg
    // 用于传递给服务器验证的消息是:
    // 真实消息 || padding || ext_msg
    // 这里我们直接构造伪造输入为 padding + ext_msg，
    // 实际使用时原消息会在服务器端拼接

    std::vector<uint8_t> padding = sm3_padding_for_length(orig_len_bytes);
    forged_input.reserve(padding.size() + ext_len);
    forged_input.insert(forged_input.end(), padding.begin(), padding.end());
    forged_input.insert(forged_input.end(), ext_msg, ext_msg + ext_len);

    // 2. 恢复内部状态寄存器V_i
    SM3_CTX ctx;
    // SM3 digest 32字节对应8个32位寄存器
    for (int i = 0; i < 8; ++i) {
        ctx.state[i] = 
            (orig_digest[i * 4] << 24) | (orig_digest[i * 4 + 1] << 16) |
            (orig_digest[i * 4 + 2] << 8) | (orig_digest[i * 4 + 3]);
    }

    // 3. 设置ctx的已处理消息总长度(bit)
    // 这里长度是原消息 + padding 的总bit数
    ctx.length = (orig_len_bytes + padding.size()) * 8;

    // 4. 缓冲区为空
    ctx.buf_used = 0;

    // 5. 用ctx继续更新扩展消息
    sm3_update(&ctx, ext_msg, ext_len);

    // 6. 计算伪造摘要
    uint8_t new_digest[SM3_DIGEST_LENGTH];
    sm3_final(&ctx, new_digest);

    std::vector<uint8_t> forged_digest(new_digest, new_digest + SM3_DIGEST_LENGTH);

    return {forged_digest, forged_input};
}

int main() {
    // 测试示例
    const std::string orig_msg = "user=alice";
    const size_t secret_len = 16; // 猜测的 secret 长度（字节）

    // 假设服务器计算 token = SM3(secret || orig_msg)
    // 我们只知道 token，原始消息长度 = secret_len + orig_msg.size()
    // 这里演示原消息就是 secret || orig_msg，secret为全0方便测试

    std::vector<uint8_t> secret(secret_len, 0);
    std::vector<uint8_t> orig_msg_bytes(orig_msg.begin(), orig_msg.end());

    std::vector<uint8_t> full_msg = secret;
    full_msg.insert(full_msg.end(), orig_msg_bytes.begin(), orig_msg_bytes.end());

    auto orig_digest = sm3_hash(full_msg.data(), full_msg.size());
    std::cout << "Original digest: " << bytes_to_hex(orig_digest) << std::endl;

    // 攻击者构造扩展消息 ext_msg
    const std::string ext_str = "&admin=true";
    std::vector<uint8_t> ext_msg(ext_str.begin(), ext_str.end());

    // 进行长度扩展攻击
    auto [new_digest, forged_input] = sm3_length_extension_attack(
        orig_digest.data(),
        secret_len + orig_msg.size(),
        ext_msg.data(),
        ext_msg.size());

    std::cout << "Forged digest:   " << bytes_to_hex(new_digest) << std::endl;

    // 验证（服务器端模拟）
    std::vector<uint8_t> server_msg = full_msg; // secret || orig_msg
    auto padding = sm3_padding_for_length(server_msg.size());
    server_msg.insert(server_msg.end(), padding.begin(), padding.end());
    server_msg.insert(server_msg.end(), ext_msg.begin(), ext_msg.end());

    auto verify_digest = sm3_hash(server_msg.data(), server_msg.size());

    std::cout << "Verify digest:   " << bytes_to_hex(verify_digest) << std::endl;

    assert(new_digest == verify_digest);
    std::cout << "Length extension attack successful!" << std::endl;

    return 0;
}
