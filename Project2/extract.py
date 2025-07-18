import pywt, cv2, numpy as np

def extract_watermark(original, watermarked, wave='haar', level=1, band='LL', alpha=0.05):
    orig = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY).astype(np.float32)
    wmimg = cv2.cvtColor(watermarked, cv2.COLOR_BGR2GRAY).astype(np.float32)
    coeffs_o = pywt.wavedec2(orig, wave, level=level)
    coeffs_w = pywt.wavedec2(wmimg, wave, level=level)
    cA_o, cA_w = coeffs_o[0], coeffs_w[0]
    sigma = cA_o.std()
    wm_est = (cA_w - cA_o) / (alpha * sigma + 1e-8)
    wm_est = np.clip(wm_est, 0, 1)
    return (wm_est * 255).astype(np.uint8)
