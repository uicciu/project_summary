import pywt, cv2, numpy as np

def embed_watermark(image, watermark, wave='haar', level=1, band='LL', alpha=0.05):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
    coeffs = pywt.wavedec2(img, wave, level=level)
    cA, details = coeffs[0], coeffs[1:]
    wm = cv2.resize(watermark, (cA.shape[1], cA.shape[0]), interpolation=cv2.INTER_AREA).astype(np.float32)
    wm_norm = (wm - wm.min()) / (wm.max() - wm.min() + 1e-8)
    cA_wm = cA + alpha * wm_norm * cA.std()
    new_coeffs = [cA_wm] + list(details)
    watermarked = pywt.waverec2(new_coeffs, wave)
    return np.clip(watermarked, 0, 255).astype(np.uint8)
