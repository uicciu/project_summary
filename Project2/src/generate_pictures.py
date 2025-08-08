import cv2
import numpy as np
import os

os.makedirs("test_data", exist_ok=True)

# 生成原图（256×256，渐变 + 随机圆）
h, w = 256, 256
image = np.zeros((h, w, 3), dtype=np.uint8)
for y in range(h):
    color = int(255 * y / h)
    image[y, :, :] = (color, color // 2, 255 - color)

# 加一些随机圆形噪声，增加纹理
for _ in range(30):
    center = (np.random.randint(0, w), np.random.randint(0, h))
    radius = np.random.randint(5, 30)
    color = tuple(np.random.randint(0, 255, 3).tolist())
    cv2.circle(image, center, radius, color, -1)

cv2.imwrite("test_data/lena_fake.png", image)

# 生成水印logo
wm_size = (128, 128)
watermark = np.ones(wm_size, dtype=np.uint8) * 255  # 白底
cv2.putText(watermark, "WATERMARK", (5, 70), cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (0,), 2, cv2.LINE_AA)
cv2.imwrite("test_data/watermark.png", watermark)

print("原图：test_data/lena_fake.png")
print("水印：test_data/watermark.png")
