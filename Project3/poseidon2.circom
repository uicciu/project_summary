pragma circom 2.1.6;

template Poseidon2() {
    signal input in[2];      // 两个输入
    signal output out;       // 单个输出（哈希结果）

    // 参数定义
    var t = 3;               // 状态向量长度
    var R_F = 8;             // 全轮数（示意值）
    var R_P = 57;            // 部分轮数（示意值）
    var e = 5;               // S-box 指数

    signal state[t];

    // 初始化
    state[0] <== in[0];
    state[1] <== in[1];
    state[2] <== 0; // capacity

    // 常数（仅演示，请替换为真实 Poseidon2 常数）
    component sbox[t];
    var c = [1,2,3,4,5,6,7,8]; // round constants（简化）
    var mds = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]; // MDS矩阵（简化）

    var r = 0;
    for (var i = 0; i < R_F + R_P; i++) {
        // 加 round constant
        for (var j = 0; j < t; j++) {
            state[j] <== state[j] + c[r % c.length];
            r++;
        }

        // S-box 应用
        for (var j = 0; j < t; j++) {
            signal s;
            s <== state[j] ** e;
            state[j] <== s;
        }

        // MDS 乘法
        var new_state = [];
        for (var j = 0; j < t; j++) {
            signal sum = 0;
            for (var k = 0; k < t; k++) {
                sum <== sum + state[k] * mds[j][k];
            }
            new_state.push(sum);
        }

        for (var j = 0; j < t; j++) {
            state[j] <== new_state[j];
        }
    }

    out <== state[0]; // 输出前半状态作为哈希结果
}

component main = Poseidon2();
