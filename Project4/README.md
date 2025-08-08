# Project 4: Software Implementation and Optimization of SM3

> **目标**：基于国密哈希算法 SM3 的软件实现，进行高效优化，并实现相关安全验证与应用（长度扩展攻击 & Merkle 树构建）。

---

## 目录

- [1. 项目概览](#1-项目概览)
- [2. SM3 简介](#2-sm3-简介)
  - [2.1 算法特点](#21-算法特点)
  - [2.2 SM3 与 SHA-256 对比](#22-sm3-与-sha-256-对比)
- [3. 项目要求](#3-项目要求)
  - [3.1 基础实现](#31-基础实现)
  - [3.2 软件优化](#32-软件优化)
  - [3.3 长度扩展攻击](#33-长度扩展攻击)
  - [3.4 Merkle 树构建](#34-merkle-树构建)
- [4. 数学模型与算法](#4-数学模型与算法)
  - [4.1 SM3 消息填充与分组](#41-sm3-消息填充与分组)
  - [4.2 消息扩展](#42-消息扩展)
  - [4.3 压缩函数](#43-压缩函数)
  - [4.4 常量、布尔函数与置换](#44-常量布尔函数与置换)
  - [4.5 哈希总体流程](#45-哈希总体流程)
- [5. 项目结构](#5-项目结构)
- [6. 性能测试](#8-性能测试)
  - [6.1 测试维度与指标](#81-测试维度与指标)
  - [6.2 SIMD/多线程测试注意事项](#83-simd多线程测试注意事项)
- [7. 实验示例](#9-实验示例)
  - [7.1 长度扩展攻击结果](#91-长度扩展攻击结果)
  - [7.2 Merkle 树存在性证明结果](#92-merkle-树存在性证明结果)
- [8. 参考文献](#10-参考文献)

---

## 1. 项目概览

本项目围绕 **SM3 哈希算法** 的软件实现与应用展开，包括：

- **从零实现 SM3**（参考国密标准）。
- **逐步优化执行效率**（算法级优化、SIMD 指令、循环展开、缓存友好数据布局等）。
- **长度扩展攻击验证**：构造 \(H(m \Vert \text{pad}(m) \Vert m_2)\) 并复用中间状态。
- **Merkle 树构建与验证**：支持大规模（≥ 100k）叶子节点，提供存在性/不存在性证明接口，可参考 RFC 6962 风格认证路径。

本仓库既可作为学习 SM3 的教学示例，也可作为性能实验平台，用于探索在不同硬件环境下的优化策略（x86 AVX2/AVX-512、ARM NEON、RISC-V V 扩展等）。

---

## 2. SM3 简介

### 2.1 算法特点

SM3 是中国商用密码标准哈希函数（GB/T 32905-2016），输出 256 位摘要，主要用于数字签名、消息完整性、身份认证等场景。

其结构与 SHA-256 类似，采用 **Merkle–Damgård** 构造，对输入消息进行分组迭代压缩。核心特点：

- 输出固定 256 bit。
- 每 512 bit 为一分组输入压缩函数。
- 总计 64 轮迭代运算。
- 使用布尔函数 $FF_j, GG_j$（分前 16 轮 / 后 48 轮两种形式）。
- 使用线性/非线性置换 $P_0, P_1$。
- 消息扩展生成 $W_j, W'_j$ 序列，为压缩函数提供混淆与扩散。

### 2.2 SM3 与 SHA-256 对比

| 算法      | 输出长度    | 安全级别（设计目标） | 结构                 | 性能（软件典型）   | 应用生态 |
| ------- | ------- | ---------- | ------------------ | ---------- | ---- |
| SHA-256 | 256 bit | 国际标准       | Merkle–Damgård     | 普遍较快       | 广泛   |
| SM3     | 256 bit | 国密标准       | Merkle–Damgård(变体) | 略低/相近（依实现） | 国密生态 |

> **注意**：实际性能高度依赖实现质量（字节序处理、循环展开、SIMD 并行）。在部分平台上优化后的 SM3 可达到或超过未优化 SHA-256 实现。

---

## 3. 项目要求

### 3.1 基础实现

- 严格遵循国密标准，实现 `sm3_hash(msg)`：输入任意长度消息，输出 32 字节（256 bit）摘要。
- 同时提供流式接口：`init` / `update` / `final`。
- 输出十六进制字符串（小写）。

### 3.2 软件优化

目标：在典型硬件上获得可衡量的吞吐提升。你应至少实现以下一种或多种优化：

- **算法级优化**：
  - 减少消息拷贝；
  - 合并大小端转换与装载；
  - 延迟计算或按需展开 $W_j$；
  - 减少模运算（32-bit 整数溢出即自然模）。
- **SIMD/并行化**：
  - x86: SSE2 / AVX2 / AVX-512；
  - ARM: NEON；
  - GPU 或多核批处理（可选）。
- **查表 / 常量折叠**：预旋转 $T_j$，预生成掩码。
- **循环展开**：按 8 或 16 轮展开，减少分支预测影响。

### 3.3 长度扩展攻击

SM3 采用 Merkle–Damgård 填充，因此存在与 SHA-256 类似的 **长度扩展攻击**：若攻击者已知 $H(m)$ 且不知道 $m$，但知道或能猜测 $|m|$，则可构造：

$$
H(m \Vert \text{pad}(m) \Vert m_2)
$$

无需知道原始消息即可伪造扩展消息的摘要。

你需要：

- 实现 `length_extension_attack(orig_digest, orig_len_bytes, extension_msg)`；
- 输出伪造的新摘要与伪造输入；
- 编写验证脚本，调用正规 SM3 实现确认攻击成功。

### 3.4 Merkle 树构建

- 使用 SM3 作为叶子/内部节点哈希函数；
- 支持 ≥100,000 个叶子节点；
- 提供：
  - `build_merkle(leaves)` 返回 root；
  - `merkle_proof(leaves, idx)` 返回认证路径；
  - `verify_merkle_proof(root, leaf, path, idx)`；
  - **不存在性证明（Sorted Merkle Tree）**：若叶子按字典序排序，可给出相邻兄弟区间证明；
  - 可选：导出 RFC 6962 风格 audit/inclusion proof 格式。

---

## 4. 数学模型与算法

> 本章给出 SM3 的形式化定义；公式以 32-bit 字为基本运算单元，`⊕` 表示按位异或，`+` 表示模 $2^{32}$ 加法，`<<<` 表示循环左移。

### 4.1 SM3 消息填充与分组

设原始消息长度为 $l$ bit。填充步骤：

1. 追加单个比特 `1`。
2. 追加 $k$ 个 `0`，使得：
   
   $$l + 1 + k \equiv 448 \pmod{512}$$

4. 追加 64 bit 的原始长度 $l$（大端表示）。

填充后消息长度为 $l' = l + 1 + k + 64$，且 $l'$ 为 512 的倍数。将填充后消息按 512 bit 分组：

$$
B_0, B_1, \dots, B_{n-1}.
$$

### 4.2 消息扩展

每个 512-bit 分组 $B_i$ 被划分为 16 个 32-bit 字：

$$W_0, W_1, \dots, W_{15}$$

随后扩展得到 $W_{16}, \dots, W_{67}$：

$$W_j = P_1\big(W_{j-16} \oplus W_{j-9} \oplus (W_{j-3} <<< 15)\big) \oplus (W_{j-13} <<< 7) \oplus W_{j-6}, \quad 16 \le j \le 67$$


### 4.3 压缩函数

初始 IV（8 × 32-bit）：

```
V0 = 7380166F 4914B2B9 172442D7 DA8A0600 A96F30BC 163138AA E38DEE4D B0FB0E4E
```

设上一轮中间值为 $V_i = (A,B,C,D,E,F,G,H)$，输入分组扩展序列 $W_j, W'_j$。对 $j = 0..63$ 执行：

$$
SS1 = ((A <<< 12) + E + (T_j <<< j)) <<< 7
$$

$$
SS2 = SS1 \oplus (A <<< 12)
$$

$$
TT1 = (FF_j(A,B,C) + D + SS2 + W'_j) \bmod 2^{32}
$$

$$
TT2 = (GG_j(E,F,G) + H + SS1 + W_j) \bmod 2^{32}
$$

寄存器更新：

$$
D = C, \quad C = B <<< 9, \quad B = A, \quad A = TT1,
$$

$$
H = G, \quad G = F <<< 19, \quad F = E, \quad E = P_0(TT2).
$$

轮结束后得到 \(C(V_i,B_i) = (A,B,C,D,E,F,G,H)\)，更新链值：

$$
V_{i+1} = V_i \oplus C(V_i,B_i).
$$

### 4.4 常量、布尔函数与置换

轮常量：

```
T_j = 0x79CC4519  (0 ≤ j ≤ 15)
T_j = 0x7A879D8A (16 ≤ j ≤ 63)
```

布尔函数：

$$
FF_j(X,Y,Z) = \begin{cases}
X \oplus Y \oplus Z, & 0 \le j \le 15, \\
(X \land Y) \lor (X \land Z) \lor (Y \land Z), & 16 \le j \le 63;
\end{cases}
$$

$$
GG_j(X,Y,Z) = \begin{cases}
X \oplus Y \oplus Z, & 0 \le j \le 15, \\
(X \land Y) \lor ((\lnot X) \land Z), & 16 \le j \le 63.
\end{cases}
$$

置换：

$$
P_0(X) = X \oplus (X <<< 9) \oplus (X <<< 17),
$$

$$
P_1(X) = X \oplus (X <<< 15) \oplus (X <<< 23).
$$

### 4.5 哈希总体流程

完整哈希：

1. 填充消息 $m \to m'$。
2. 分组
3. 设 $V_0 = IV$。
4. 对每一分组
5. 输出 $V_n$（拼接为 256-bit digest，按大端序列化）。

---

## 5. 项目结构

下面给出推荐目录组织。你可以选择 C / C++ / Rust / Python 作为主实现语言，本文以 C 为示例，并提供 Python 绑定。

```
sm3-project/
├── include/
│   └── sm3.h                  # 对外 API 头文件
├── assets/
|   ├── Length_extension_attack.png
|   └── merkle.png
├── src/
│   ├── sm3.c                  
│   ├── merkle.cpp            
│   └── sm3_length_extension_attack.cpp
└──README.md                  # 本文档
```

---


## 6. 性能测试

### 6.1 测试维度与指标

- **吞吐量**：MB/s。
- **每字节周期数 (cycles/byte)**：使用 `rdtsc` 或 `perf`。
- **批处理可扩展性**：多消息并行批处理大小 (N=1,4,8,16)。
- **分组长度影响**：短消息 vs 长消息。
- **实现对比**：`ref` vs `opt` vs `avx2` vs `neon`。

### 6.2 SIMD/多线程测试注意事项

- 固定 CPU 频率（禁用动态频率变动）。
- 绑定线程亲和性（`taskset`）。
- 预热缓存。
- 测试不同批深度（一次处理多块消息）。

---

## 7. 实验结果

### 9.1 长度扩展攻击结果

假设服务器验证 `token = SM3(secret || msg)`： 我们截获 `digest = SM3(secret || msg)`，并猜测 `secret` 长度（例如 16 字节）。

![image](https://github.com/uicciu/project_summary/blob/main/Project4/assets/Length_extension_attack.png)

### 9.2 Merkle 树存在性证明结果
![image](https://github.com/uicciu/project_summary/blob/main/Project4/assets/merkle.png)

* Leaf hashes：对应每个叶子数据字符串的 SM3 哈希值。

* Merkle root hash：所有叶子节点通过二叉哈希树合并计算得到的根哈希。

* Proof path hashes：验证某个叶子节点（这里是 "cherry"）的存在性，提供从叶子到根的兄弟节点哈希路径。

* Verification result：使用该路径计算最终哈希，与根哈希一致，验证成功。



## 10. 参考文献

1. 《信息安全技术 SM3 密码杂凑算法》GB/T 32905-2016.
2. 国家密码管理局相关发布文档（SM 系列算法）。
3. Merkle Tree 原始论文：R. C. Merkle, "Protocols for Public Key Cryptosystems", 1980.
4. Certificate Transparency（Merkle Tree 应用）技术资料，RFC 6962.
5. 典型开源实现（例如 GMSSL / BouncyCastle / OpenSSL 中的 SM3 模块）。

---


