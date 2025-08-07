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
