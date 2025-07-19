import cv2, numpy as np

def attack_flip(img, code=1): return cv2.flip(img, code)

def attack_crop(img, ratio=0.1):
    h, w = img.shape[:2]
    dx, dy = int(w*ratio), int(h*ratio)
    crop = img[dy:h-dy, dx:w-dx]
    return cv2.resize(crop, (w,h))

def attack_brightness(img, beta=30): return cv2.convertScaleAbs(img, alpha=1.0, beta=beta)

def attack_contrast(img, alpha=1.5): return cv2.convertScaleAbs(img, alpha=alpha)

def attack_jpeg(img, quality=50):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, enc = cv2.imencode('.jpg', img, encode_param)
    return cv2.imdecode(enc, 1)

def attack_noise(img, sigma=10):
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    noisy = img.astype(np.float32) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)
