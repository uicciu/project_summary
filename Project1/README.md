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

#### 1.3 
