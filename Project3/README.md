
# Project3: Implement the Circuit of Poseidon2 Hash Algorithm using Circom

## 目录
- [项目概述](#项目概述)
- [Poseidon2 算法结构](#poseidon2-算法结构)
- [项目要求](#项目要求)
- [文件结构](#文件结构)
- [编译与证明流程](#编译与证明流程)
- [数学原理](#数学原理)
- [测试](#测试)
- [参考](#参考)

## 项目概述
本项目实现了 **Poseidon2** 哈希函数的 Circom 电路，并使用 **Groth16** 算法生成证明与验证。

Poseidon2 是一种基于置换结构的 ZK 友好哈希函数，主要特点是利用 **MDS 矩阵** 和 **幂指数 S-box** 进行多轮迭代变换。  
我们使用参数：
- $n = 256$：有限域元素位宽。
- $t = 3$：状态向量长度。
- $d = 5$：S-box 指数。

---

## Poseidon2 算法结构
Poseidon2 哈希函数主要分为 **全轮（Full Rounds）** 和 **部分轮（Partial Rounds）**，其状态更新公式为：

1. **状态初始化：**

$$
\mathbf{x}^{(0)} = [m_0, m_1, 0]
$$

3. **轮函数（Round Function）：**
对于每一轮 $r$，更新公式为：

$$
\mathbf{x}^{(r+1)} = M \cdot S(\mathbf{x}^{(r)} + \mathbf{C}^{(r)})
$$

其中：

- $\mathbf{C}^{(r)}$ 是第 $ r $ 轮的常量向量。
- $S(\cdot)$ 是逐元素应用的 S-box：

$$
S(x) = x^d \pmod p
$$

- $M$ 是 MDS 矩阵（Maximum Distance Separable），确保混合性。

3. **输出：**

$$
h = x_0^{(R)}
$$

其中 $R = R_F + R_P$ 为总轮数。

---

## 项目要求

- 公共输入：Poseidon2 哈希值 $h$。
- 私有输入：哈希原像 $[m_0, m_1]$。
- 仅考虑一个 block 的输入。
- 使用 Groth16 算法生成零知识证明。

---

## 文件结构
```
Project3/
│
├── circuits/
│   ├── poseidon2.circom        # Poseidon2 电路实现
│   ├── poseidon2_test.circom   # 测试电路
│
├── test/
│   └── poseidon2_test.js       # 使用 snarkjs 测试电路
│
├── build/
│   ├── poseidon2.r1cs          # 编译后的电路文件
│   ├── poseidon2.wasm          # 电路生成的 WASM
│   ├── poseidon2_0000.zkey     # 初始 ZKey
│   ├── poseidon2_final.zkey    # 最终 ZKey
│   └── verification_key.json   # 验证密钥
│
├── input.json                  # 示例输入文件
├── proof.json                  # Groth16 证明文件
├── public.json                 # 公共输入文件
├── README.md                   # 项目说明
└── package.json
```

---

## 编译与证明流程
### 1. 编译电路
```bash
circom circuits/poseidon2.circom --r1cs --wasm --sym -o build/
```

### 2. 生成可信设置
```bash
snarkjs groth16 setup build/poseidon2.r1cs powersOfTau28_hez_final_10.ptau build/poseidon2_0000.zkey
snarkjs zkey contribute build/poseidon2_0000.zkey build/poseidon2_final.zkey
snarkjs zkey export verificationkey build/poseidon2_final.zkey build/verification_key.json
```

### 3. 生成证明
```bash
snarkjs groth16 prove build/poseidon2_final.zkey input.json proof.json public.json
```

### 4. 验证证明
```bash
snarkjs groth16 verify build/verification_key.json public.json proof.json
```

---

## 数学原理
Poseidon2 的安全性来自于其置换结构和 MDS 矩阵的扩散性。  
其核心 S-box 使用奇数指数 $d=5$，保证代数免疫性。

MDS 矩阵示例（t=3）：

$$
M = \begin{pmatrix}
1 & 1 & 1 \\
1 & 2 & 3 \\
1 & 3 & 5
\end{pmatrix}
$$

---

## 测试
使用 Node.js 测试：
```bash
node test/poseidon2_test.js
```

---

## 参考
1. Poseidon2 哈希算法参考文档。
2. [Circom 官方文档](https://docs.circom.io/)
3. [snarkjs 官方文档](https://github.com/iden3/snarkjs)


