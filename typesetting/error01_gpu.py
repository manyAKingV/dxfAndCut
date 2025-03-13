import os
import torch  # 12.4
import numpy as np
from PIL import Image
import time

"""
    使用GPU进行计算反而降低了计算速度
"""

# 允许处理大尺寸图片
Image.MAX_IMAGE_PIXELS = None

# 计算幅宽对应的像素分辨率
DPI = 200
FABRIC_WIDTH = 140
RESOLUTION = int(DPI * FABRIC_WIDTH / 2.54)


def crop_cutpart(img_array):
    # 将 NumPy 数组转换为 PyTorch 张量并移动到 GPU 上
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    img_tensor = torch.from_numpy(img_array).to(device)
    height, width = img_tensor.shape[:2]

    # 初始化边界
    min_x = width
    min_y = height
    max_x = 0
    max_y = 0

    # 遍历像素找边界
    for y in range(height):
        for x in range(width):
            if img_tensor.dim() == 3 and img_tensor.shape[2] in [3, 4]:
                if not torch.all(img_tensor[y, x, :3] == 255):
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
            elif img_tensor.dim() == 2:
                if img_tensor[y, x] != 255:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)

    # 根据边界裁剪数组
    if img_tensor.dim() == 3 and img_tensor.shape[2] in [3, 4]:
        cropped_tensor = img_tensor[min_y:max_y + 1, min_x:max_x + 1, :]
    else:
        cropped_tensor = img_tensor[min_y:max_y + 1, min_x:max_x + 1]

    # 将裁剪后的张量转换回 NumPy 数组
    cropped_array = cropped_tensor.cpu().numpy()
    cropped_height, cropped_width = cropped_array.shape[:2]
    return cropped_array, cropped_width, cropped_height



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

    result_array = None
    current_width = 0
    max_height = 0

    # 遍历文件夹中的所有 PNG 图片
    for filename in os.listdir(image_folder):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(image_folder, filename)
            try:
                # 打开图片并转换为 NumPy 数组
                with Image.open(file_path) as img:
                    img_array = np.array(img)
                    # 处理裁片
                    img_array,width,height = crop_cutpart(img_array)
                    max_height = max(max_height, height)

                    # 若 result_array 未初始化，根据当前图片初始化
                    if result_array is None:
                        result_array = np.zeros((height, width, 4), dtype=np.uint8)
                    # 若当前图片会超出 result_array 宽度，扩展 result_array
                    elif current_width + width > result_array.shape[1]:
                        new_width = current_width + width
                        new_result_array = np.zeros((max_height, new_width, 4), dtype=np.uint8)
                        new_result_array[:result_array.shape[0], :result_array.shape[1], :] = result_array
                        result_array = new_result_array

                    # 拼接当前图片到 result_array
                    result_array[:height, current_width:current_width + width, :] = img_array
                    current_width += width
                    print(f"计算完成一个,{filename}")

            except Exception as e:
                print(f"处理文件 {filename} 时出现错误: {e}")

    # 若有图片被处理，将无颜色部分设置为白色并保存拼接后的图片
    if result_array is not None:
        # 将无颜色部分（像素值为 0）设置为白色
        result_array[np.all(result_array[:, :, :3] == 0, axis=2)] = [255, 255, 255, 255]

        result_image = Image.fromarray(result_array)
        # 按指定 DPI 保存图片
        result_image.save(output_path, dpi=(DPI, DPI))
        print(f"拼接后的图片已按 {DPI} DPI 保存到 {output_path}")
    else:
        print("未找到有效的 PNG 图片进行拼接。")


if __name__ == "__main__":
    image_folder = 'create_png'  # 替换为实际的图片文件夹路径
    output_path = 'output.png'  # 替换为实际的输出图片路径
    start_time = time.time()
    stitch_images(image_folder, output_path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"计算执行耗时：{elapsed_time} 秒")
