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
