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
|    [project4](https://github.com/uicciu/project_summary/blob/main/Project4/README.md)    |     Software Implementation and Optimization of SM3     | 202200460059 | 
|    [project5](https://github.com/uicciu/project_summary/blob/main/Project5/README.md)    |     Optimization of Software Implementation of SM2     | 202200460059 | 
|    [project6](https://github.com/uicciu/project_summary/blob/main/Project6/README.md)    |     Google Password Checkup verification     | 202200460059 | 


## 
