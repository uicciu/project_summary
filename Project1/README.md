# Project1 Software implementation and optimization of SM4

## 项目要求

* 从基本实现出发 优化SM4的软件执行效率，至少应该覆盖T-table、AESNI以及最新的指令集（GFNI、VPROLD等）

* 基于SM4的实现，做SM4-GCM工作模式的软件优化实现

## 项目实现

### 1. 优化SM4的软件执行效率

> 三种选择，T表、AESNI以及最新的指令集GFNI

#### 1.1 T-table

> 通过将 S-Box 和线性变换预计算为 T 表，减少运行时计算。

__实现方法__：

预计算 4 张 T 表（每张 256 项，每项为32位字）用于替代每轮的 S-box 和线性替换操作。

#### 1.2 AESNI 

> 利用SM4与AES中S盒结构的相似性，借助intel的AES-NI指令完成S盒操作。

__实现方法__:

使用``_mm_aesenclast_si128`` 指令来加速 S-box 操作，并构造全 0 轮密钥；自动完成字节代换（S-box）;抵消轮密钥加和 ShiftRows 的影响，以保留 SM4 所需的替代效果；从而实现了 SM4 的 AES-NI 指令集优化版本。

#### 1.3 VPROLD 指令

> VPROLD 为 Intel AVX-512 指令集 中的一条矢量指令，用于按位循环左移，对应函数``_mm_rol_epi32``

__实现方法__:

使用基于 SIMD 的 VPROLD 指令``_mm_rol_epi32``来加速线性变换:

* 保留 SBOX 完整替代逻辑；

* 使用 ``_mm_rol_epi32`` 替代多次 ROTL；

* 完整保持 SM4 加密流程；

* 输出基于 VPROLD 优化后的性能时间。

### 2. SM4-GCM工作模式的软件优化实现

> 在软件层面实现 SM4 分组加密算法与 GCM（Galois/Counter Mode）认证加密模式.

__实现方法__:

1. **SM4 加密优化**：使用 SIMD 指令加速 SM4 的线性变换 L()，减少循环移位与 XOR 的开销。
2. **GHASH 优化**：GCM 模式中的 GHASH 使用 GF(2^128) 乘法，通常用 CLMUL 指令或 AVX/AVX-512 指令优化，以提高吞吐率。
3. **多块并行**：对多数据块使用批处理并行优化，减少循环开销。
4. **减少内存操作**：减少 memcpy 和小数组拷贝，使用寄存器级操作。

## 项目结果
