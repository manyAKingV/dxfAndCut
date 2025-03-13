import os
import numpy as np
from PIL import Image
import time

# 允许处理大尺寸图片
Image.MAX_IMAGE_PIXELS = None

# 计算幅宽对应的像素分辨率
DPI = 200
FABRIC_WIDTH = 140
RESOLUTION = int(DPI * FABRIC_WIDTH / 2.54)


def crop_cutpart(img_array):
    """
    裁剪图片数组，去除空白边缘
    :param img_array: 输入的图片数组
    :return: 裁剪后的数组、宽度和高度
    """
    if len(img_array.shape) == 3 and img_array.shape[2] in [3, 4]:
        # 找到非白色像素的位置
        non_white = np.argwhere(np.any(img_array[:, :, :3] != 255, axis=2))
    else:
        non_white = np.argwhere(img_array != 255)

    if non_white.size == 0:
        return img_array, 0, 0

    min_y, min_x = non_white.min(axis=0)
    max_y, max_x = non_white.max(axis=0)

    if len(img_array.shape) == 3 and img_array.shape[2] in [3, 4]:
        cropped_array = img_array[min_y:max_y + 1, min_x:max_x + 1, :]
    else:
        cropped_array = img_array[min_y:max_y + 1, min_x:max_x + 1]

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

    result_array = np.zeros((RESOLUTION, 0, 4), dtype=np.uint8)
    current_x = 0
    current_y = 0

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
                    img_array, width, height = crop_cutpart(img_array)
                    print(f"{filename} _width {width} _height {height}")
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

            except Exception as e:
                print(f"处理文件 {filename} 时出现错误: {e}")

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
    image_folder = 'create_png'  # 替换为实际的图片文件夹路径
    output_path = 'output.png'  # 替换为实际的输出图片路径
    start_time = time.time()
    stitch_images(image_folder, output_path)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"计算执行耗时：{elapsed_time} 秒")
