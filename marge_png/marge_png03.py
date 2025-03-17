from PIL import Image
import numpy as np
import os

"""
    多个裁片的贴图合并
"""

def overlay_images(img1_path, img2_path):
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
    # 转换为 NumPy 数组
    img1_array = np.array(img1)
    img2_array = np.array(img2)
    # 确保 img2_array 的通道数与 img1_array 一致
    if img1_array.shape[2] == 3 and img2_array.shape[2] == 4:
        img2_array = img2_array[:, :, :3]
    elif img1_array.shape[2] == 4 and img2_array.shape[2] == 3:
        alpha = np.full((img2_array.shape[0], img2_array.shape[1], 1), 255, dtype=np.uint8)
        img2_array = np.concatenate((img2_array, alpha), axis=2)
    result_array = np.copy(img1_array)
    # 判断是否为黑色或白色像素
    black_or_white = np.logical_or(
        np.all(img1_array[:, :, :3] == [0, 0, 0], axis=-1),
        np.all(img1_array[:, :, :3] == [255, 255, 255], axis=-1)
    )
    result_array[black_or_white] = img2_array[black_or_white]
    result_img = Image.fromarray(result_array)
    return result_img



if __name__ == "__main__":
    input_folder = "create_png"
    base_img_path = "image02.png"
    output_folder = "gender_png"

    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    try:
        # 遍历输入文件夹中的所有图片
        for filename in os.listdir(input_folder):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                img1_path = os.path.join(input_folder, filename)
                result_img = overlay_images(img1_path, base_img_path)
                # 生成输出文件名
                output_filename = os.path.splitext(filename)[0] + "_01.png"
                output_path = os.path.join(output_folder, output_filename)
                # 保存结果图片
                result_img.save(output_path)
                print(f"图片已保存到 {output_path}")

    except FileNotFoundError:
        print("错误: 未找到指定的图片文件!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")
