import pandas as pd
import matplotlib.pyplot as plt
from attacks import *
from embed import embed_watermark
from extract import extract_watermark
from metrics import psnr, nc, ber, ssim

def eval_robustness(host_img, wm_img, attacks_cfg, alpha=0.05):
    wm_embed = embed_watermark(host_img, wm_img, alpha=alpha)
    records = []
    for atk_name, atk_fn, atk_kwargs in attacks_cfg:
        atk_img = atk_fn(wm_embed, **atk_kwargs)
        wm_ext = extract_watermark(host_img, atk_img, alpha=alpha)
        wm_ext_r = cv2.resize(wm_ext, (wm_img.shape[1], wm_img.shape[0]))
        row = {
            'attack': atk_name,
            'psnr': psnr(host_img, atk_img),
            'nc': nc(wm_img, wm_ext_r),
            'ber': ber(wm_img, wm_ext_r),
            'ssim': ssim(host_img, atk_img)
        }
        records.append(row)
    df = pd.DataFrame(records)
    df.to_csv('results/metrics.csv', index=False)
    return df

def plot_nc(df):
    plt.figure()
    plt.bar(df['attack'], df['nc'])
    plt.xticks(rotation=30)
    plt.ylabel('NC')
    plt.title('NC vs Attack')
    plt.tight_layout()
    plt.savefig('results/plots/nc_plot.png')
    plt.show()
