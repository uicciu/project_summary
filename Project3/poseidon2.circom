pragma circom 2.0.0;

/**
 * Poseidon2 Hash Function Circuit
 * Parameters: n = 256, t = 3, d = 5
 *
 * Public input: hash output
 * Private input: preimage [m0, m1]
 */

template Poseidon2() {
    signal input preimage[2];   // 私有输入
    signal input hash;          // 公共输入

    // Poseidon2 常量参数
    var t = 3;
    var R_F = 8;   // full rounds
    var R_P = 56;  // partial rounds
    var d = 5;     // S-box exponent

    signal state[t];

    // 初始化状态
    state[0] <== preimage[0];
    state[1] <== preimage[1];
    state[2] <== 0;

    // AddRoundKey + S-box 全轮
    for (var r = 0; r < R_F + R_P; r++) {
        // S-box
        if (r < R_F/2 || r >= R_F/2 + R_P) {
            for (var i = 0; i < t; i++) {
                state[i] <== state[i] ** d;
            }
        } else {
            state[0] <== state[0] ** d;
        }

        // MDS 矩阵混合 (简单 MDS 例子)
        var tmp[t];
        tmp[0] <== state[0] + state[1] + state[2];
        tmp[1] <== state[0] + 2*state[1] + 3*state[2];
        tmp[2] <== state[0] + 3*state[1] + 5*state[2];

        for (var i = 0; i < t; i++) {
            state[i] <== tmp[i];
        }
    }

    // 检查最终 hash 是否匹配
    hash === state[0];
}

component main = Poseidon2();
