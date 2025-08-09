# Cybersecurity Innovation and Entrepreneurship Practice Course

> 2025年网络空间安全创新创业实践 有关项目集合

## 项目创建者

| 姓名 |                Github账户名称                | 学号         |
| :----------: | :------------------------------------------: | ------------ |
|    苏永佳    |     [uicciu ](https://github.com/uicciu)     | 202200460059 | 


## 项目表

一共有6个项目。

| 项目序号 |                项目名称                | 实现结果         |
| :----------: | :------------------------------------------: | ------------ |
|    [project1](https://github.com/uicciu/project_summary/blob/main/Project1/README.md)    |     Software implementation and optimization of SM4    | 通过 **T-Table** 技术将 S-box 和线性变换预计算成查找表，提升约 2.5–3 倍性能；利用 **AES-NI 指令**中 ```_mm_aesenclast_si128``` 实现快速 S-box 替代并配合逆 ShiftRows 操作，提升约 5 倍；使用 **AVX-512** 指令中的 _mm512_rol_epi32 实现多个轮函数输入的并行循环左移，结合 SIMD 技术可提升 6–8 倍性能；最终在 **GCM** 模式中结合 CLMUL加速运算，性能得到更好的提升。| 
|    [project2](https://github.com/uicciu/project_summary/blob/main/Project2/README.md)    |     Image Leak Detection Based on Digital Watermarking     | 本项目基于**离散小波变换DWT**在宿主图像的LL子带中嵌入隐形水印，利用调整小波系数幅值实现水印信息的隐秘植入；提取时通过比较原始与水印图像的低频系数差异还原水印。针对**亮度调整、对比度变化、裁剪、水平翻转及不同质量等级的JPEG压缩**等多种攻击进行了鲁棒性测试。实验结果表明，该方法在保证图像高视觉质量的同时，对亮度、对比度及中等强度JPEG压缩攻击具备良好鲁棒性，但对几何变换防护效果有限，需进一步引入几何同步或冗余嵌入策略以增强实用性。 | 
|    [project3](https://github.com/uicciu/project_summary/blob/main/Project3/README.md)    |     Implement the circuit of the Poseidon2 hash algorithm using Circom     | 本项目基于**Circom**实现```Poseidon2哈希电路```，利用**Groth16算法**完成零知识证明的生成与验证，展示了该哈希函数的置换结构及MDS矩阵扩散性，并通过脚本自动化完成电路编译、可信设置生成、证明生成与验证全过程。 | 
|    [project4](https://github.com/uicciu/project_summary/blob/main/Project4/README.md)    |     Software Implementation and Optimization of SM3     | 本项目围绕中国国家标准哈希算法SM3展开，完整实现了SM3的基础算法与流式接口，并基于国密规范进行了软件级优化，包括减少内存拷贝、循环展开及SIMD指令加速。项目重点验证了SM3的安全特性，特别是通过实现长度扩展攻击演示了**Merkle–Damgård结构**带来的潜在风险，演示了攻击者在未知密钥条件下如何利用中间状态伪造消息摘要。此外，项目设计并实现了基于SM3的高效Merkle树构建和验证机制，支持大规模叶节点处理，并提供存在性和不存在性证明，满足现代应用如区块链与证书透明度的安全需求。 | 
|    [project5](https://github.com/uicciu/project_summary/blob/main/Project5/README.md)    |     Optimization of Software Implementation of SM2     | 本项目基于Python完整实现**SM2数字签名算法**，涵盖密钥生成、签名和验签过程，重点复现了随机数重复使用和忽略用户标识Z两大安全漏洞，通过PoC验证其对私钥泄露和签名伪造的实际威胁，结合数学推导深入分析漏洞机理，同时探讨了算法在软件层面的优化方向，旨在全面提升对SM2算法安全性和实用性的理解与掌握。 | 
|    [project6](https://github.com/uicciu/project_summary/blob/main/Project6/README.md)    |     Google Password Checkup verification     | 本项目基于 **DDH 假设**和**同态加密**，实现并验证了 ```Google Password Checkup```所用的 ```Private Intersection Sum with Cardinality```协议，保障双方在半诚实模型下安全计算交集大小及对应值总和，同时保护数据隐私和防止非交集信息泄露。 | 


## 
