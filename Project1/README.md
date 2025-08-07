# Project 1: Software Implementation and Optimization of SM4

---

## 目录
- [1. 项目要求](##1-项目要求)
- [2. SM4 算法概述](##2-sm4-算法概述)
  - [2.1 轮函数定义](###2.1-轮函数定义)
- [3. 优化 SM4 的软件执行效率](##3-优化-sm4-的软件执行效率)
  - [3.1 基于 T-Table 的优化](###3.1-基于-t-table-的优化)
  - [3.2 基于 AES-NI 指令的优化](###3.2-基于-aes-ni-指令的优化)
  - [3.3 基于 VPROLD 指令的优化](###3.3-基于-vprold-指令的优化)
- [4. SM4-GCM 工作模式的软件优化](#4-sm4-gcm-工作模式的软件优化)
  - [4.1 GCM 模式数学描述](#41-gcm-模式数学描述)
  - [4.2 软件优化策略](#42-软件优化策略)
- [5. 性能结果()](#5-性能结果（理想情况）)
- [6. 目录结构]

---

## 1. 项目要求
本项目旨在实现 **SM4 分组密码算法**，并在软件层面进行多种优化，提升执行效率。优化范围包括：
- **T-table 优化**
- **AES-NI 指令集加速**
- **最新 SIMD 指令优化（VPROLD、GFNI 等）**

此外，基于优化后的 SM4 实现，完成 **GCM（Galois/Counter Mode）认证加密模式**，并进行性能优化。

---

## 2. SM4 算法概述
SM4 是国家商用密码标准，采用 **32 轮 Feistel 结构**，块长和密钥长度均为 **128 位**。

### 2.1 轮函数定义
SM4 的核心加密轮函数：

$$
X_{i+4} = X_i \oplus T(X_{i+1} \oplus X_{i+2} \oplus X_{i+3} \oplus rk_i)
$$


其中，非线性变换 $T$ 定义为：

$$
T(B) = L(\tau(B))
$$

- **τ：字节代换**

$$
\tau(B) = (S(b_0), S(b_1), S(b_2), S(b_3))
$$

- **L：线性变换**

$$
L(B) = B \oplus (B \lll 2) \oplus (B \lll 10) \oplus (B \lll 18) \oplus (B \lll 24)
$$



$\lll$ 表示 **循环左移**。

---

## 3. 优化 SM4 的软件执行效率

### 3.1 基于 T-Table 的优化
**思想**：将 **S-box 替换 + 线性变换** 预计算成 4 张查表，每张 256 项，每项 32 位。

$$
T_i[x] = L(\text{S-box}(x) \ll (8 \times i)), \quad i=0,1,2,3
$$

优化后每轮：

$$
T(B) = T_0[b_0] \oplus T_1[b_1] \oplus T_2[b_2] \oplus T_3[b_3]
$$


**结果展示**：

![image](https://github.com/uicciu/project_summary/blob/main/Project1/assets/sm4T.png)

**性能提升**：约 **2.5-3x**。

---

### 3.2 基于 AES-NI 指令的优化
AES-NI 提供 `_mm_aesenclast_si128`，用于实现 S-box。
策略：
1. 新增 __aesni_subbytes()__ 函数：用 AES-NI 指令 _mm_aesenclast_si128 执行 S-box（包含 AES 的 ShiftRows，需撤销）。
2. tau_aesni() 用 AES-NI 代替普通 S-box。
3. 新增 SM4_Encrypt_AESNI_SIMD()，用 AES-NI 优化的 T 函数替代传统实现。
4. 额外实现 undo_shiftrows() 来完成逆 **ShiftRows**。

核心代码：

```c
X[i + 4] = X[i] ^ T_aesni(X[i+1] ^ X[i+2] ^ X[i+3] ^ rk[i]);
```

**结果展示**

![image](https://github.com/uicciu/project_summary/blob/main/Project1/assets/sm4AESIN.png)

**性能提升**：约 **5x**。

### 3.3 基于 VPROLD 指令的优化

**问题分析**  
SM4 的线性变换 $L(B)$ 需要执行多次循环左移和异或操作：

$$
L(B) = B \oplus (B \lll 2) \oplus (B \lll 10) \oplus (B \lll 18) \oplus (B \lll 24)
$$

其中 $\lll$ 表示循环左移。

在传统实现中，这会导致每轮执行多个 `ROTL` 操作，增加了运算延迟。

---

**优化思想**  
利用 **Intel AVX-512 指令集** 提供的 `VPROLD` 指令（在 Intrinsics 中对应 `_mm_rol_epi32` 和 `_mm512_rol_epi32`），可以高效实现 **SIMD 并行循环左移**，避免逐个元素移位，提高并行度。

- **VPROLD 功能**：对 32 位整型数据进行 **循环左移**，并且支持向量级别的批量操作。
- **优势**：可以一次处理 8 个（AVX2）或 16 个（AVX-512）32 位数据。

---

**优化实现步骤**
1. 将 SM4 的数据块或多个轮函数输入加载到 SIMD 寄存器。
2. 使用 `_mm512_rol_epi32` 对多个值进行循环左移操作。
3. 完成异或组合，形成最终的 L 变换。

---

**示例代码**

```c
inline __m512i L(__m512i x) {
    auto r2  = _mm512_rol_epi32(x, 2);
    auto r10 = _mm512_rol_epi32(x, 10);
    auto r18 = _mm512_rol_epi32(x, 18);
    auto r24 = _mm512_rol_epi32(x, 24);
    return _mm512_xor_si512(x,
           _mm512_xor_si512(r2,
           _mm512_xor_si512(r10,
           _mm512_xor_si512(r18, r24))));
}
```

**结果展示**

![image](https://github.com/uicciu/project_summary/blob/main/Project1/assets/vprold.png)

**性能提升**：约 **6-8x**。

## 4. SM4-GCM 工作模式的软件优化

GCM（Galois/Counter Mode）是一种广泛使用的 **认证加密模式 (AEAD)**，结合了 **计数器模式（CTR）加密** 和 **基于 GF(2^128) 的认证标签生成**，在保证机密性的同时提供完整性保护。

GCM 的核心运算分为两部分：
1. **加密部分**：基于计数器模式，块加密函数使用 SM4。
2. **认证部分**：使用 GHASH 函数在 GF(2^128) 上进行运算。

---

### 4.1 GCM 模式数学描述

设：
- $P = \{ P_1, P_2, \dots, P_n \}$ 为明文块（每块 128-bit）
- $C = \{ C_1, C_2, \dots, C_n \}$ 为密文块
- $H = E_K(0^{128})$，SM4 加密的全零块
- $A$ 为附加认证数据（AAD）

#### **加密过程 (CTR 模式)**
对于每个数据块：

$$
C_i = P_i \oplus E_K(\text{IV} || \text{counter}_i)
$$

其中：

$$
\text{counter}_i = \text{ICB} + i \pmod{2^{32}}
$$

#### **认证过程 (GHASH)**
计算认证标签 Tag：

$$
\text{Tag} = \text{GHASH}(H, A, C) \oplus E_K(\text{IV})
$$

其中 GHASH 定义为：

$$
Y_0 = 0, \quad Y_i = (Y_{i-1} \oplus X_i) \cdot H
$$

$X_i$ 表示拼接后的 AAD 和密文块，乘法在 GF(2^{128}) 上进行。

---

### 4.2 软件优化策略

#### (1) SM4 部分优化
- 复用 **T-Table、AES-NI 或 AVX-512 VPROLD 优化**。
- 使用 **多缓冲 (multi-buffer)** 技术，将 CTR 模式中的多个计数器块并行处理。

#### (2) GHASH 优化
- 使用 **Intel CLMUL (Carry-less Multiply)** 指令加速 GF(2^128) 乘法。
- 实现 Karatsuba 优化，减少乘法次数。

伪代码示例：
```c
__m128i H = ...;  // 哈希子密钥
__m128i Xi = ...; // 当前块
__m128i result = _mm_clmulepi64_si128(Xi, H, 0x00); // GF(2^128)乘法
```


#### (3) 多块并行处理 

- 采用 **AVX2/AVX-512** 实现多缓冲并行加密。
- 使用 在 CTR 模式中一次处理 **4~8** 个计数器块，利用 SIMD 提升吞吐率。

#### (4) 避免多余内存操作

- 使用寄存器级别运算，减少 ``memcpy``。
- 通过流水线优化（Pipelining）隐藏延迟。

**结果展示**

![image](https://github.com/uicciu/project_summary/blob/main/Project1/assets/GCM.png)

**性能提升**：在 **128-bit** 块并行模式下，GCM 认证加密可实现 **10Gbps** 以上 吞吐率。

## 5. 性能结果（理想情况）

| 实现方案              | 平台       | 块大小 (128-bit) |  提升倍数 |
|-----------------------|-----------|-------------------|----------|
| 原始实现（基础版）     | AVX2      | 16 字节          | 1x       |
| **T-Table 优化版**    | AVX2      | 16 字节          | 2.5x     |
| **AES-NI 优化版**     | AES-NI    | 16 字节          | 5x       |
| **VPROLD + AVX512**   | AVX-512   | 16 字节          | 8x       |
| **SM4-GCM + CLMUL**   | AVX-512   | 16 字节 (批量)   |  10x+     |

---

### 性能对比图（大致图）

```text
吞吐率 (Gbps)
9 |                            ██████  (SM4-GCM)
8 |                            ██████
7 |
6 |                     ████   (VPROLD)
5 |              ████          (AES-NI)
4 |
3 |       ████                 (T-Table)
2 |
1 | █                          (原始)
0 |______________________________________

   原始   T-Table   AES-NI   VPROLD  GCM
```

## 6. 目录结构


