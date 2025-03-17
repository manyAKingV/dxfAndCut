import cv2
import numpy as np
import os
from PIL import Image
from tqdm import tqdm  # 新增进度条功能


def batch_process_images_optimized(input_dir="create_png",
                                   output_dir="create_png",
                                   blur_size=(5, 5),
                                   low_threshold_ratio=0.5,
                                   high_threshold_ratio=1.5):
    """
    批量处理目录中的PNG图片，优化版边缘检测与透明化处理
    :param input_dir: 输入目录路径
    :param output_dir: 输出目录路径
    :param blur_size: 高斯模糊核大小（奇数元组）
    :param threshold_ratio: 高低阈值比例
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 获取所有PNG文件并添加进度条
    png_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png')]
    for filename in tqdm(png_files, desc="Processing Images"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # 读取图像并保留DPI
        with Image.open(input_path) as pil_img:
            original_dpi = pil_img.info.get('dpi', (72, 72))
            img_np = np.array(pil_img.convert('RGBA'))

        # 改进版边缘检测流程（网页1][3]
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)
        blurred = cv2.GaussianBlur(gray, blur_size, 0)

        # 动态阈值计算（网页1][3]
        v = np.median(blurred)
        low_threshold = int(max(0, (1.0 - low_threshold_ratio) * v))
        high_threshold = int(min(255, (1.0 + high_threshold_ratio) * v))

        # 边缘检测优化（网页1]
        edges = cv2.Canny(blurred, low_threshold, high_threshold)

        # 形态学优化（网页3]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        dilated = cv2.dilate(closed, kernel, iterations=1)

        # 改进轮廓检测（网页1][3]
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

        # 应用蒙版并保存
        result_pil = Image.fromarray(img_np).convert("RGBA")
        alpha = Image.fromarray(mask).convert("L")
        result_pil.putalpha(alpha)
        result_pil.save(output_path, dpi=original_dpi, optimize=True)


if __name__ == "__main__":
    batch_process_images_optimized()