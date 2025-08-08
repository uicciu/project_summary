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
- [6. 接口说明](#6-接口说明)
  - [6.1 C 语言接口](#61-c-语言接口)
  - [6.2 Python 参考封装](#62-python-参考封装)
  - [6.3 命令行工具 sm3cli](#63-命令行工具-sm3cli)
- [7. 使用说明](#7-使用说明)
  - [7.1 构建与安装](#71-构建与安装)
  - [7.2 计算文件摘要](#72-计算文件摘要)
  - [7.3 批量哈希](#73-批量哈希)
  - [7.4 与 OpenSSL(SM3) 或参考实现对比测试](#74-与-opensslsm3-或参考实现对比测试)
- [8. 性能测试](#8-性能测试)
  - [8.1 测试维度与指标](#81-测试维度与指标)
  - [8.2 基准测试脚本](#82-基准测试脚本)
  - [8.3 SIMD/多线程测试注意事项](#83-simd多线程测试注意事项)
- [9. 实验示例](#9-实验示例)
  - [9.1 长度扩展攻击示例](#91-长度扩展攻击示例)
  - [9.2 Merkle 树存在性证明示例](#92-merkle-树存在性证明示例)
  - [9.3 Merkle 树不存在性证明示例](#93-merkle-树不存在性证明示例)
- [10. 参考文献](#10-参考文献)

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
   $$
   l + 1 + k \equiv 448 \pmod{512}.
   $$
3. 追加 64 bit 的原始长度 $l$（大端表示）。

填充后消息长度为 $l' = l + 1 + k + 64$，且 $l'$ 为 512 的倍数。将填充后消息按 512 bit 分组：

$$
B_0, B_1, \dots, B_{n-1}.
$$

### 4.2 消息扩展

每个 512-bit 分组 $B_i$ 被划分为 16 个 32-bit 字：

$$
W_0, W_1, \dots, W_{15}.
$$

随后扩展得到 $W_{16}, \dots, W_{67}$：

$$
W_j = P_1\big(W_{j-16} \oplus W_{j-9} \oplus (W_{j-3} <<< 15)\big) \oplus (W_{j-13} <<< 7) \oplus W_{j-6}, \quad 16 \le j \le 67.
$$

再定义：

$$
W'_j = W_j \oplus W_{j+4}, \quad 0 \le j \le 63.
$$

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
2. 分组：$m' = B_0 \Vert B_1 \Vert \dots \Vert B_{n-1}$。
3. 设 $V_0 = IV$。
4. 对每一分组：$V_{i+1} = CF(V_i, B_i)$。
5. 输出 $V_n$（拼接为 256-bit digest，按大端序列化）。

---

## 5. 项目结构

下面给出推荐目录组织。你可以选择 C / C++ / Rust / Python 作为主实现语言，本文以 C 为示例，并提供 Python 绑定。

```
sm3-project/
├── include/
│   └── sm3.h                  # 对外 API 头文件
├── src/
│   ├── sm3.c                  # 基础参考实现（可读性版本）
│   ├── sm3_opt.c              # 优化版（循环展开 / 内联 / 查表）
│   ├── sm3_avx2.c             # AVX2 SIMD 并行实现（可选）
│   ├── sm3_neon.c             # ARM NEON 实现（可选）
│   └── sm3_utils.c            # 字节序、工具函数
├── python/
│   ├── sm3.py                 # 纯 Python 参考 & ctypes 绑定
│   └── length_extension_attack.py
├── merkle/
│   ├── merkle_sm3.py          # Merkle 树实现
│   ├── merkle_cli.py          # CLI 工具
│   └── proofs/                # 示例证明文件
├── tests/
│   ├── test_vectors.c         # 与官方/参考向量对比
│   ├── test_length_ext.py     # 长度扩展验证
│   ├── test_merkle.py         # Merkle 存在性/不存在性
│   └── data/                  # 测试输入样例
├── bench/
│   ├── bench_sm3.c            # 性能基准
│   └── bench.py               # 批量性能测试脚本
├── cmake/
│   └── ...
├── CMakeLists.txt
├── Makefile
├── README.md                  # 本文档
└── LICENSE
```

---

## 6. 接口说明

### 6.1 C 语言接口

#### 上下文结构体

```c
#include <stdint.h>
#include <stddef.h>

#define SM3_DIGEST_LENGTH 32

typedef struct {
    uint32_t state[8];   // 当前链值 V_i
    uint64_t length;     // 已处理比特长度（或字节长度 * 8）
    uint8_t  buffer[64]; // 分组缓冲
    size_t   buf_used;   // 缓冲已用字节
} sm3_ctx;
```

#### 初始化

```c
void sm3_init(sm3_ctx *ctx);
```

#### 增量更新

```c
void sm3_update(sm3_ctx *ctx, const uint8_t *data, size_t len);
```

#### 完成并输出摘要

```c
void sm3_final(sm3_ctx *ctx, uint8_t out[SM3_DIGEST_LENGTH]);
```

#### 一次性 API

```c
void sm3(const uint8_t *msg, size_t len, uint8_t out[SM3_DIGEST_LENGTH]);
```

### 6.2 Python 参考封装

示例：

```python
import sm3

digest = sm3.hash(b"hello world")
print(digest.hex())
```

或流式：

```python
h = sm3.SM3()
h.update(b"hello ")
h.update(b"world")
print(h.digest().hex())
```

### 6.3 命令行工具 sm3cli

```
$ sm3cli -h
Usage: sm3cli [options] <file>...

Options:
  -s <string>   Hash literal string
  -x            Output lowercase hex (default)
  -X            Output uppercase hex
  -b            Benchmark mode
  --impl=<ref|opt|avx2> Select implementation
```

---

## 7. 使用说明

### 7.1 构建与安装

#### 使用 CMake

```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
make install  # 可选
```

#### 使用 Makefile

```bash
make CC=gcc CFLAGS="-O3 -march=native"
```

### 7.2 计算文件摘要

```bash
./sm3cli data/message.txt
```


### 7.3 批量哈希

```bash
find ./data -type f -print0 | xargs -0 ./sm3cli > digests.txt
```

### 7.4 与 OpenSSL(SM3) 

若系统 OpenSSL 支持 `sm3` 算法，可比对：

```bash
echo -n "abc" | openssl dgst -sm3
./sm3cli -s abc
```

---

## 8. 性能测试

### 8.1 测试维度与指标

- **吞吐量**：MB/s。
- **每字节周期数 (cycles/byte)**：使用 `rdtsc` 或 `perf`。
- **批处理可扩展性**：多消息并行批处理大小 (N=1,4,8,16)。
- **分组长度影响**：短消息 vs 长消息。
- **实现对比**：`ref` vs `opt` vs `avx2` vs `neon`。

### 8.2 基准测试脚本

示例（Python）：

```python
import os, time, random
import sm3

sizes = [1, 8, 64, 256, 1024, 4096, 1<<20]
for s in sizes:
    data = os.urandom(s)
    t0 = time.time()
    for _ in range(1000):
        sm3.hash(data)
    t1 = time.time()
    print(s, (t1-t0))
```

### 8.3 SIMD/多线程测试注意事项

- 固定 CPU 频率（禁用动态频率变动）。
- 绑定线程亲和性（`taskset`）。
- 预热缓存。
- 测试不同批深度（一次处理多块消息）。

---

## 9. 实验示例

### 9.1 长度扩展攻击示例

假设服务器验证 `token = SM3(secret || msg)`： 我们截获 `digest = SM3(secret || msg)`，并猜测 `secret` 长度（例如 16 字节）。

Python 攻击示例：

```python
from length_extension_attack import sm3_lenext_attack

orig_digest_hex = "66c7f0f462eeedd9d1f2d46bdc10e4e2..."  # 截获
orig_len = 16 + len(b"user=alice")
ext_msg = b"&admin=true"
new_digest, forged_input = sm3_lenext_attack(orig_digest_hex, orig_len, ext_msg)
```

验证：

```python
import sm3
assert sm3.hash(forged_input).hex() == new_digest.hex()
```

### 9.2 Merkle 树存在性证明示例

```python
from merkle_sm3 import build_merkle, merkle_proof, verify_merkle_proof

leaves = [b"L0", b"L1", b"L2", b"L3"]
root, nodes = build_merkle(leaves)
path = merkle_proof(nodes, idx=2)
assert verify_merkle_proof(root, leaves[2], path, idx=2)
```

### 9.3 Merkle 树不存在性证明示例

若叶子排序，可证明值 `X` 位于 `L_i` 与 `L_{i+1}` 之间：

```python
from merkle_sm3 import merkle_non_inclusion

proof = merkle_non_inclusion(sorted_leaves, X)
# proof: (left_leaf, right_leaf, left_path, right_path)
```

验证时同时校验左右邻区间路径与排序关系。

---

## 10. 参考文献

1. 《信息安全技术 SM3 密码杂凑算法》GB/T 32905-2016.
2. 国家密码管理局相关发布文档（SM 系列算法）。
3. Merkle Tree 原始论文：R. C. Merkle, "Protocols for Public Key Cryptosystems", 1980.
4. Certificate Transparency（Merkle Tree 应用）技术资料，RFC 6962.
5. 典型开源实现（例如 GMSSL / BouncyCastle / OpenSSL 中的 SM3 模块）。

---


