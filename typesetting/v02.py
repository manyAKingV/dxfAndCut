import os
import numpy as np
from PIL import Image
import time

"""
    在v1的基础上，通过从大到小对裁片的原高度进行排列，实现排版的优化
"""

# 允许处理大尺寸图片
Image.MAX_IMAGE_PIXELS = None

# 计算幅宽对应的像素分辨率
DPI = 200
FABRIC_WIDTH = 140
RESOLUTION = int(DPI * FABRIC_WIDTH / 2.54)


def crop_and_return_numpy(img_array, crop_box=None):
    """
    裁剪图像数组并返回Numpy数组
    :param img_array: 输入的Numpy数组（支持H×W×C格式）
    :param crop_box: 裁剪区域元组（left, upper, right, lower），若为None则自动检测非透明区域
    :return: 裁剪后的Numpy数组、裁剪宽度和高度
    """
    # 自动检测非透明区域（针对RGBA图像）
    if crop_box is None:
        if len(img_array.shape) == 3 and img_array.shape[2] == 4:
            alpha = img_array[:, :, 3]
            non_zero = np.argwhere(alpha > 0)
            if non_zero.size == 0:
                return np.array([]), 0, 0
            min_y, min_x = non_zero.min(axis=0)
            max_y, max_x = non_zero.max(axis=0)
            crop_box = (min_x, min_y, max_x + 1, max_y + 1)
        else:
            # 非透明图像直接返回原尺寸
            return img_array, img_array.shape[1], img_array.shape[0]

    # 转换为PIL图像进行精确裁剪[6,7](@ref)
    pil_image = Image.fromarray(img_array)
    cropped_image = pil_image.crop(crop_box)

    # 返回Numpy数组及尺寸[7,8](@ref)
    cropped_array = np.array(cropped_image)
    height, width = cropped_array.shape[:2]
    return cropped_array, width, height


def stitch_images(image_folder, output_path):
    """
    拼接指定文件夹中的所有 PNG 图片
    :param image_folder: 图片所在文件夹路径
    :param output_path: 拼接后图片的保存路径
    """
    # 检查文件夹是否存在
    if not os.path.exists(image_folder):
        print(f"文件夹 {image_folder} 不存在。")
        return

    # 存储处理后的图片数组及其宽度
    processed_images = []

    # 遍历文件夹中的所有 PNG 图片
    for filename in os.listdir(image_folder):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(image_folder, filename)
            try:
                # 打开图片并转换为 NumPy 数组
                with Image.open(file_path) as img:
                    width, height = img.size
                    new_width = int(width * 2.8)
                    new_height = int(height * 2.8)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                    img = img.rotate(90, expand=True)
                    img_array = np.array(img)
                    # 处理裁片
                    img_array, width, height = crop_and_return_numpy(img_array)
                    print(f"{filename} _width {width} _height {height}")
                    processed_images.append((img_array, width, height, filename))
            except Exception as e:
                print(f"处理文件 {filename} 时出现错误: {e}")

    # 按宽度从大到小排序
    processed_images.sort(key=lambda x: x[1], reverse=True)

    result_array = np.zeros((RESOLUTION, 0, 4), dtype=np.uint8)
    current_x = 0
    current_y = 0

    # 依次拼接排序后的图片
    for img_array, width, height, filename in processed_images:
        # 检查是否需要换行
        if current_y + height > RESOLUTION:
            current_x = result_array.shape[1]
            current_y = 0

        # 检查是否需要扩展结果数组的宽度
        if current_x + width > result_array.shape[1]:
            new_width = current_x + width
            new_result_array = np.zeros((RESOLUTION, new_width, 4), dtype=np.uint8)
            new_result_array[:, :result_array.shape[1], :] = result_array
            result_array = new_result_array

        # 拼接当前图片到 result_array
        result_array[current_y:current_y + height, current_x:current_x + width, :] = img_array
        current_y += height
        print(f"计算完成一个,{filename}")

    # 若有图片被处理，将无颜色部分设置为白色并保存拼接后的图片
    if result_array.shape[1] > 0:
        # 将无颜色部分（像素值为 0）设置为白色
        result_array[np.all(result_array[:, :, :3] == 0, axis=2)] = [255, 255, 255, 255]

        result_image = Image.fromarray(result_array)
        # 按指定 DPI 保存图片
        result_image.save(output_path, dpi=(DPI, DPI))
        print(f"拼接后的图片已按 {DPI} DPI 保存到 {output_path}")
    else:
        print("未找到有效的 PNG 图片进行拼接。")


if __name__ == "__main__":
    image_folder = 'gender_png'  # 替换为实际的图片文件夹路径
    output_path = 'output.png'  # 替换为实际的输出图片路径
    start_time = time.time()
    stitch_images(image_folder, output_path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"计算执行耗时：{elapsed_time} 秒")
