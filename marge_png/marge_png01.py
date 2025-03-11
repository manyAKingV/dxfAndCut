from PIL import Image
import numpy as np


def overlay_images(img1_path, img2_path, output_path):
    try:
        # 打开两张图片
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)

        # 调整图二的大小以匹配图一
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

        # 将图片转换为 NumPy 数组
        img1_array = np.array(img1)
        img2_array = np.array(img2)

        # 确保 img2_array 的通道数与 img1_array 一致
        if img1_array.shape[2] == 3 and img2_array.shape[2] == 4:
            img2_array = img2_array[:, :, :3]
        elif img1_array.shape[2] == 4 and img2_array.shape[2] == 3:
            alpha = np.full((img2_array.shape[0], img2_array.shape[1], 1), 255, dtype=np.uint8)
            img2_array = np.concatenate((img2_array, alpha), axis=2)

        # 创建一个新的数组来存储结果
        result_array = np.copy(img1_array)

        # 找到图一像素值为透明或全黑的位置
        transparent_or_black = np.all(img1_array[:, :, :3] == [0, 0, 0], axis=-1)

        # 在这些位置使用图二的像素值
        result_array[transparent_or_black] = img2_array[transparent_or_black]

        # 将结果数组转换回图片
        result_img = Image.fromarray(result_array)

        # 保存结果图片
        result_img.save(output_path)
        print(f"图片已保存到 {output_path}")
    except FileNotFoundError:
        print("错误: 未找到指定的图片文件!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")


if __name__ == "__main__":
    img1_path = "image01.png"
    img2_path = "image02.png"
    output_path = "output.png"
    overlay_images(img1_path, img2_path, output_path)