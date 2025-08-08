pragma circom 2.0.0;

// Poseidon2 Hash Circuit for t=3, d=5, with given MDS matrix and constants

template Poseidon2() {
    // 常量定义
    signal input in[2];   // 私有输入，两个元素（x0,x1）
    signal output out;    // 公共输出，哈希值

    // 状态长度 t=3，状态初始为 [x0, x1, 0]
    signal state[3];
    state[0] <== in[0];
    state[1] <== in[1];
    state[2] <== 0;

    // 轮常量（示例，实际请替换为安全生成的常量）
    var fullRounds = 8;
    var partialRounds = 57;
    var totalRounds = fullRounds + partialRounds;

    // 这里用示例常量，实际应由外部生成器生成
    // 轮常量C[r][t]
    signal C[65][3];
    // MDS矩阵
    var M = [
        [1,1,1],
        [1,2,3],
        [1,3,5]
    ];

    // 初始化轮常量为0，方便演示（可修改成实际常量）
    for (var r = 0; r < totalRounds; r++) {
        for (var i = 0; i < 3; i++) {
            C[r][i] <== 0;
        }
    }

    // S-box 幂指数 d=5 的非线性变换函数
    function sbox(x) -> (out) {
        // 计算 x^5 = x * x^2 * x^2
        var x2 = x * x;
        var x4 = x2 * x2;
        out <== x * x4;
    }

    // 轮函数，更新状态
    function roundFunction(stateIn) -> (stateOut) {
        // 添加轮常量
        signal tmp[3];
        for (var i=0; i<3; i++) {
            tmp[i] <== stateIn[i] + C[__r][i];
        }
        // 应用 S-box
        signal sboxed[3];
        for (var i=0; i<3; i++) {
            sboxed[i] <== sbox(tmp[i]);
        }
        // 乘以 MDS 矩阵
        signal newState[3];
        for (var i=0; i<3; i++) {
            var acc = 0;
            for (var j=0; j<3; j++) {
                acc += M[i][j] * sboxed[j];
            }
            newState[i] <== acc;
        }
        return newState;
    }

    // 迭代执行所有轮
    signal stateR[65][3];
    for (var i=0; i<3; i++) {
        stateR[0][i] <== state[i];
    }
    for (var r=0; r<totalRounds; r++) {
        __r = r;
        signal nextState[3];
        nextState <== roundFunction([stateR[r][0], stateR[r][1], stateR[r][2]]);
        for (var i=0; i<3; i++) {
            stateR[r+1][i] <== nextState[i];
        }
    }

    // 输出第 totalRounds 轮的第一个状态元素作为哈希值
    out <== stateR[totalRounds][0];
}

component main = Poseidon2();
