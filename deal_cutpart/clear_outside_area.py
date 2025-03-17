import cv2
import numpy as np
from PIL import Image, ImageChops


def process_image_with_dpi(input_path, output_path):
    # 使用Pillow读取原始图像及DPI信息
    with Image.open(input_path) as pil_img:
        original_dpi = pil_img.info.get('dpi', (72, 72))  # 获取DPI，默认72
        img_np = np.array(pil_img.convert('RGBA'))  # 转换为带透明通道的numpy数组

    # OpenCV处理流程
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 优化自适应阈值
    thresh = cv2.adaptiveThreshold(blurred, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # 形态学处理（闭合小孔洞）
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 查找并填充轮廓
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

    # 转换为Pillow格式处理透明度
    result_pil = Image.fromarray(img_np).convert("RGBA")
    alpha = Image.fromarray(mask).convert("L")

    # 应用透明蒙版
    result_pil.putalpha(alpha)

    # 保存时携带DPI信息
    result_pil.save(output_path, dpi=original_dpi, optimize=True)


# 使用示例
process_image_with_dpi("zuoqianpian.png", "output.png")