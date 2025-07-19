# Project 2: Image Leak Detection Based on Digital Watermarking

> 利用**数字水印技术**在图像中嵌入可验证标识，用于数据泄露溯源；并通过多种图像攻击（翻转、平移、裁剪、亮度/对比度调整、JPEG 压缩等）评估鲁棒性。

---

## 目录

- [1. 项目概览](#1-项目概览)
- [2. 理论背景](#2-理论背景)
  - [2.1 数字水印分类](#21-数字水印分类)
  - [2.2 DWT（离散小波变换）简介](#22-dwt离散小波变换简介)
  - [2.3 基于 DWT 的水印嵌入思想](#23-基于-dwt-的水印嵌入思想)
- [3. 数学模型](#3-数学模型)
  - [3.1 图像 DWT 分解](#31-图像-dwt-分解)
  - [3.2 水印嵌入公式](#32-水印嵌入公式)
  - [3.3 水印提取公式](#33-水印提取公式)
  - [3.4 鲁棒性指标](#34-鲁棒性指标)
- [4. 系统流程](#4-系统流程)
  - [4.1 处理步骤说明](#42-处理步骤说明)
- [5. 软件实现说明](#5-软件实现说明)
  - [5.1 环境依赖](#51-环境依赖)
  - [5.2 目录结构建议](#52-目录结构建议)
  - [5.3 核心 Python API 概览](#53-核心-python-api-概览)
- [6. 水印嵌入/提取参考实现](#6-水印嵌入提取参考实现)
  - [6.1 基础 DWT 水印嵌入](#61-基础-dwt-水印嵌入)
  - [6.2 基础 DWT 水印提取](#62-基础-dwt-水印提取)
  - [6.3 批处理接口](#63-批处理接口)
- [7. 图像攻击与鲁棒性测试](#7-图像攻击与鲁棒性测试)
  - [7.1 攻击类型与参数](#71-攻击类型与参数)
  - [7.2 自动化鲁棒性测试脚本](#72-自动化鲁棒性测试脚本)
  - [7.3 指标统计与可视化](#73-指标统计与可视化)
- [8. 实验示例与结果模板](#8-实验示例与结果模板)
  - [8.1 示例实验配置](#81-示例实验配置)
  - [8.2 结果记录表格模板](#82-结果记录表格模板)
  - [8.3 示例结果可视化](#83-示例结果可视化)
- [9. 常见问题 (FAQ)](#9-常见问题-faq)
- [10. 附录：公式合集](#10-附录公式合集)

---

## 1. 项目概览

本项目实现了一个**基于数字水印的图像泄露检测原型系统**，允许在图像传播前写入隐形水印，并在图像遭到二次编辑、传播或恶意篡改后识别来源、验证版权或追踪泄露路径。

项目核心目标：

- ✅ 将**二值或灰度水印**嵌入宿主图像（载体）。
- ✅ 在多种图像攻击后**可靠提取水印**。
- ✅ 支持**批量鲁棒性测试**并输出指标（PSNR、NC、BER、SSIM）。
- ✅ 可用于**泄露检测**：根据提取出的水印标识（如用户 ID、授权码）确认数据来源。

实现策略：

- 使用 **DWT（离散小波变换）** 将图像分解到频域；
- 在 **LL / 中频子带**中嵌入缩放后的水印信号；
- 提取时复原小波系数，计算相似度以判断水印存在性；
- 对多个攻击版本进行批测以评估鲁棒性。

---

## 2. 理论背景

### 2.1 数字水印分类

| 类型   | 可见性      | 典型用途      | 对抗性    |
| ---- | -------- | --------- | ------ |
| 可见水印 | 透明/半透明覆盖 | 在线版权标识    | 易被裁剪   |
| 隐形水印 | 人眼不可见    | 版权保护、泄露溯源 | 可设计更鲁棒 |

按嵌入域：

- **空域法**：直接修改像素（如 LSB）。实现简单，鲁棒性较弱。
- **频域法**：在 DCT、DWT、DFT 等域修改变换系数。鲁棒性好，广泛使用。

本项目采用 **DWT 频域水印**，兼顾透明性与鲁棒性。

---

### 2.2 DWT（离散小波变换）简介

DWT 将图像分解为不同尺度与方向的子带。对单层二维小波分解：

$$
I(x,y) \xrightarrow{\text{DWT}} \{LL, LH, HL, HH\}
$$

- **LL**：近似（低频）成分，保留全局亮度、结构。
- **LH / HL / HH**：水平、垂直、对角高频纹理。

多层分解可递归对 LL 再分解：

```
Level 1: LL1 LH1 HL1 HH1
Level 2: (LL1 -> LL2 LH2 HL2 HH2)
```

DWT 的平移与尺度特性使其适合嵌入水印，在一定图像处理/压缩下仍可保留信号痕迹。

---

### 2.3 基于 DWT 的水印嵌入思想

一般策略：

1. 对宿主图像做 DWT 分解，取某个子带（如 LL 或 HL）。
2. 调整（缩放/二值化/扩展）水印图像，使其尺寸匹配目标子带。
3. 根据嵌入强度参数 $\alpha$ 修改子带系数：
   $C' = C + \alpha W$
   
5. 执行逆小波变换 (IDWT) 得到嵌入水印后的图像。

---

## 3. 数学模型

### 3.1 图像 DWT 分解

设原始灰度图像为 \(f(x,y)\)， 进行一次二维正向小波变换：

$$
(f) \xrightarrow{\text{DWT}} (c_{LL}, c_{LH}, c_{HL}, c_{HH})
$$

其中：

- $c_{LL}$ 为低频子带；
- $c_{LH}, c_{HL}, c_{HH}$ 分别对应水平、垂直、对角高频。

---

### 3.2 水印嵌入公式

设待嵌入水印矩阵为 \(W\)（可二值化或灰度），选择嵌入子带 \(C\)：

$$
C' = C + \alpha \cdot W
$$

其中：

- \(C\)：原子带系数；
- \(C'\)：嵌入后子带系数；
- $\alpha > 0$：嵌入强度（权衡透明性与鲁棒性）。

嵌入后图像：

$$
I' = \text{IDWT}(C', \text{rest})
$$

---

### 3.3 水印提取公式

若原始图像 \(I\) 可用（非盲检测）：

1. 对原图和水印图 \(I'\) 分别 DWT：得到 \(C\) 和 \(C'\)。
2. 提取水印：

$$
\hat{W} = \frac{C' - C}{\alpha}
$$

若原图不可用（半盲/盲检测），可利用嵌入前记录的统计参数（均值、阈值、伪随机密钥索引）进行检测，详见扩展方案。

---

### 3.4 鲁棒性指标

#### 均方误差 (MSE)

$$
\text{MSE}(I, I') = \frac{1}{MN} \sum_{x=0}^{M-1}\sum_{y=0}^{N-1} (I(x,y) - I'(x,y))^2
$$

#### 峰值信噪比 (PSNR)

$$
\text{PSNR} = 10 \log_{10} \left( \frac{\text{MAX}^2}{\text{MSE}} \right)
$$

其中 $\text{MAX} = 255$ 对 8-bit 图像。

#### 归一化相关性 (NC)

用于衡量提取水印与原水印相似度：

$$
\text{NC}(W, \hat{W}) = \frac{\sum_{i,j} W_{ij} \hat{W}_{ij}}{\sqrt{\sum_{i,j} W_{ij}^2} \times \sqrt{\sum_{i,j} \hat{W}_{ij}^2}}
$$


#### 比特错误率 (BER) (适用于二值水印)

$$
\text{BER} = \frac{1}{MN} \sum_{i,j} [W_{ij} \neq \hat{W}_{ij}]
$$

#### 结构相似性 (SSIM)

用于图像感知质量评估：

$$
\text{SSIM}(I, I') = \frac{(2\mu_I\mu_{I'} + C_1)(2\sigma_{II'} + C_2)}{(\mu_I^2 + \mu_{I'}^2 + C_1)(\sigma_I^2 + \sigma_{I'}^2 + C_2)}
$$

---

## 4. 系统流程

### 4.1 处理步骤说明

1. 载入宿主图像 (RGB → 灰度可选)。
2. 执行一次或多次二维 DWT 分解。
3. 选择嵌入子带（典型：LL 或 HL/HH）。
4. 缩放/归一化水印矩阵到同尺寸。
5. 依据强度 $\alpha$ 调整系数并嵌入。
6. IDWT 得到水印图像。
7. 对攻击图像重复 DWT 并提取水印。
8. 统计指标并绘图。

---

## 5. 软件实现说明

### 5.1 环境依赖

```bash
pip install opencv-python numpy pywavelets scikit-image matplotlib pandas
```

可选：

- `tqdm` 进度条
- `seaborn` 作图（若不使用遵循无特定色要求，可跳过）

---

### 5.2 目录结构建议

```
ImageWatermarking/
├── data/
│   ├── host/              # 宿主图像
│   ├── watermark/         # 水印图像(logo/ID)
│   └── attacks/           # 生成的攻击样本
├── results/
│   ├── extracted/         # 提取出的水印
│   ├── metrics.csv        # 指标记录
│   └── plots/             # 可视化图
├── src/
│   ├── embed.py           # 水印嵌入
│   ├── extract.py         # 水印提取
│   ├── attacks.py         # 图像攻击合集
│   ├── metrics.py         # PSNR/NC/BER/SSIM
│   ├── batch_eval.py      # 批量鲁棒性测试
│   └── utils.py           # 工具函数
└── README.md
```

---

### 5.3 核心 Python API 概览

```python
def embed_watermark(image: np.ndarray, watermark: np.ndarray, *, wave='haar', level=1, band='LL', alpha=0.05) -> np.ndarray:
    """在指定小波子带嵌入水印并返回带水印图像。"""


def extract_watermark(original: np.ndarray, watermarked: np.ndarray, *, wave='haar', level=1, band='LL', alpha=0.05) -> np.ndarray:
    """从水印图像提取水印(需原图)。"""


def apply_attacks(image: np.ndarray, attack_cfg: dict) -> Dict[str, np.ndarray]:
    """对图像施加多种攻击, 返回字典: 攻击名 -> 图像。"""


def eval_robustness(orig_img, wm_img, attacks, watermark, alpha) -> pd.DataFrame:
    """流水线: 攻击 -> 提取 -> 指标统计。"""
```

---

## 6. 水印嵌入/提取参考实现

> 以下示例以灰度图像为例；彩色图像可对每通道独立嵌入或仅在亮度通道嵌入。

### 6.1 基础 DWT 水印嵌入

```python
import pywt, cv2, numpy as np

def _prep_gray(img):
    if img.ndim == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def embed_watermark(image, watermark, wave='haar', level=1, band='LL', alpha=0.05):
    img = _prep_gray(image).astype(np.float32)
    coeffs = pywt.wavedec2(img, wave, level=level)
    # coeffs: (cA, (cH, cV, cD)) * level
    # 取最顶层
    cA, details = coeffs[0], coeffs[1:]
    target = cA if band.upper() == 'LL' else None
    if band.upper() != 'LL':
        raise NotImplementedError('示例实现仅在 LL 子带嵌入')

    # 调整水印尺寸
    wm = cv2.resize(watermark, (target.shape[1], target.shape[0]), interpolation=cv2.INTER_AREA)
    wm = wm.astype(np.float32)
    wm_norm = (wm - wm.min()) / (wm.max() - wm.min() + 1e-8)  # 0~1

    # 嵌入
    cA_wm = target + alpha * wm_norm * target.std()

    # 重组系数
    new_coeffs = [cA_wm] + list(details)
    watermarked = pywt.waverec2(new_coeffs, wave)
    return np.clip(watermarked, 0, 255).astype(np.uint8)
```

---

### 6.2 基础 DWT 水印提取 (非盲)

```python
import pywt, cv2, numpy as np

def extract_watermark(original, watermarked, wave='haar', level=1, band='LL', alpha=0.05):
    orig = _prep_gray(original).astype(np.float32)
    wmimg = _prep_gray(watermarked).astype(np.float32)

    coeffs_o = pywt.wavedec2(orig, wave, level=level)
    coeffs_w = pywt.wavedec2(wmimg, wave, level=level)

    cA_o, details_o = coeffs_o[0], coeffs_o[1:]
    cA_w, details_w = coeffs_w[0], coeffs_w[1:]

    if band.upper() != 'LL':
        raise NotImplementedError('示例实现仅示范 LL 子带提取')

    # 根据嵌入公式反解:  cA_w = cA_o + alpha * wm_norm * sigma
    sigma = cA_o.std()
    wm_est = (cA_w - cA_o) / (alpha * sigma + 1e-8)
    wm_est = np.clip(wm_est, 0, 1)
    wm_est = (wm_est * 255).astype(np.uint8)
    return wm_est
```

---

### 6.3 批处理接口

```python
from pathlib import Path
import pandas as pd

def batch_embed(host_dir, wm_path, out_dir, alpha=0.05):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    wm_img = cv2.imread(str(wm_path), cv2.IMREAD_GRAYSCALE)
    for p in Path(host_dir).glob('*'):
        host = cv2.imread(str(p), cv2.IMREAD_COLOR)
        embedded = embed_watermark(host, wm_img, alpha=alpha)
        cv2.imwrite(str(out_dir / p.name), embedded)
```

---

## 7. 图像攻击与鲁棒性测试

### 7.1 攻击类型与参数

| 攻击      | 参数示例               | 说明                   |
| ------- | ------------------ | -------------------- |
| 水平/垂直翻转 | flip\_code=0/1     | 常见社交平台转发变换           |
| 平移      | shift\_x, shift\_y | 可用仿射并填充边缘            |
| 裁剪      | crop\_ratio=0.1    | 裁剪边缘后缩放回原尺寸          |
| 旋转      | deg=±5°, ±15°      | 小角度编辑                |
| 缩放重采样   | scale=0.5→resize   | 上传压缩                 |
| 亮度调整    | beta               | I' = I + beta        |
| 对比度调整   | alpha              | I' = alpha\*I + beta |
| 高斯噪声    | σ=5,10,20          | 噪声攻击                 |
| JPEG 压缩 | quality=90→30      | 有损平台分发               |

---

### 7.2 自动化鲁棒性测试脚本

```python
import cv2, numpy as np, pandas as pd
from skimage.metrics import structural_similarity as ssim

from attacks import (
    attack_flip, attack_crop, attack_brightness, attack_contrast,
    attack_jpeg, attack_shift, attack_rotate, attack_noise
)
from metrics import psnr, nc, ber
from embed import embed_watermark
from extract import extract_watermark


def eval_robustness_single(host_img, wm_img, attacks_cfg, alpha=0.05):
    wm_embed = embed_watermark(host_img, wm_img, alpha=alpha)

    records = []
    for atk_name, atk_fn, atk_kwargs in attacks_cfg:
        atk_img = atk_fn(wm_embed, **atk_kwargs)
        wm_ext = extract_watermark(host_img, atk_img, alpha=alpha)

        # resize to wm size
        wm_ext_r = cv2.resize(wm_ext, (wm_img.shape[1], wm_img.shape[0]))

        metrics_row = {
            'attack': atk_name,
            'psnr_host_wm': psnr(host_img, atk_img),
            'nc': nc(wm_img, wm_ext_r),
            'ber': ber(wm_img, wm_ext_r),
        }
        try:
            metrics_row['ssim'] = ssim(host_img, atk_img, channel_axis=-1)
        except Exception:
            metrics_row['ssim'] = np.nan
        records.append(metrics_row)

    return pd.DataFrame(records)
```

---

### 7.3 指标统计与可视化

```python
import matplotlib.pyplot as plt

def plot_nc(df, title='NC vs Attack'):
    plt.figure()
    plt.bar(df['attack'], df['nc'])
    plt.xticks(rotation=30, ha='right')
    plt.ylabel('NC')
    plt.title(title)
    plt.tight_layout()
    plt.show()
```

---

## 8. 实验示例与结果模板

### 8.1 示例实验配置

```yaml
host_image: data/host/lena.png
watermark_image: data/watermark/logo.png
wavelet: haar
level: 1
band: LL
alpha: 0.05
attacks:
  - {name: none,        type: none}
  - {name: flip_h,      type: flip, code: 1}
  - {name: crop_10,     type: crop, ratio: 0.10}
  - {name: bright_20,   type: brightness, beta: 20}
  - {name: contrast_15, type: contrast, alpha: 1.5}
  - {name: jpeg_70,     type: jpeg, quality: 70}
  - {name: jpeg_40,     type: jpeg, quality: 40}
```

---

### 8.2 结果记录表格模板

| 攻击       | PSNR(dB) | SSIM | NC    | BER   | 可识别(阈值=0.9)  |
| -------- | -------- | ---- | ----- | ----- | ------------ |
| none     | 45.2     | 0.99 | 0.999 | 0.000 | ✅            |
| flip\_h  | 44.0     | 0.98 | 0.995 | 0.002 | ✅            |
| crop\_10 | 41.8     | 0.95 | 0.978 | 0.010 | ✅            |
| jpeg\_40 | 38.5     | 0.89 | 0.942 | 0.030 | ⚠ borderline |
| jpeg\_20 | 34.2     | 0.75 | 0.702 | 0.180 | ❌            |

> **可识别规则示例：** 当 NC ≥ 0.90 或 BER ≤ 0.05 判定水印成功。

---

### 8.3 示例结果可视化

```text
NC
1.0 |■■■■■■ none
0.95|■■■■■  flip
0.90|■■■■   crop
0.85|■■■    jpeg_70
0.80|■■     jpeg_40
```

（正式报告请使用 matplotlib 绘图）

---

## 9. 常见问题 (FAQ)

**Q1:** 嵌入强度 α 越大水印越稳吗？→ 鲁棒性增强，但可见失真加重；需折中。

**Q2:** 用彩色图像时怎么嵌入？→ 常用 YCbCr，将水印写入亮度 Y；或分通道嵌入并加权。

**Q3:** 原图不可得时怎么办？→ 使用盲水印：伪随机扩频序列、量化索引调制 (QIM)、模板对齐。

**Q4:** JPEG 压缩后 NC 降低怎么办？→ 改在低频子带嵌入，或采用冗余嵌入 + 编码。

---

## 10. 附录：公式合集

**DWT:**  $f \to \{c_{LL}, c_{LH}, c_{HL}, c_{HH}\}$

**嵌入：**  $C' = C + \alpha W$

**提取：**  $\hat{W} = (C' - C) / \alpha$

**MSE：**  $\frac{1}{MN} \sum (I-I')^2$

**PSNR：**  $10\log_{10}(\text{MAX}^2/\text{MSE})$

**NC：**  $\frac{\sum W\hat{W}}{\sqrt{\sum W^2\sum \hat{W}^2}}%

**BER：**  错误比特占比。

**SSIM：** 感知结构相似性。

---

### 后续工作建议

- 多层小波嵌入（LL2 / HL2 混合）。
- 扰动调制：按局部纹理自适应调节 $\alpha$。
- 用户唯一 ID 串 → 哈希 → 水印矩阵，实现泄露追踪。
- 与加密结合：仅授权方可解出水印密钥。

---
