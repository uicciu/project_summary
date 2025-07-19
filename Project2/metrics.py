import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr_func
from skimage.metrics import structural_similarity as ssim_func

def psnr(orig, proc): return psnr_func(orig, proc)

def nc(w1, w2): return np.sum(w1*w2)/(np.sqrt(np.sum(w1**2)*np.sum(w2**2))+1e-8)

def ber(w1, w2): return np.mean((w1>128)!=(w2>128))

def ssim(img1, img2): return ssim_func(img1, img2, channel_axis=-1)
